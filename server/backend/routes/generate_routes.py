from flask import Blueprint, jsonify, request, send_file

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from bson.objectid import ObjectId
from bson.binary import Binary

from datetime import datetime

import io
from io import BytesIO
import random
import math
import copy
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

from backend.db import get_client

generate_bp = Blueprint("generate", __name__)

@generate_bp.route("", methods=['POST'])
def generate():
    print("Generating packet")
    data = request.get_json()

    objective_list = data.get("objectiveList")
    student_id = data.get("studentId")

    try:
        client = get_client()

        # result = generateQuestions(client, objective_list)
        print(f"Objectives: {objective_list}")
        packet_id = createPacket(client, student_id)

        pdf = FPDF(format="letter", unit="in")

        pdf_width = pdf.w
        pdf_width_usable = pdf.epw
        print(f"pdf width: {pdf_width}")
        print(f"pdf effective: {pdf_width_usable}")
        margin = (pdf_width - pdf_width_usable)/2
        print(f".75 inch : {margin}")
        usuable_width = pdf_width - (margin*2)
        print(f"Usable width: {usuable_width}")

        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        # print(f"Packet id: {packet_id}")
        pdf.cell(pdf_width_usable, .5, text=str(packet_id), align="C", border=1)
        pdf.ln(.5)

        for obj in objective_list:
            pdf.cell(pdf_width_usable, .5, text=obj["name"])
            pdf.ln(.25)
        pdf.ln(.25)
        pdf.line(.4, pdf.get_y(), 8.5-.4, pdf.get_y())
        pdf.ln(.25)



        ans_key = {}
        questions = []

        factory = QuestionFactory(questions)

        for question in objective_list:
            print(question["id"]["$oid"])
            factory.generate_question(question["id"]["$oid"])
        
        random.shuffle(questions)

        add_question_to_pdf(pdf, questions, ans_key)
        
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

        # return jsonify({'success' : True})
    except Exception as e:
        return jsonify({'error' : e})
    
class QuestionFactory:
    def __init__(self, questions):
            # self.pdf = pdf
            self.questions = questions
            self.generators = {
                '67f02b21cc26b50fa38d3145': generate_circle_area_question,
                '67f1648ccc26b50fa38d3163' : generate_diameter_area_question
                # Add more question handlers
            }

    def generate_question(self, question_id):
        if question_id in self.generators:
            # Call the appropriate function with the provided parameters
            # return self.generators[question_id](**params)
            self.generators[question_id](self.questions)
            print(f"Handler exists for id {question_id}")
        else:
            print(f"Handler does not exist for id {question_id}")

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
    # print(f"addPacket packed id: {packet_id}")
    result = client["m2m_math_db"]["packets"].update_one({"_id" : packet_id_obj}, {'$set' : {"content" : mongo_packet, "answer_key" : ans_key}})
    return result

def generate_diameter_area_question(questions):
    unique_numbers = random.sample(range(0, 10), 5)

    for rad in unique_numbers:
        # print(f"Generating question with area {rad * rad}")
        questions += [create_diameter_area_question(rad)]

def create_diameter_area_question(radius):
    # Create figure and axis
    fig = plt.figure(1, figsize=(7.7,1))

    fig.patch.set_facecolor('white')

    # Add choices at bottom
    diameter = radius * 2
    
    # Generate plausible wrong answers
    wrong_answers = [
        radius,  # Using radius instead of diameter
        radius/2,  # Using circumference
        round(diameter - random.randint(1, 2))  # Just wrong
    ]
    
    # All answer choices
    all_answers = wrong_answers + [diameter]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(diameter)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    # Add question text
    fig.text(0.05, 0.8, f"The area of a circle is {radius**2}$\\pi$ cm$^2$. What is the diameter of the circle?", ha='left', fontsize=12)

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.3, f"[A] {all_answers[0]} cm", ha='center', fontsize=12)
    fig.text(0.32, 0.3, f"[B] {all_answers[1]} cm", ha='center', fontsize=12)
    fig.text(0.52, 0.3, f"[C] {all_answers[2]} cm", ha='center', fontsize=12)
    fig.text(0.72, 0.3, f"[D] {all_answers[3]} cm", ha='center', fontsize=12)

    # fig.savefig('diameter.png')
    plt.tight_layout(pad=0.1)

    # Save to BytesIO
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=300)
    plt.close(fig)
    img_data.seek(0)
    
    return {
        'id' : 1,
        'image': img_data,
        'correct_answer': correct_letter,
        'correct_value': diameter
    }

