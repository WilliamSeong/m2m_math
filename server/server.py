from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from dotenv import load_dotenv

import cv2 as cv
import numpy as np
import re
import base64

import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


app = Flask(__name__)
CORS(app)
load_dotenv()

db_user = os.getenv("MONGODB_USER")
db_password = os.getenv("MONGODB_PASSWORD")

uri = f"mongodb+srv://{db_user}:{db_password}@young-by-nail.vhysf.mongodb.net/?retryWrites=true&w=majority&appName=young-by-nail"
print(uri)
client = MongoClient(uri, server_api=ServerApi('1'))

@app.route("/test")
def test():
    print("Test request received")
    return jsonify({"message" : "Test received"})

@app.route("/db")
def db():
    print("Fetching questions")

    try:
        result = questions(client)
        print(result["template"])
        return jsonify({"template" : result["template"]})
    except:
        print("Algebra fetch error")
        return jsonify({"error": "Database error"}), 500

def questions(client):
    try:
        result = client["m2m_math_db"]["questions"].find_one()
        if (result):
            return result
        else:
            print("No questions")
            return None
    except Exception as e:
        print("DB fetch error for questions: ", e)
        return None

@app.route("/camera", methods=['POST'])
def cameraResponse():
    data = request.get_json()
    image_uri = data.get("uri")

    try:
        result = pushImage(client, image_uri)
        print(result)
        return jsonify({"message" : "success"})
    except:
        print("Algebra fetch error")
        return jsonify({"error": "Database error"}), 500


def pushImage(client, uri):
    try:
        result = client["m2m_math_db"]["submissions"].insert_one({"uri" : uri})
        return result
    except Exception as e:
        print("Image insert error for questions: ", e)
        return None
    
file_path = "testImage.png"
print(f"File exists: {os.path.exists(file_path)}")

@app.route("/process", methods=['POST'])
def process():
    print("Processing image")
    try:
        data = request.get_json()
        image_uri = data.get("uri")

        if not image_uri:
            return jsonify({'error': 'No image URI provided'})

        if image_uri.startswith('data:image'):
            # Extract the base64 data
            base64_data = re.sub('^data:image/.+;base64,', '', image_uri)
            # Decode base64 to bytes
            img_bytes = base64.b64decode(base64_data)
            # Convert to numpy array
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            # print(f"image shape before decode: {img_array.shape}")
            # print(img_array)

            # Decode the image
            img = cv.imdecode(img_array, cv.IMREAD_COLOR)
            # print(f"image shape after decode: {img.shape}")
            # print(img)

            if img is None:
                return jsonify({'error': 'Failed to decode image'})
                
            # Grayscale image
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # print(f"image shape after decode and grayscale: {gray.shape}")
            # print(gray)

            # Apply binary thresholding
            ret, binary = cv.threshold(gray, 190, 1, cv.THRESH_BINARY)
            print(f"image shape after decode and grayscale and binary: {binary.shape}")
            print(f"binary threshold is: {ret}")
            print(binary)

            cv.imwrite("processed_image_gray.jpg", gray)
            cv.imwrite("processed_image_binary.jpg", binary * 255)

            with open('image_aligned.txt', 'w') as f:
                # For each row in the image
                for row in binary:
                    # Format each pixel value to take up 3 spaces (right-aligned)
                    row_str = ' '.join(f"{pixel:3d}" for pixel in row)
                    # Write the row and add a newline
                    f.write(row_str + '\n')
                    f.write('\n')

            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Unsupported URI format'})
    except Exception as e:
        return jsonify({'error': str(e)})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050)

# Activate environment with flask
# source venv/bin/activate

# Run flask server
# python3 -m flask --app server run --host=0.0.0.0 --port=9050
# or 
# python3 server.py

# http request endpoint
# http://192.168.1.103:9050
