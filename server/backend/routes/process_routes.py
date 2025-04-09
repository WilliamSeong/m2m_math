from flask import Blueprint, jsonify, request

from bson.objectid import ObjectId

from datetime import datetime

from backend.db import get_client

import cv2 as cv
import base64
import numpy as np
import re

process_bp = Blueprint("process", __name__)

@process_bp.route("", methods=['POST'])
def process():
    print("Processing image")
    try:

        client = get_client()

        data = request.get_json()
        image_uri = data.get("uri")
        packet_id = data.get("packetId")
        student_id = data.get("studentId")

        print(f"Packet Id for grading: {packet_id}")

        if not image_uri:
            return jsonify({'error': 'No image URI provided'})
        
        final, final_binary = sheet(image_uri)
        # final_png = numpy_to_uri(final)
        vis_final = visualize_extraction_regions(final_binary)
        vis_final_png = numpy_to_uri(vis_final)
        student_answers = extract_answers(final_binary)
        print(f"answers: {student_answers}")

        answer_key = getAnswerKey(client, packet_id)
        print(f"answer key: {answer_key}")

        correct, incorrect = grade(student_answers, answer_key)

        pushSubmission(client, packet_id, vis_final_png, correct, incorrect, student_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})
    
def pushSubmission(client, packet_id, vis_uri, correct, incorrect, student_id):
    try:
        packet_id_obj = ObjectId(packet_id) if isinstance(packet_id, dict) else ObjectId(packet_id)
        student_id_obj = ObjectId(student_id) if isinstance(student_id, dict) else ObjectId(student_id)
        document = {
                    "packet_id" : packet_id_obj, 
                    "images" : 
                        {
                            "processed" : vis_uri
                        },
                    "score" :
                        {
                            "correct" : correct,
                            "incorrect" : incorrect,
                        },
                    "datetime" : datetime.now()
                    }
        result = client["m2m_math_db"]["submissions"].insert_one(document)
        submission_id = result.inserted_id
        client["m2m_math_db"]["packets"].update_one({"_id": packet_id_obj}, {"$push": {"submissions": submission_id}})
        client["m2m_math_db"]["students"].update_one({"_id": student_id_obj}, {"$set": {"last_submission": datetime.now()}})
        return result
    except Exception as e:
        print("Image insert error for questions: ", e)
        return None

# Convert processed image arrays back to uri for mongo
def numpy_to_uri(image_array):
    # Encode the image as PNG/JPEG
    success, encoded_img = cv.imencode('.png', image_array)
    if not success:
        return None
    
    # Convert to base64 string
    base64_str = base64.b64encode(encoded_img).decode('utf-8')
    
    # Create the data URI
    img_uri = f"data:image/png;base64,{base64_str}"
    
    return img_uri

def grade(answers, answer_key):
    correct = []
    incorrect = []
    for key, value in answer_key.items():
        print(f"question {key}: answer key-{value} answer-{answers[key]}")
        student_answer = value
        correct_answer = answers[key]
        if (student_answer == correct_answer):
            correct += [key]
        else:
            incorrect += [key]
    
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Grade: {correct}/{correct+incorrect}")
    return correct, incorrect
    
def getAnswerKey(client, packet_id):
    packet_id_obj = ObjectId(packet_id) if isinstance(packet_id, dict) else ObjectId(packet_id)
    result = client["m2m_math_db"]["packets"].find_one({"_id" : packet_id_obj}, {"_id" : 0, "answer_key" : 1})
    return result["answer_key"]

def visualize_extraction_regions(binary_image):
    # Make a copy of the image and convert to BGR so we can draw colored lines
    vis_img = cv.cvtColor(binary_image, cv.COLOR_GRAY2BGR)
    
    # Define the region we want to extract answers from
    y_start, y_end = 250, 1450
    x_start, x_end = 120, 340
    
    # Draw a red rectangle around the answer region
    cv.rectangle(vis_img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    
    # Calculate row height (for 50 questions)
    num_questions = 50
    row_height = (y_end - y_start) // num_questions
    
    # Draw horizontal lines for each row
    for i in range(1, num_questions):
        y = y_start + i * row_height
        cv.line(vis_img, (x_start, y), (x_end, y), (0, 0, 255), 1)
    
    # Draw vertical lines to separate A, B, C, D, E columns
    option_width = (x_end - x_start) // 5
    for i in range(1, 5):
        x = x_start + i * option_width
        cv.line(vis_img, (x, y_start), (x, y_end), (0, 0, 255), 1)
    
    cv.imwrite("answer_extraction.jpg", vis_img * 255)

    return(vis_img)

def extract_answers(final):
    # print("Extracting answers!")
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
        # if (q < 18):
        #     print("Question ", q)
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
                    answers[str(q)] = options[i]
        else:
            answers[str(q)] = options[4]
    
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

def generate_score_report():
    print("hello")