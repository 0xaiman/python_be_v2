# tgw camera
import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

api = Blueprint('v2', __name__)

load_dotenv()

@api.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "This is a test endpoint for v2, NEW CAMERA."}), 200

@api.route('/raw-payload', methods=['POST'])
def handle_raw_payload():
    raw_data = request.json
    print(raw_data)

    return
