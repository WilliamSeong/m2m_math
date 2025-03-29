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
        
        final, final_binary = sheet(image_uri)
        # visualize_extraction_regions(final_binary)
        answers = extract_answers(final_binary)
        print("answers: ", answers)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})

# def visualize_extraction_regions(binary_image):
#     # Make a copy of the image and convert to BGR so we can draw colored lines
#     vis_img = cv.cvtColor(binary_image, cv.COLOR_GRAY2BGR)
    
#     # Define the region we want to extract answers from
#     y_start, y_end = 250, 1450
#     x_start, x_end = 120, 340
    
#     # Draw a red rectangle around the answer region
#     cv.rectangle(vis_img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    
#     # Calculate row height (for 50 questions)
#     num_questions = 50
#     row_height = (y_end - y_start) // num_questions
    
#     # Draw horizontal lines for each row
#     for i in range(1, num_questions):
#         y = y_start + i * row_height
#         cv.line(vis_img, (x_start, y), (x_end, y), (0, 0, 255), 1)
    
#     # Draw vertical lines to separate A, B, C, D, E columns
#     option_width = (x_end - x_start) // 5
#     for i in range(1, 5):
#         x = x_start + i * option_width
#         cv.line(vis_img, (x, y_start), (x, y_end), (0, 0, 255), 1)
    
#     cv.imwrite("answer_extraction.jpg", vis_img * 255)

def extract_answers(final):
    print("Extracting answers!")
    # Load the pre-processed image
    img = final
    
    # Define the region of answers (you might need to adjust these coordinates)
    # This focuses on the answer bubbles region
    answer_region = img[250:1450, 120:340]
    
    # Get number of rows (questions)
    num_questions = 50  # Based on your form
    
    # Height of each row
    row_height = answer_region.shape[0] // num_questions
    
    # Width of the answer region divided by 5 (A, B, C, D, E)
    option_width = answer_region.shape[1] // 5
    
    answers = {}
    options = ['A', 'B', 'C', 'D', 'E']
    
    for q in range(1, num_questions + 1):
        if (q < 18):
            print("Question ", q)
        # Calculate the row position for this question
        row_start = (q - 1) * row_height
        row_end = row_start + row_height
        
        # Extract the row for this question
        row = answer_region[row_start:row_end, :]
        # print("question ", q, "row?: ", row)
        
        # For each option (A, B, C, D, E)
        answer_averages = []
        
        for i in range(5):
            # Calculate the column position for this option
            col_start = i * option_width
            col_end = col_start + option_width
            
            # Extract the bubble region
            bubble = row[:, col_start:col_end]
            
            # Calculate the average pixel value (darker means filled)
            avg_pixel = np.mean(bubble)
            # if (q == 1 or q == 9 or q == 10):
            #     print("Average of choice ", options[i], " is: ", avg_pixel)
            answer_averages += [avg_pixel]
            
        # if (q < 18):
        #     # print("Answer_average: ", answer_averages)
        #     # print("Standard deviation: ", np.std(answer_averages))
        #     # print("differences: ", np.abs(answer_averages-np.mean(answer_averages)))
        #     print("significance?: ", np.where(np.abs(answer_averages - np.mean(answer_averages)) > np.std(answer_averages), 1, 0))
        
        significance = np.where(np.abs(answer_averages - np.mean(answer_averages)) > np.std(answer_averages), 1, 0)

        if np.mean(significance) == .2:
            for i in range(5):
                if significance[i] == 1:
                    answers[q] = options[i]
        else:
            answers[q] = options[4]
    
    return answers

