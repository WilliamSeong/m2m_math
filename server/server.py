from flask import Flask, request
from flask import jsonify
from flask import send_file
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson.binary import Binary
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

import cv2 as cv
import numpy as np
import re
import base64
import math
import random
import copy
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import io
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

# Generate pdf
@app.route("/pdf")
def pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test Packet!", align="C")

        # Get the PDF content as bytes
        pdf_bytes = pdf.output()
        # print(f"pdf in byte form: {pdf_bytes}")

        # Create a blob-like object using io.BytesIO
        pdf_blob = io.BytesIO(pdf_bytes)
        # print(f"pdf blob form: {pdf_blob}")
        # Reset the file pointer to the beginning
        pdf_blob.seek(0)
        
        # Return the PDF as a downloadable file
        return send_file(
            pdf_blob,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )
    except Exception as e:
        return jsonify({'error' : e})

# Get all students
@app.route("/students")
def students():
    print("Fetching students")
    try:
        result = fetchStudents(client)
        # json string the list with dumps (Mongo ObjectId won't jsonify)
        json_data = dumps(result)
        return json_data
    except Exception as e:
        print(f"Student fetching error: {e}")
        return jsonify({'error' : e})
    
def fetchStudents(client):
    cursor = client["m2m_math_db"]["students"].find({})
    # convert mongo cursor to python list
    list_cur = list(cursor)
    return list_cur

# Get a student details and their packets
@app.route("/student/details", methods=['POST'])
def studentDetails():
    data = request.get_json()
    student_id = data.get("studentId")
    print(f"Fetching student {student_id} details")

    try:

        details_result = fetchStudentDetails(client, student_id)
        packets_result = fetchStudentPackets(client, student_id)

        json_data_details = dumps(details_result)
        json_data_packets = dumps(packets_result)

        return jsonify({'result' : json_data_details, 'packets' : json_data_packets})

    except Exception as e:
        return jsonify({'error' : e})

def fetchStudentDetails(client, student_id):
    # print("making call to db for student details with", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)

    result = client["m2m_math_db"]["students"].find_one({"_id" : student_id_obj})

    return result

def fetchStudentPackets(client, student_id):
    # print("Checking packets for student id: ", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    
    cursor = client["m2m_math_db"]["packets"].find({"student_id" : student_id_obj})
    
    list_cur = list(cursor)
    return list_cur

