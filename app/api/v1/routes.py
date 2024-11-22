# milesight camera
import base64
import io
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from PIL import Image, ImageDraw, ImageFont

api = Blueprint('v1', __name__)

load_dotenv()


@api.route('/test', methods=['POST'])
def test():
    return jsonify({"message": "This is a test endpoint for v1, MILESIGHT CAMERA."}), 200
 

@api.route('/parking-session/operatorId/<int:operatorId>/floorId/<int:floorId>', methods=['POST'])
def parking_event(operatorId, floorId):
    try:
        raw_data = request.json
        # target_url =  "http://localhost:3000/parking-session/test"
        base_url = os.getenv("TARGET_URL","http://localhost:3000/parking-session/operatorId/1/floorId/1")
        print("operator id:",operatorId)
        print("floor id:",floorId)
        print("raw data", raw_data)
        target_url = f"{base_url}/parking-session/operatorId/{operatorId}/floorId/{floorId}"
    
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

       
        processed_image = snapshot_processing( coordinates, snapshot_base64)
        base64_processed_image = save_and_apply_overlay(time, license_plate, device_name, processed_image)

        
        # print(base64_processed_image)

        raw_data['snapshot'] = base64_processed_image # change the value from original base 64 to processed one.

        response = requests.post(target_url,json=raw_data)
        print(response.content)
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
