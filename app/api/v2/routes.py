# tgw camera
import base64
import json
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, request
from PIL import Image, ImageDraw, ImageFont

from app.models.v2.models import (Device, ParkingBay, ParkingFloor,
                                  ParkingOperator, ParkingSession, Vehicle)

api = Blueprint('v2', __name__)

load_dotenv()

def create_v2_routes(limiter):

    @api.route('/test', methods=['GET'])
    @limiter.limit("5 per minute")
    def test():
        return jsonify({"message": "This is a test endpoint for v2, TGW CAMERA."}), 200

    @api.route('/raw-payload', methods=['POST'])
    @limiter.limit("5 per minute")
    def handle_raw_payload():
        raw_data = request.json
        print(raw_data)

        return raw_data

    @api.route('/parking-session/operatorId/<int:operatorId>/floorId/<int:floorId>/LprResult', methods=['POST'])
    @limiter.limit("50 per minute")
    def parking_event(operatorId, floorId):
        payload = request.json
        payload['picSmall'] = None

        # validate if parking-operator and parkingfloor exist in DB
        if not validate_operator_and_floor(operatorId, floorId):
            return jsonify({
                "status": "error",
                "message": f"Parking operator with ID {operatorId} or floor with ID {floorId} does not exist."
            }), 400

        try:
            # Extract details from payload
            park_space_info = payload.get('parkSpaceInfo', [])[0] # [1],[2] //edge case: handle 3 car park at once
            cam_name = payload.get('camName', 'unknown')
            current_date = datetime.now().strftime('%Y-%m-%d')
            park_space_info['picSmall'] = None
            print(park_space_info)

            if park_space_info:
                recog_time = park_space_info.get('recogTime', '').replace(':', '-').replace(' ', '_')
                plate_num = park_space_info.get('plateNum', 'unknown')
                bay_id = park_space_info.get('spaceNo', 'unknown')
                bay_name = park_space_info.get('spaceName', 'unknown')
                pic_small = park_space_info.get('picSmall', '')

                print("recog_time",recog_time)
                print("plate_num",plate_num)
                print("bay_id",bay_id)
                print("bay_name",bay_name)
                # print("pic_small",pic_small)
                # store this in redis, then points to nestjs

                if park_space_info.get('spaceState') == 1:  # SpaceState 1 indicates entering
                    base_name = f"{recog_time}_{plate_num}_{bay_id}_{bay_name}"
                    json_file_name = f"{base_name}_.json"
                    picture_file_name = f"{base_name}.jpg"
                    overlay_text = f"{plate_num} - {recog_time}"  # Text to overlay on the image
                else:
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    json_file_name = f"non_entry_event_{timestamp}.json"
                    picture_file_name = None

            else:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                json_file_name = f"invalid_payload_{timestamp}.json"
                picture_file_name = None

            # Directory structure
            # base_directory = r'C:\Users\maima\Desktop\bigtac\flask_iot_server_forwarding_only\json_file' #
            base_directory = Path(__file__).resolve().parent / 'json_file'  # Dynamic base directory
            date_directory = base_directory / current_date
            cam_directory = date_directory / cam_name

            cam_directory.mkdir(parents=True, exist_ok=True)

            # Save JSON file
            json_file_path = cam_directory / json_file_name
            # json_file_path = os.path.join(cam_directory, json_file_name)
            with open(json_file_path, 'w') as json_file:
                json.dump(payload, json_file, indent=4)
            print(f"Payload saved to {json_file_path}")

            # Save picture if applicable
            # Save picture if applicable
            if picture_file_name and pic_small:
                picture_file_path = os.path.join(cam_directory, picture_file_name)
                try:
                    # Fix and decode the modified Base64 string
                    print(f"Saving image to {picture_file_path}")
                    pic_small_fixed = fix_base64(pic_small)
                    image_data = base64.b64decode(pic_small_fixed)

                    # Add text overlay to the image
                    updated_image_data = add_text_to_image(image_data, overlay_text)

                    # Save the updated image
                    with open(picture_file_path, 'wb') as picture_file:
                        picture_file.write(updated_image_data)
                    print(f"Picture saved to {picture_file_path}")
                except Exception as e:
                    print(f"Error saving picture: {e}")

    
        except Exception as e:
            print(f"Error processing payload: {e}")
            return jsonify({
                "status": "error",
                "message": "Failed to process the payload.",
                "error": str(e)
            }), 500

        return jsonify({
            "status": "success",
            "message": "Payload received and processed.",
            "received_data": payload
        })
    

    
    return api

# helpers
def fix_base64(data):
    """
    Fix the modified Base64 string by reversing substitutions and padding.
    """
    data = data.replace('-', '+').replace('_', '/').replace('.', '=')
    # Check if padding is correct (multiple of 4 chars)
    return data + '=' * (-len(data) % 4)  # Ensure proper padding


def add_text_to_image(image_data, text, font_size=20):
    """
    Add text with a black background to an image using Pillow.
    Args:
        image_data: Byte data of the image.
        text: The text to overlay on the image.
        font_size: Size of the font for the text.

    Returns:
        The image with the text and background added, as byte data.
    """
    try:
        # Open the image from the byte data
        image = Image.open(BytesIO(image_data))
        draw = ImageDraw.Draw(image)

        # Define font (default system font if no custom font is available)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)  # Adjust font path if necessary
        except IOError:
            font = ImageFont.load_default()

        # Get image dimensions
        img_width, img_height = image.size

        # Calculate text size and position
        margin = 10
        text_width, text_height = draw.textsize(text, font=font)
        text_position = (margin, img_height - text_height - margin)

        # Define rectangle coordinates for background
        rect_x0 = text_position[0] - margin
        rect_y0 = text_position[1] - margin
        rect_x1 = text_position[0] + text_width + margin
        rect_y1 = text_position[1] + text_height + margin

        # Draw black rectangle as background
        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill="black")

        # Overlay the text in white
        draw.text(text_position, text, font=font, fill="white")

        # Save the modified image to byte data
        output = BytesIO()
        image.save(output, format="JPEG")
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        print(f"Error adding text to image: {e}")
        return image_data  # Return original image if text overlay fails


def validate_operator_and_floor(operator_id, floor_id):
    """
    Validates if the parking operator with operator_id has a floor with floor_id.

    :param operator_id: ID of the parking operator
    :param floor_id: ID of the parking floor
    :return: True if the floor exists for the operator, False otherwise
    """
    try:
        # Query the database to check the existence of the floor within the operator
        operator = ParkingOperator.query.filter_by(id=operator_id).first()
        print(operator)
        if not operator:
            return False  # Operator does not exist

        # Check if the floor exists for the given operator
        floor = ParkingFloor.query.filter_by(id=floor_id, operator_id=operator_id).first()
        if not floor:
            return False  # Floor does not exist for the operator

        return True  # Both operator and floor exist
    except Exception as e:
        print(f"Error during validation: {e}")
        return False


    