@app.route("/generate", methods=['POST'])
def generate():
    print("Generating packet")
    data = request.get_json()

    objective_list = data.get("objectiveList")
    student_id = data.get("studentId")
    options = ["A", "B", "C", "D"]
    try:

        # print(f"Objective list: {objective_list}")
        # print(f"Student id: {student_id}")

        result = generateQuestions(client, objective_list);
        ans_key = {}

        packet_id = createPacket(client, student_id)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        print(f"Packet id: {packet_id}")
        pdf.cell(200, 10, text=str(packet_id), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        for obj in objective_list:
            pdf.cell(200, 5, text=obj["name"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        for i, question in enumerate(result):
            # print(f"question {i}: {question}")
            pdf.cell(200, 5, text=f"{i + 1}. {question["question"]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                # Create a single string with all answers and their labels
            answer_line = ""

            shuffled_answers = shuffle(question["answers"])

            for j, answer in enumerate(shuffled_answers):

                # Add letter label based on index
                letter = chr(65 + j)  # 65 is ASCII for 'A'

                if shuffled_answers[j] == question["solution"]:
                    ans_key[str(i + 1)] = options[j]
                
                # Add spacing between answers except for the first one
                if j > 0:
                    answer_line += "   "
                
                # Add the labeled answer
                answer_line += f"[{letter}] {str(answer)}"
            
            # Print all answers on one line
            pdf.cell(200, 5, text=answer_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # print(f"answer key : {ans_key}")

        # pdf.multi_cell(200, 10, text=str(ans_key))

        # Get the PDF content as bytes
        pdf_bytes = pdf.output()
        # print(f"pdf in byte form: {pdf_bytes}")

        addPacketContent(client, packet_id, pdf_bytes, ans_key)

        # Create a blob-like object using io.BytesIO
        pdf_blob = io.BytesIO(pdf_bytes)
        # print(f"pdf blob form: {pdf_blob}")
        # Reset the file pointer to the beginning
        pdf_blob.seek(0)
        
        # Return the PDF as a downloadable file
        return send_file(
            pdf_blob,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )
    except Exception as e:
        return jsonify({'error' : e})
    
def createPacket(client, student_id):
    try:
        student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
        result = client["m2m_math_db"]["packets"].insert_one({"student_id" : student_id_obj, "submissions" : [], "date_created" : datetime.now()})
        packet_id = result.inserted_id
        client["m2m_math_db"]["students"].update_one({"_id": student_id_obj}, {"$push": {"packets_inprogress": packet_id}})
        return packet_id
    except Exception as e:
        return {'error' : e}

def addPacketContent(client, packet_id, packet, ans_key):
    mongo_packet = Binary(packet)
    packet_id_obj = ObjectId(packet_id['$oid']) if isinstance(packet_id, dict) else ObjectId(packet_id)
    print(f"addPacket packed id: {packet_id}")
    result = client["m2m_math_db"]["packets"].update_one({"_id" : packet_id_obj}, {'$set' : {"content" : mongo_packet, "answer_key" : ans_key}})
    return result
    
def shuffle(array):
    # Make a copy of the array (optional, if you want to preserve the original)
    # array_copy = array.copy()
    
    # Start from the last element
    for current_index in range(len(array) - 1, 0, -1):
        # Pick a random index from 0 to current_index
        random_index = random.randint(0, current_index)
        
        # Swap current_index with random_index
        array[current_index], array[random_index] = array[random_index], array[current_index]
    
    return array
    

def generateQuestions(client, objectives):
    print(f"Generating questions for objectives {objectives}")
    
    allQuestions = []

    for obj in objectives:
        student_id_obj = ObjectId(obj["id"]['$oid']) if isinstance(obj["id"], dict) else ObjectId(obj["id"])
        result = client["m2m_math_db"]["questions"].find_one({"objective_id" : student_id_obj})
        allQuestions += generateNQuestions(result, 5)
    
    return allQuestions

def generateNQuestions(template, n):
    question = template["template"]
    solution = template["correct_answer"]
    answers = copy.deepcopy(template["answers"])


    problems = []

    for _ in range(n):
        values = {}

        for var_name, constraints in template["variables"].items():
            # print(f"Variable name: {var_name}")
            # print(f"Constraints: {constraints}")
            if constraints.get('min') == 0:
                values[var_name] = math.floor(random.random() * constraints['max']) + 1
            else:
                # Original calculation works fine if min is already > 0
                values[var_name] = math.floor(random.random() * (constraints['max'] - constraints['min'] + 1) + constraints['min'])
        
        # print(f"Values: {values}")

        for var_name, value in values.items():
            # Create regex pattern
            pattern = r'{{' + var_name + r'}}'
            
            # Replace in question and solution
            question = re.sub(pattern, str(value), question)
            solution = re.sub(pattern, str(value), solution)
            
            # Replace in answers
            for index, ans in enumerate(answers):
                answers[index] = re.sub(pattern, str(value), ans)
        
        # Evaluate the solution and answers
        solution_str = solution.strip("{}")
        solution = eval(solution_str)

        for index, ans in enumerate(answers):
            ans_str = ans.strip("{}")
            answers[index] = eval(ans_str)

        problems.append({"question": question, "solution": solution, "answers": answers})
            
        question = template["template"]
        solution = template["correct_answer"]
        answers = copy.deepcopy(template["answers"])
    
    # print(f"Problems: {problems}")
    return problems

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
    
file_path = "testImage.png"
print(f"File exists: {os.path.exists(file_path)}")

@app.route("/process", methods=['POST'])
def process():
    print("Processing image")
    try:
        data = request.get_json()
        image_uri = data.get("uri")
        # packet_id = data.get("packetId")
        packet_id = "67eb0f7182159cf0f5c40629"

        print(f"Packet Id for grading: {packet_id}")

        if not image_uri:
            return jsonify({'error': 'No image URI provided'})
        
        final, final_binary = sheet(image_uri)
        final_png = numpy_to_uri(final)
        vis_final = visualize_extraction_regions(final_binary)
        vis_final_png = numpy_to_uri(vis_final)
        student_answers = extract_answers(final_binary)
        print(f"answers: {student_answers}")

        answer_key = getAnswerKey(client, packet_id)
        print(f"answer key: {answer_key}")

        correct, incorrect = grade(student_answers, answer_key)

        pushSubmission(client, packet_id, final_png, vis_final_png, correct, incorrect)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})
    
def pushSubmission(client, packet_id, final_uri, vis_uri, correct, incorrect):
    try:
        packet_id_obj = ObjectId(packet_id) if isinstance(packet_id, dict) else ObjectId(packet_id)
        document = {
                    "packet_id" : packet_id_obj, 
                    "images" : 
                        {
                            "original" : final_uri, 
                            "processed" : vis_uri
                        },
                    "score" :
                        {
                            "correct" : correct,
                            "incorrect" : incorrect,
                        }
                    }
        result = client["m2m_math_db"]["submissions"].insert_one(document)
        submission_id = result.inserted_id
        client["m2m_math_db"]["packets"].update_one({"_id": packet_id_obj}, {"$push": {"submissions": submission_id}})
        return result
    except Exception as e:
        print("Image insert error for questions: ", e)
        return None

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
    correct = 0
    incorrect = 0
    for key, value in answer_key.items():
        print(f"question {key}: answer key-{value} answer-{answers[key]}")
        student_answer = value
        correct_answer = answers[key]
        if (student_answer == correct_answer):
            correct += 1
        else:
            incorrect += 1
    
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
