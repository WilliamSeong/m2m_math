from flask import Blueprint, jsonify, request, send_file

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from bson.objectid import ObjectId
from bson.binary import Binary

from datetime import datetime

import io
from io import BytesIO
import os
import random
import math
import copy
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

from backend.db import get_client
from backend.registry import generators

import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from questions.grade_1 import q1_10
from questions.pre_algebra import q81_90

generate_bp = Blueprint("generate", __name__)

# There are 1382 obj

@generate_bp.route("/test",)
def test():
    print('Testing decorator')

    factory = QuestionFactory([])
    factory.test_decorator()

    return jsonify({'success':True})

@generate_bp.route("", methods=['POST'])
def generate():
    print("Generating packet")
    data = request.get_json()

    objective_list = data.get("objectiveList")
    student_id = data.get("studentId")
    print(f"Objective list for generation: {objective_list}")
    print(f"Student id for generation: ", student_id)

    try:
        client = get_client()

        packet_id = createPacket(client, student_id)

        pdf = FPDF(format="letter", unit="in")

        pdf_width = pdf.w
        pdf_width_usable = pdf.epw
        margin = (pdf_width - pdf_width_usable)/2
        usuable_width = pdf_width - (margin*2)

        pdf.add_page()
        pdf.set_font("Times", size=12)

        initializePage(pdf, packet_id, student_id, usuable_width)
        for key, value in objective_list.items():
            pdf.cell(pdf_width_usable, .5, text=value)
            pdf.ln(.25)
        pdf.ln(.25)
        pdf.line(.4, pdf.get_y(), 8.5-.4, pdf.get_y())
        pdf.ln(.25)

        ans_key = {}
        questions = []

        factory = QuestionFactory(questions)

        for key, value in objective_list.items():
            factory.generate_question(key)
        
        random.shuffle(questions)

        add_question_to_pdf(pdf, questions, ans_key, packet_id, student_id, usuable_width)
        
        # Get the PDF content as bytes
        pdf_bytes = pdf.output()

        addPacketContent(client, packet_id, pdf_bytes, ans_key)

        # Create a blob-like object using io.BytesIO
        pdf_blob = io.BytesIO(pdf_bytes)

        # Reset the file pointer to the beginning
        pdf_blob.seek(0)
        
        # Return the PDF as a downloadable file
        return send_file(
            pdf_blob,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )

        # return jsonify({'success' : True})
    except Exception as e:
        return jsonify({'error' : e})
    
def initializePage(pdf, packet_id, student_id, width):
    # Calculate widths for each cell
    left_cell_width = width / 2  # Adjust this ratio as needed
    right_cell_width = width / 2
    
    # Save the starting Y position
    starting_y = pdf.get_y()
    
    # First cell (top left) - use ln=0 to prevent line break
    pdf.cell(left_cell_width, 0.5, text=f"Packet: {str(packet_id)}", align="L", ln=0)
    
    # Second cell (top right)
    pdf.cell(right_cell_width, 0.5, text=f"Student: {str(student_id['$oid'])}", align="R", ln=1)
    pdf.line(.4, pdf.get_y(), 8.5-.4, pdf.get_y())

    pdf.set_y(starting_y + .5)  # Move down by height of cell

def createPacket(client, student_id):
    try:
        student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
        result = client["m2m_math_db"]["packets"].insert_one({"student_id" : student_id_obj, "submissions" : [], "date_created" : datetime.now()})
        packet_id = result.inserted_id
        print(f"Inserting packet {packet_id} to student {student_id_obj}")
        client["m2m_math_db"]["students"].update_one({"_id": student_id_obj}, {"$set": {f"packets_inprogress.{packet_id}": True, "last_assignment": datetime.now()}})
        return packet_id
    except Exception as e:
        return {'error' : e}

def addPacketContent(client, packet_id, packet, ans_key):
    mongo_packet = Binary(packet)
    print(f"packet_id: {packet_id}")
    packet_id_obj = ObjectId(packet_id['$oid']) if isinstance(packet_id, dict) else ObjectId(packet_id)
    result = client["m2m_math_db"]["packets"].update_one({"_id" : packet_id_obj}, {'$set' : {"content" : mongo_packet, "answer_key" : ans_key}})
    return result

def add_question_to_pdf(pdf, questions, ans_key, packet_id, student_id, width):
    print(f"There are {len(questions)} questions")
    for i, question in enumerate(questions):
        # Calculate width (8.5 inches minus 1-inch total margins)
        page_width = pdf.epw
        margin = .4

        # Check if there's enough space on the current page for the image
        # Get image dimensions
        img_width = page_width - .25
        img = Image.open(question['image'])
        img_height = (img.height / img.width) * img_width
        
        # Add some buffer space for the number and padding
        total_needed_height = img_height + 0.2
        
        # Check if we need to add a page break
        if pdf.get_y() + total_needed_height > pdf.eph:
            pdf.add_page()
            initializePage(pdf, packet_id, student_id, width)
        
        # Now add the question number and image together
        current_y = pdf.get_y() + .25

        # Add question number in left margin
        pdf.set_xy(margin - .05, current_y)  # Position to the left of image
        pdf.set_font('Times', 'B', 13)  # Bold
        pdf.cell(.05, .05, f"{i+1}.")
        pdf.set_font('Times', '', 12)   # Regular
        
        # Add the complete question image (includes question number, text, diagram, and choices)
        pdf.set_xy(margin, current_y-0.12)  # Reset x position for image
        pdf.image(question['image'], x=0.65, w=page_width-.25)

        pdf.set_y(current_y + img_height + 0.1)

        # Construct answer key
        ans_key[str(i + 1)] = question["correct_answer"]

class QuestionFactory:
    def __init__(self, questions):
            # self.pdf = pdf
            self.questions = questions
            self.generators = generators

    def generate_question(self, question_id):
        if question_id in self.generators:
            # Call the appropriate function with the provided parameters
            # return self.generators[question_id](**params)
            self.generators[question_id](self.questions)
            print(f"Handler exists for id {question_id}")
        else:
            print(f"Handler does not exist for id {question_id}")

    def test_decorator(self):
        print(self.generators)