# Answer sheet isolating
def sheet(uri):
    if uri.startswith('data:image'):
        # Extract the base64 data
        base64_data = re.sub('^data:image/.+;base64,', '', uri)
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
        # print(f"image shape after decode and grayscale and binary: {binary.shape}")
        # print(f"binary threshold is: {ret}")
        # print(binary)

        # Apply morphologyEx to blank out the actual answer sheet (Not Good)
        # kernel = np.ones((20,20), np.uint8)
        # blank = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel, iterations=1)

        # Contour Blanking (Better)
        contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        page_contour = max(contours, key=cv.contourArea)
        blank = np.zeros_like(binary)
        cv.drawContours(blank, [page_contour], 0, 1, -1)
        # outline = np.zeros_like(binary)
        # cv.drawContours(outline, [page_contour], 0, 1, 3)
        outline = np.zeros((binary.shape[0], binary.shape[1], 3), dtype=np.uint8)
        cv.drawContours(outline, [page_contour], 0, (0, 255, 255), 3)
        # print("page_contour: ", page_contour)

        # Get corners
        con = np.zeros((binary.shape[0], binary.shape[1], 3), dtype=np.uint8)

        # print("contour coordinate: ", c)
        epsilon = 0.02 * cv.arcLength(page_contour, True)
        corners = cv.approxPolyDP(page_contour, epsilon, True)
        # print("corners: ", corners)
        
        # print("corners: ", corners)
        cv.drawContours(con, [page_contour], -1, (0, 255, 255), 3)
        cv.drawContours(con, corners, -1, (255, 0, 255), 10)

        corners = sorted(np.concatenate(corners).tolist())

        for index, c in enumerate(corners):
            # print("corners: ", c)
            character = chr(65 + index)
            cv.putText(con, character, c, cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv.LINE_AA)
        
        # Order corners, top-left, top-right, bottom-right, bottom-left
        ordered_corners = order_points(corners)
        # print("ordered corners: ", ordered_corners)

        # Get destination coordinates
        # (tl, tr, br, bl) = ordered_corners
        # widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        # widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        # maxWidth = max(int(widthA), int(widthB))

        # heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        # heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        # maxHeight = max(int(heightA), int(heightB))

        maxWidth = 600
        maxHeight = 1600
        minHeight = 1546

        destination_corners = [[0,0], [maxWidth, 0], [maxWidth, maxHeight], [0,minHeight]]

        # print("Destination corners: ", destination_corners)

        M = cv.getPerspectiveTransform(np.float32(ordered_corners), np.float32(destination_corners))
        final = cv.warpPerspective(img, M, (destination_corners[2][0], destination_corners[2][1]), flags=cv.INTER_LINEAR)
        final_binary = cv.warpPerspective(binary, M, (destination_corners[2][0], destination_corners[2][1]), flags=cv.INTER_LINEAR)

        cv.imwrite("original_image_color.jpg", img)
        cv.imwrite("processed_image_gray.jpg", gray)
        cv.imwrite("processed_image_binary.jpg", binary * 255)
        cv.imwrite("blanked__image_binary.jpg", blank * 255)
        cv.imwrite("contour_image.jpg", outline)
        cv.imwrite("corner_image.jpg", con)
        cv.imwrite("final_image.jpg", final)
        cv.imwrite("final_binary_image.jpg", final_binary * 255)

        with open('image_final_binary.txt', 'w') as f:
            # For each row in the image
            for row in final_binary:
                # Format each pixel value to take up 3 spaces (right-aligned)
                row_str = ' '.join(f"{pixel:3d}" for pixel in row)
                # Write the row and add a newline
                f.write(row_str + '\n')
                f.write('\n')

        return final, final_binary
    else:
        return jsonify({'error': 'Unsupported URI format'})

def order_points(pts):
    "Rearrange coordinate: top-left, top-right, bottom-right, bottom-left"
    rect = np.zeros((4,2), dtype='float32')
    pts = np.array(pts)
    s = pts.sum(axis=1)

    # top-left have lowest sum
    rect[0] = pts[np.argmin(s)]

    # bottom-right have largest sum
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    # top-right have the smallest difference
    rect[1] = pts[np.argmin(diff)]

    # bottom-left have the largest difference
    rect[3] = pts[np.argmax(diff)]

    return rect.astype('int').tolist()


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
