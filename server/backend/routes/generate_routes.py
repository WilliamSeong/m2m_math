from flask import Blueprint, jsonify, request, send_file

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from bson.objectid import ObjectId
from bson.binary import Binary

from datetime import datetime

import io
import random
import math
import copy
import re

from backend.db import get_client

generate_bp = Blueprint("generate", __name__)

@generate_bp.route("", methods=['POST'])
def generate():
    print("Generating packet")
    data = request.get_json()

    objective_list = data.get("objectiveList")
    student_id = data.get("studentId")
    options = ["A", "B", "C", "D"]

    try:
        client = get_client()

        result = generateQuestions(client, objective_list)
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
