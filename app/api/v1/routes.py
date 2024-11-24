# milesight camera
import base64
import io
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from PIL import Image, ImageDraw, ImageFont

from app.db import db
from app.models.parking_logs import ParkingLog

api = Blueprint('v1', __name__)

load_dotenv()


@api.route('/test', methods=['POST'])
def test():
    return jsonify({"message": "This is a test endpoint for v1, MILESIGHT CAMERA."}), 200
 

@api.route('/parking-session/operatorId/<int:operatorId>/floorId/<int:floorId>', methods=['POST'])
# /parking-session/operatorId/1/floorId/1 GROUND (100)
# /parking-session/operatorId/1/floorId/2 LEVEL 1 (100)
# ...
# /parking-session/operatorId/1/floorId/10 LEVEL10
# 
def parking_event(operatorId, floorId):
    try:
        raw_data = request.json
        bearer_token = "token"
        headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
        
        base_url = os.getenv("TARGET_URL","http://localhost:3000/parking-session/operatorId/1/floorId/1")
        print("operator id:",operatorId)
        print("floor id:",floorId)
        print("raw data", raw_data)

        # 1 -Generate target url to NESTJS
        target_url = f"{base_url}/parking-session/operatorId/{operatorId}/floorId/{floorId}"
    
        # 2- Data extraction to use in naming the snapshot files
        time = raw_data['time']
        license_plate = raw_data['License Plate']
        device_name = raw_data['device']
        coordinates = {
            'x1':raw_data['coordinate_x1'],
            'y1':raw_data['coordinate_y1'],
            'x2':raw_data['coordinate_x2'],
            'y2':raw_data['coordinate_y2']
        }
        snapshot_base64 = raw_data['snapshot']

        # 3 - helper function : Image compresion , overlay   
        processed_image = snapshot_processing( coordinates, snapshot_base64)

        # 4 - save and  convert the processed image into base64 again to send to NESTJS
        base64_processed_image = save_and_apply_overlay(time, license_plate, device_name, processed_image)

        # 5 - Update the base64 value  with the processed  image one
        raw_data['snapshot'] = base64_processed_image 

        # 6 - send POST request to NESTJS
        response = requests.post(target_url,json=raw_data, headers=headers)
        print(response.content)

        #7 - Store the data into the database
        db_response = save_parking_event_to_db(operatorId, floorId,raw_data)
        if db_response["status"] == "error":
            return jsonify({"error": db_response["message"]}), 500
        
        return response.content, response.status_code
        # return "OK"
    except requests.exceptions.Timeout:
        # Handle timeout errors
        return jsonify({"error": "Request to target server timed out"}), 504
    
    except requests.exceptions.ConnectionError:
        # Handle connection errors
        return jsonify({"error": "Failed to connect to target server"}), 502
    
    except requests.exceptions.RequestException as e:
        # Catch other request-related exceptions
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    except Exception as e:
        # Handle unexpected server-side errors
        return jsonify({"error": "Internal server error", "details": str(e)}), 500



def snapshot_processing( coordinates, snapshot_base64):
    print("snapshot processing ok")

    img = Image.open(io.BytesIO(base64.decodebytes(bytes(snapshot_base64,"utf-8"))))
    # cropped_img = img.crop((coordinates['x1'], coordinates['y1'], coordinates['x2'], coordinates['y2']))

    return img


def save_and_apply_overlay(time, license_plate, device_name, img):
     # overlay text formatting

    dt_object = datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    formatted_time = dt_object.strftime('%Y%m%d_%H%M%S')
    folder_name = dt_object.strftime('%Y%m%d')
    file_name = f"{formatted_time}_{license_plate}.jpg"

    # creating dedicated snapshot folder
    snapshot_dir = os.path.join(os.getcwd(), 'snapshot')
    os.makedirs(snapshot_dir, exist_ok=True)

    # create folder strurcture (date and device folder witihin snapshot)
    daily_folder_path = os.path.join(snapshot_dir, folder_name)
    device_folder_path = os.path.join(daily_folder_path, device_name)
    os.makedirs(device_folder_path,exist_ok=True)

    file_path = os.path.join(device_folder_path,file_name)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=15, optimize=True)
    buffer.seek(0)

    compressed_img = Image.open(buffer)

    overlay_text = f"{formatted_time}_{license_plate}"
    font_size = 15
    font = ImageFont.load_default()
    text_color = (255, 255, 255)  # White text
    background_color = (0, 0, 0)  # Black background for text
    text_position = (10, compressed_img.height - font_size - 10)

    draw = ImageDraw.Draw(compressed_img)

    text_bbox = draw.textbbox(text_position, overlay_text, font=font)
    draw.rectangle([text_position, (text_bbox[2], text_bbox[3])], fill=background_color)
    draw.text(text_position, overlay_text, font=font, fill=text_color)

    compressed_img.save(file_path,quality=100,optimize=True)

    buffer = io.BytesIO()
    compressed_img.save(buffer, format='JPEG')
    buffer.seek(0)

    base64_encoded_compressed_img = base64.b64encode(buffer.read()).decode('utf-8')

    return base64_encoded_compressed_img

def save_parking_event_to_db(operatorId, floorId,raw_data):
    """
    Save parking event data to the database.
    """
    try:
        parking_event = ParkingLog(
            event=raw_data.get('event'),
            operator_id = operatorId,
            floor_id = floorId,
            device=raw_data.get('device'),
            time=datetime.strptime(raw_data['time'], '%Y-%m-%d %H:%M:%S'),
            report_type=raw_data.get('report_type'),
            resolution_w=raw_data.get('resolution_w'),
            resolution_h=raw_data.get('resolution_h'),
            channel=raw_data.get('channel'),
            bay_name=raw_data.get('bay_name'),
            bay_id=raw_data.get('bay_id'),
            occupancy=raw_data.get('occupancy'),
            duration=raw_data.get('duration'),
            license_plate=raw_data.get('License Plate'),
            plate_color=raw_data.get('Plate Color'),
            vehicle_type=raw_data.get('Vehicle Type'),
            vehicle_color=raw_data.get('Vehicle Color'),
            vehicle_brand=raw_data.get('Vehicle Brand'),
            coordinate_x1=raw_data.get('coordinate_x1'),
            coordinate_y1=raw_data.get('coordinate_y1'),
            coordinate_x2=raw_data.get('coordinate_x2'),
            coordinate_y2=raw_data.get('coordinate_y2'),
            snapshot=raw_data.get('snapshot')
        )
        db.session.add(parking_event)
        db.session.commit()
        print("Parking event saved to database.")
        return {"status": "success", "message": "Data saved successfully."}
    except Exception as e:
        db.session.rollback()
        print(f"Error saving to database: {e}")
        return {"status": "error", "message": str(e)}