def generate_circle_area_question(questions):
        unique_numbers = random.sample(range(0, 20), 5)

        for rad in unique_numbers:
            # print(f"Generating question with radius {rad}")
            questions += [create_circle_area_question(rad)]

def create_circle_area_question(radius):
    fig, ax = plt.subplots(1, figsize=(7.7,2.5))
    fig.subplots_adjust(left=.05, right=.3, top=.8, bottom=.2)

    # Set background color to white
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Create a circle patch
    circle = plt.Circle((4, 5), 3, fill=False)

    # Create radius line
    ax.plot([4, 7], [5, 5], 'k-') # line from (.4, .5) to (.7, .5)
    ax.plot(4, 5, 'ko', markersize=4)  # Center dot

    # Create radius label
    ax.text(5.5, 5.2, f"{radius} ft", ha='center')

    # Add the circle to the axes
    ax.add_patch(circle)

    # Ensure the aspect ratio is equal so that the circle is not distorted
    ax.set_aspect('equal', adjustable='box')

    # Remove axes ticks and labels for a cleaner look, if desired
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Show the plot
    # plt.show()

    # Save the plot
    # fig.savefig('plotcircles.png')
    
    # Add choices at bottom
    area = math.pi * radius**2
    rounded_area = round(area)
    
    # Generate plausible wrong answers
    wrong_answers = [
        round(math.pi * radius),  # Using radius instead of radius squared
        round(2 * math.pi * radius),  # Using circumference
        round(area - random.randint(5, 10))  # Just wrong
    ]
    
    # All answer choices
    all_answers = wrong_answers + [rounded_area]
    random.shuffle(all_answers)
    
    # Find index of correct answer
    correct_index = all_answers.index(rounded_area)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D
    
    # plt.tight_layout()
    
    # Right text question and text answers
    fig.text(.05, .92, f"What is the area of the circle? Use 3.14 for π and round to the nearest whole number.", ha='left', fontsize=12)
    fig.text(0.12, 0.05, f"[A] {all_answers[0]} ft²", ha='center', fontsize=12)
    fig.text(0.32, 0.05, f"[B] {all_answers[1]} ft²", ha='center', fontsize=12)
    fig.text(0.52, 0.05, f"[C] {all_answers[2]} ft²", ha='center', fontsize=12)
    fig.text(0.72, 0.05, f"[D] {all_answers[3]} ft²", ha='center', fontsize=12)

    # Save to BytesIO
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=300)
    plt.close(fig)
    img_data.seek(0)
    
    return {
        'id' : 2,
        'image': img_data,
        'correct_answer': correct_letter,
        'correct_value': rounded_area
    }

def add_question_to_pdf(pdf, questions, ans_key):

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
        total_needed_height = img_height + 0.3
        
        # Check if we need to add a page break
        if pdf.get_y() + total_needed_height > pdf.eph:
            pdf.add_page()
        
        # Now add the question number and image together
        current_y = pdf.get_y()


        # Add question number in left margin
        pdf.set_xy(margin - .05, current_y)  # Position to the left of image
        pdf.cell(.05, .05, f"{i+1}.")
        # img = Image.open(question['image'])
        # width, height = img.size
        # print(f"Question {i+1} has width {width} and height {height}")

        # Add the complete question image (includes question number, text, diagram, and choices)
        pdf.set_xy(margin, current_y-0.12)  # Reset x position for image
        pdf.image(question['image'], x=0.65, w=page_width-.25)

        pdf.set_y(current_y + img_height + 0.35)

        # Construct answer key
        ans_key[str(i + 1)] = question["correct_answer"]