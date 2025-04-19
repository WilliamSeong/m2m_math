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
import matplotlib.patches as patches
from PIL import Image
import numpy as np

from backend.db import get_client

generate_bp = Blueprint("generate", __name__)

# There are 1382 obj

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
        pdf.set_font("Helvetica", size=12)

        initializePage(pdf, packet_id, student_id, usuable_width)
        for key, value in objective_list.items():
            print(f"OBJECT: {key}{value}")
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
        pdf.cell(.05, .05, f"{i+1}.")
        
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
            self.generators = {
                '67f02b21cc26b50fa38d3145' : generate_circle_area_question,
                '67f1648ccc26b50fa38d3163' : generate_diameter_area_question,
                '67f684becc26b50fa38d31a4' : generate_dock_scale_question,
                "67fb3159ee43b6ac0569c485" : generate_ratio_two_lengths_question,
                "67fbfb4eee43b6ac0569c488" : generate_geometric_scale_drawing_area_question,
                "67fc451aee43b6ac0569c490" : generate_ratio_scale_drawing_figure_question,
                "67fca2f6ee43b6ac0569c495" : generate_triangle_from_angles_sides_question,
                "67fd763cee43b6ac0569c49d" : generate_3d_prism_slice_question,
                "67fd9a8dee43b6ac0569c4a3" : generate_area_circumference_in_pi,
                "67ff16feee43b6ac0569c4b3" : generate_area_circumference_wp
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

def intify(value):
    return int(value) if (value == int(value)) else round(value, 2)

def addIntChoices(fig, choices, unit):
        fig.text(0.12, 0.1, f"[A] {intify(choices[0])} {unit}", ha='center', fontsize=12, family='serif')
        fig.text(0.32, 0.1, f"[B] {intify(choices[1])} {unit}", ha='center', fontsize=12, family='serif')
        fig.text(0.52, 0.1, f"[C] {intify(choices[2])} {unit}", ha='center', fontsize=12, family='serif')
        fig.text(0.72, 0.1, f"[D] {intify(choices[3])} {unit}", ha='center', fontsize=12, family='serif')

def addStrChoices(fig, choices):
        fig.text(0.12, 0.1, f"[A] {choices[0]}", ha='center', fontsize=12, family='serif')
        fig.text(0.32, 0.1, f"[B] {choices[1]}", ha='center', fontsize=12, family='serif')
        fig.text(0.52, 0.1, f"[C] {choices[2]}", ha='center', fontsize=12, family='serif')
        fig.text(0.72, 0.1, f"[D] {choices[3]}", ha='center', fontsize=12, family='serif')

def addQuestion(fig, question):
        fig.text(0.01, 0.97,
                question, 
                ha='left',
                va='top',
                fontsize=12,
                wrap=True,
                family='serif'
            )

def cleanAx(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

def saveQuestion(id, fig, correct_letter, correct_value):
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=300)
    plt.close(fig)
    img_data.seek(0)

    return {
        'id' : id,
        'image': img_data,
        'correct_answer': correct_letter,
        'correct_value': correct_value
    }

def generate_dock_scale_question(questions):
    for _ in range(5):
        total_length = random.randint(10,20) * .5
        walkway_length = random.randint(math.floor(total_length*.5), 2 * math.floor(total_length * .7)) * .5
        walkway_width = random.randint(1, math.floor(walkway_length)) * .25
        ratio = random.randint(1,15)
        question = random.randint(0,2)

        questions += [create_dock_scale_question(total_length, walkway_width, walkway_length, ratio, question)]

def create_dock_scale_question(full_length, walkway_width, walkway_length, feet_ratio, question):
    # Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7,3))

    # Add axes that is 0.1 from left, 0.2 from top, 0.7 width of fig and .5 heigh of fig
    ax = fig.add_axes([0.1, 0.2, 0.7, .5 ])

    # Set limits of ax
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3.5)

    # Plot Rectangle
    walkway = patches.Rectangle((0.5, 1), 2, 1, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(walkway)

    # Plot Octagon
    octagon_points = [(2.5, 1), (2.5, 2), (3, 3), (3.5, 3), (4, 2), (4, 1), (3.5, 0), (3, 0)]
    dock = patches.Polygon(octagon_points, closed=True, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(dock)

    # Draw the planks
    for i in range(35):
        i += 1
        i *= .1
        if i < 2:
            ax.plot([i+.5, i+.5], [2,1], 'k-', linewidth=0.5)
        elif i < 2.5:
            ax.plot([i+.5, i+.5], [(i-2)*2 + 2,1-(i-2)*2], 'k-', linewidth=0.5)
        elif i < 3:
            ax.plot([i+.5, i+.5], [3,0], 'k-', linewidth=0.5)
        else:
            ax.plot([i+.5, i+.5], [(1-(i-3)*2)+2, 1-(1-(i-3)*2)], 'k-', linewidth=0.5)

    # Plot length line
    ax.plot([0.5, 4], [3.3, 3.3], 'k-', linewidth=1)
    ax.plot([0.5,0.5], [3.2,3.4], 'k-', linewidth=0.5)
    ax.plot([4,4], [3.2,3.4], 'k-', linewidth=0.5)

    # Plot labels
    ax.text(2.3, 3.4, f'{full_length} in.', ha='center', fontsize='small')
    ax.text(0, 1.35, f'{walkway_width} in.', ha='left', fontsize='small')
    ax.text(1.5, .6, f'{walkway_length} in.', ha='center', fontsize='small')
    ax.text(4.1, 1.35, f'{walkway_width} in.', ha='left', fontsize='small')

    # Question options
    questions = [
                    "What is the actual length of the entire dock?",
                    "What is the actual width of the dock's walkway?",
                    "What is the actual length of the dock's walkway?"
                ]

    # Find correct answer
    if question == 0:
        answer = full_length * feet_ratio
    elif question == 1:
        answer = walkway_width * feet_ratio
    elif question == 2:
        answer = walkway_length * feet_ratio

    # Generate plausible wrong answers
    if question == 0:
        wrong_answers = [
                            walkway_length * feet_ratio,
                            round(feet_ratio / walkway_length, 2),
                            full_length * feet_ratio + random.randint(-3,3)
                        ]
    elif question == 1:
        wrong_answers = [
                            round(walkway_width / feet_ratio),
                            feet_ratio + walkway_width,
                            walkway_length + full_length + (2 * walkway_width)
                        ]
    elif question == 2:
        wrong_answers = [
                            (walkway_length + 1) * feet_ratio,
                            feet_ratio + walkway_length,
                            round(walkway_length / feet_ratio)
                        ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"A catalog has a scale drawing of a floating dock. The dock is a regular octagon attached to a rectangular walkway. The scale drawing has a scale of 1 inch:{feet_ratio} feet. {questions[question]}"

    addQuestion(fig, problem)

    addIntChoices(fig, all_answers, "in")

    cleanAx(ax)

    return saveQuestion(81, fig, correct_letter, answer)

def generate_ratio_two_lengths_question(questions):
    for _ in range(5):
            a = random.randint(2,10)
            if a <= 5:
                sample = random.sample(range(a+1, 10), 2)
                b = sample[0]
                c = sample[1]
            else:
                b = 1
                c = random.randint(a + 1, 11)

            real = random.randint(15, 60)

            questions += [create_ratio_two_lengths_question(a, b, c, real)]

def create_ratio_two_lengths_question(a, b, c, real):
    # Create figure and axis

    # Create fig that is 7.7 in. wide and 3 in. tall
    if a > b:
        fig = plt.figure(figsize=(7.7,3))
        # Define the coordinates of the trapezoid
        width = 6  # width of the base
        height = 4  # height of the trapezoid
        top_width = 4  # width of the top side

        # Add axes that is 0.1 from left, 0.2 from bottom, 0.7 width of fig and .5 heigh of fig
        ax = fig.add_axes([0.1, 0.2, 0.7, .4 ])

        # Set limits of ax
        ax.set_xlim(0, 6)
        ax.set_ylim(0, 5)

    else:
        fig = plt.figure(figsize=(7.7,2))
        # Define the coordinates of the trapezoid
        width = 4.5  # width of the base
        height = 2  # height of the trapezoid
        top_width = 3  # width of the top side

        ax = fig.add_axes([0.1, 0.3, 0.7, .4])

        # Set limits of ax
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 4)

    # Draw the trapezoid outline
    trapezoid_points = [(0, 1), ((width / 2) - (top_width / 2), height + 1), ((width / 2) + (top_width / 2), height + 1), (width, 1)]
    trapezoid = patches.Polygon(trapezoid_points, closed=True, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(trapezoid)

    # Plot partitions
    def add_detail(count):
        ax.plot([(width / 2) + (top_width / 2), (width / 2) + (top_width / 2)], [height + 1, 1],  'k-', linewidth=1)
        for i in range(count):
            increment = i*(top_width / count)
            ax.plot([(width / 2) - (top_width / 2) + increment, (width / 2) - (top_width / 2) + increment + .5], [height + 1, 1],  'k-', linewidth=1)
            ax.plot([(width / 2) - (top_width / 2) + increment, (width / 2) - (top_width / 2) + increment], [height + 1, 1],  'k-', linewidth=1)
    if a > b:
        add_detail(8)
    else:
        add_detail(5)
    
    # Plot dimensions
    if a > b:
        ax.text(5.1, 2.3, f'a', ha='center', fontsize='small', fontstyle='italic')
        ax.text(4.75, 4.2, f'b', ha='center', fontsize='small', fontstyle='italic')
        ax.text(5.4, .5, f'c', ha='center', fontsize='small', fontstyle='italic')
    else:
        ax.text(3.8, 1.7, f'a', ha='center', fontsize='small', fontstyle='italic')
        ax.text(3.5, 3.2, f'b', ha='center', fontsize='small', fontstyle='italic')
        ax.text(4, 0.5, f'c', ha='center', fontsize='small', fontstyle='italic')

    # Question options
    questions = [
                    ["a", a],
                    ["b", b],
                    ["c", c]
                ]
    
    choices = random.sample(questions, 2)

    # Answer
    answer = round(real * (choices[1][1]/choices[0][1]), 1)

    # Wrong Answers
    wrong_answers = [
                            round(real * (choices[0][1]/choices[1][1]), 1),
                            real,
                            real + choices[1][1]
                        ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"An engineer sketches a scale drawing of a bridge. In the drawing, the ratio of beam {choices[0][0]}'s length to beam {choices[1][0]}'s length is {choices[0][1]}:{choices[1][1]}. The actual length of beam {choices[0][0]} will be {real} m. What will be the actual length of beam {choices[1][0]} ?"
    addQuestion(fig, problem)

    addIntChoices(fig, all_answers, "m")

    cleanAx(ax)

    return saveQuestion(82, fig, correct_letter, answer)

def generate_geometric_scale_drawing_area_question(questions):
    for _ in range(5):
        rand = random.randint(20, 41)
        kitchen_length = living_length = int(rand * .25) if (rand * .25 == int(rand * .25)) else rand * .25
        bedroom_width = bedroom_length = dining_length = int(rand//2 * .25) if (rand//2 * .25 == int(rand//2 * .25)) else rand//2 * .25
        kitchen_width = int(rand // 3 * .25) if (rand // 3 * .25 == int(rand // 3 * .25)) else rand // 3 * .25

        scale = random.randint(2, 10)
        questions += [create_geometric_scale_drawing_area_question(kitchen_length, kitchen_width, bedroom_width, bedroom_length, living_length, dining_length, scale)]

def create_geometric_scale_drawing_area_question(kitchen_length, kitchen_width, bedroom_width, bedroom_length, living_length, dining_length, scale):
    # Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7,3))
    # Add axes that is 0.1 from left, 0.2 from bottom, 0.7 width of fig and .5 heigh of fig
    ax = fig.add_axes([0.1, 0.2, 0.6, .6 ])

    # Set limits of ax
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)

    # Draw the blueprint
    blueprint_points = [(1, 1), (1, 3), (3, 3), (3, 4), (9, 4), (9, 1)]
    blueprint = patches.Polygon(blueprint_points, closed=True, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(blueprint)

    # Plot partitions
    # Bedroom Wall
    ax.plot([3, 3],[1, 2.1], 'k-', linewidth=1)
    ax.plot([3, 3],[2.7, 3], 'k-', linewidth=1)

    # Bathroom/Kitchen Wall
    ax.plot([3, 3.2],[3, 3], 'k-', linewidth=1)
    ax.plot([3.8, 5.8],[3, 3], 'k-', linewidth=1)
    ax.plot([6.5, 8],[3, 3], 'k-', linewidth=1)
    ax.plot([8.7, 9],[3, 3], 'k-', linewidth=1)

    # Bathroom-Kitchen inbetween Wall
    ax.plot([5, 5],[3, 4], 'k-', linewidth=1)

    # Dining Room Wall
    ax.plot([7, 7],[1, 2], 'k-', linewidth=1)
    ax.plot([7, 7],[2.7, 3], 'k-', linewidth=1)

    # Plot labels
    ax.text(4, 3.4, f'Bathroom', ha='center', fontsize='small')
    ax.text(7, 3.4, f'Kitchen', ha='center', fontsize='small')
    ax.text(2, 1.9, f'Bedroom', ha='center', fontsize='small')
    ax.text(5, 1.9, f'Living Room', ha='center', fontsize='small')
    ax.text(8, 1.9, f'Dining Room', ha='center', fontsize='small')

    # Plot dimensions
    ax.plot([1, 9], [.7, .7], 'k-', linewidth=1)
    ax.plot([1, 1], [.8, .6], 'k-', linewidth=1)
    ax.plot([3, 3], [.8, .6], 'k-', linewidth=1)
    ax.plot([7, 7], [.8, .6], 'k-', linewidth=1)
    ax.plot([9, 9], [.8, .6], 'k-', linewidth=1)

    ax.plot([.7, .7], [1, 3], 'k-', linewidth=1)
    ax.plot([.6, .8], [3, 3], 'k-', linewidth=1)
    ax.plot([.6, .8], [1, 1], 'k-', linewidth=1)

    ax.plot([9.3, 9.3], [3, 4], 'k-', linewidth=1)
    ax.plot([9.2, 9.4], [4, 4], 'k-', linewidth=1)
    ax.plot([9.2, 9.4], [3, 3], 'k-', linewidth=1)

    ax.plot([5, 9], [4.3, 4.3], 'k-', linewidth=1)
    ax.plot([5, 5], [4.2, 4.4], 'k-', linewidth=1)
    ax.plot([9, 9], [4.2, 4.4], 'k-', linewidth=1)

    # Plot dimension labels
    ax.text(7, 4.5, f'{kitchen_length} in.', ha='center', va='center', fontsize='small')
    ax.text(10, 3.5, f'{kitchen_width} in.', ha='center', va='center', fontsize='small')
    ax.text(0, 2, f'{bedroom_width} in.', ha='center', va='center', fontsize='small')
    ax.text(2, 0.4, f'{bedroom_length} in.', ha='center', va='center', fontsize='small')
    ax.text(5, 0.4, f'{living_length} in.', ha='center', va='center', fontsize='small')
    ax.text(8, 0.4, f'{dining_length} in.', ha='center', va='center', fontsize='small')

    # answer
    answer = (scale * scale * (living_length + dining_length) * (kitchen_width + bedroom_width)) + (scale * scale * bedroom_width * bedroom_length)

    # wrong answers
    wrong_answers = [
                        ((living_length + dining_length) * (kitchen_width + bedroom_width)) + (bedroom_width * bedroom_length) * scale,
                        ((bedroom_length + living_length + dining_length) * scale) * ((bedroom_width + kitchen_width) * scale),
                        ((living_length + dining_length) * scale) + ((kitchen_width + bedroom_width) * scale)
                    ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"The scale drawing below shows the floor plan of an apartment. The scale is 1 inch:{scale} feet. What is the actual area of the apartment?"
    addQuestion(fig, problem)

    addIntChoices(fig, all_answers, "ft\u00B2")

    cleanAx(ax)
    
    return saveQuestion(83, fig, correct_letter, answer)

def generate_ratio_scale_drawing_figure_question(questions):
        for _ in range(5):
            length = random.randint(2,10)
            width = random.randint(-1,1) + length
            ratio = random.randint(2,10)
            questions += [create_ratio_scale_drawing_figure_question(length, width, ratio)]

def create_ratio_scale_drawing_figure_question(length, width, ratio):
    # Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7,3))
    # Add axes that is 0.1 from left, 0.2 from bottom, 0.7 width of fig and .5 heigh of fig
    ax = fig.add_axes([0.1, 0.2, 0.6, .6 ])

    # Set limits of ax
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)

    # Question options
    questions = [
                    'basement',
                    'living room',
                    'kitchen',
                    'bedroom',
                    'dining room'
                ]
    question = random.choice(questions)

    if length > width:
        # Draw the rectangle
        rectangle_points = [(1, 1), (1,4), (5, 4), (5, 1)]
        ax.text(3, 4.1, f"{length} in.", ha='center', fontsize='small')
        ax.text(.9, 2.5, f"{width} in.", ha='right', va='center', fontsize='small')
        ax.text(3, 2.5, f"{question}", ha='center', va='center', fontsize='small')
    elif width > length:
        rectangle_points = [(2, 1), (2,4), (4, 4), (4, 1)]
        ax.text(3, 4.1, f"{length} in.", ha='center', fontsize='small')
        ax.text(1.9, 2.5, f"{width} in.", ha='right', va='center', fontsize='small')
        ax.text(3, 2.5, f"{question}", ha='center', va='center', fontsize='small')
    else:
        rectangle_points = [(2, 1.5), (2,4), (4, 4), (4, 1.5)]
        ax.text(3, 4.1, f"{length} in.", ha='center', fontsize='small')
        ax.text(1.9, 2.75, f"{width} in.", ha='right', va='center', fontsize='small')
        ax.text(3, 2.75, f"{question}", ha='center', va='center', fontsize='small')

    rectangle = patches.Polygon(rectangle_points, closed=True, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(rectangle)

    # answer
    answer = f"1 in\u00B2 : {ratio ** 2} ft\u00B2"

    # wrong answers
    wrong_answers = [
                        f"1 in\u00B2 : {ratio} ft\u00B2",
                        f"{ratio**2} in\u00B2 : 1 ft\u00B2",
                        f"{length * width} in\u00B2 : {ratio} ft\u00B2"
                    ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    # Plot question
    problem = f"The diagram below is a scale drawing of a {question}. The ratio of the length in the drawing to that of the actual {question} is 1 inch : {ratio} feet. What is the ratio of the area of the drawing to that of the actual {question}?"
    addQuestion(fig, problem)

    addStrChoices(fig, all_answers)

    cleanAx(ax)

    return saveQuestion(84, fig, correct_letter, answer)

def generate_triangle_from_angles_sides_question(questions):
            for _ in range(5):
                # Question options
                options = [
                                'AAA',
                                'AAS',
                                'SAS',
                                'SSA',
                                'SSS'
                            ]
                
                question = random.choice(options)

                questions += [create_triangle_from_angles_sides_question(question)]

def create_triangle_from_angles_sides_question(question):
    # Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7, 1.25))

    # Possibilities
    # 1. AAA
        # More than two triangles
    # 2. AAS/ASA
        # One triangle
    # 3. SAS
        # One triangle
    # 4. SSA
        # S1 = opposite S2 = adjacent
            # if opposite > adjacent
                # One triangle
            # if opposite = adjacent * sin(A)
                # One triangle (right triangle)
            # if opposite < adjacent * sin(A)
                # No triangle
            # if adjacent * sin(A) < a < b
                # Two triangles
    # 5. SSS
        # One triangle

    if question == 'AAA':
        a = random.randint(10, 18)
        b = random.randint(4, 36 - a)
        c = (36 - a - b)

        a = f"m\u2220A = {a * 5}\u00B0"
        b = f"m\u2220B = {b * 5}\u00B0"
        c = f"m\u2220C = {c * 5}\u00B0"

        answer = 'More than 2 triangles are possible.'
    elif question == 'AAS':
        a = random.randint(10, 16)
        b = random.randint(4, 36 - a)
        c = (36 - a - b)
        
        angle_A = a * 5
        angle_B = b * 5
        
        side_length = random.randint(3, 12)

        choice = random.choice(['AAS', 'ASA'])
        if choice == 'AAS':
            a = f"m\u2220 A = {angle_A}\u00B0"
            b = f"m\u2220 B = {angle_B}\u00B0"
            c = f"AC = {side_length}"
        else:
            a = f"m\u2220 A = {angle_A}\u00B0"
            b = f"m\u2220 B = {angle_B}\u00B0"
            c = f"AB = {side_length}"
        answer = 'Exactly 1 triangle is possible.'
    elif question == 'SAS':
        # Generate two side lengths
        side_a = random.randint(3, 12)
        side_b = random.randint(3, 12)
        
        # Generate an angle between them (angle C)
        # Avoiding very small or very large angles
        c = random.randint(4, 32)  # This gives angles between 20° and 160°
        angle_C = c * 5

        a = f"AB = {side_a}"
        b = f"BC = {side_b}"
        c = f"m\u2220 C = {angle_C}\u00B0"
        answer = 'Exactly 1 triangle is possible.'
    elif question == 'SSS':
        side_a = random.randint(3, 12)
        side_b = random.randint(3, 12)

        min_side_c = abs(side_a - side_b) + 1  # +1 to avoid degenerate triangles
        max_side_c = side_a + side_b - 1  # -1 to avoid straight lines
        side_c = random.randint(min_side_c, max_side_c)

        a = f"AB = {side_a}"
        b = f"BC = {side_b}"
        c = f"AC = {side_c}"
        answer = 'Exactly 1 triangle is possible.'
    else:
        a = random.randint(4, 32)  # Between 20° and 160°
        angle_A = a * 5
        
        # Generate the adjacent side
        side_b = random.randint(5, 15)
        
        # Calculate the height (critical value)
        height = side_b * math.sin(math.radians(angle_A))
        
        # Decide which case to generate
        case = random.choice(["no_triangle", "one_triangle", "right_triangle", "two_triangles"])
        
        if case == "no_triangle":
            # side_a < height (no triangle possible)
            side_a = max(1, int(height - 1))  # Ensure it's less than height and an integer
            answer = "No triangle is possible."
            
        elif case == "one_triangle":
            # side_a > side_b (one triangle)
            side_a = side_b + random.randint(1, 5)
            answer = "Exactly 1 triangle is possible."
            
        elif case == "right_triangle":
            # We need a special case to get an integer that makes a right triangle
            # Look for Pythagorean triples or approximate
            # For simplicity, round to nearest integer (not perfectly accurate but workable)
            side_a = round(height)
            answer = "Exactly 1 triangle is possible."
        elif case == "two_triangles":
            # height < side_a < side_b (two triangles)
            # Find a whole number between height and side_b
            min_a = math.ceil(height + 0.1)
            max_a = side_b - 1
            
            if min_a < max_a:
                side_a = random.randint(min_a, max_a)
                answer = "Exactly 2 triangles are possible."
            else:
                # If we can't find a valid integer in the range, default to one triangle
                side_a = side_b + random.randint(1, 5)
                answer = "Exactly 1 triangle is possible."

        a = f"m\u2220 A = {angle_A}\u00B0"
        b = f"AB = {side_b}"
        c = f"BC = {side_a}"
    
    # all answers
    all_answers = [
                    "Exactly 1 triangle is possible.",
                    "Exactly 2 triangles are possible.",
                    "More than 2 triangles are possible.",
                    "No triangle is possible."    
                    ]
    
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"Triangle ABC has the following characteristics: {a} , {b} , and {c}. How many different triangles can be drawn with these characteristics?"
    addQuestion(fig, problem)

    # Add multiple choice options with proper spacing
    fig.text(0.07, 0.4, f"[A] {all_answers[0]}", fontsize=12, family='serif')
    fig.text(0.57, 0.4, f"[B] {all_answers[1]}", fontsize=12, family='serif')
    fig.text(0.07, 0.1, f"[C] {all_answers[2]}", fontsize=12, family='serif')
    fig.text(0.57, 0.1, f"[D] {all_answers[3]}", fontsize=12, family='serif')

    return saveQuestion(85, fig, correct_letter, answer)

def generate_3d_prism_slice_question(questions):
    for _ in range(5):
        # Question options
        shape = random.choice([
                "cube",
                "cone",
                "cylinder",
                "hemisphere",
                "triangular prism",
                "pyramid",
                "pyramid",
                "pyramid",
                "pyramid"
            ])
        slice = random.choice(['vertically', 'horizontally'])

        questions += [create_3d_prism_slice_question(shape, slice)]

def create_3d_prism_slice_question(shape, slice):
# Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7, 2))
    # Add axes that is 0.1 from left, 0.2 from bottom, 0.7 width of fig and .5 heigh of fig

    if shape == 'cube':
        ax = fig.add_axes([0.1, 0.2, 0.23, .6 ], projection='3d')

        vertices = np.array([
                                [0, 0, 0],  # vertex 0
                                [1, 0, 0],  # vertex 1
                                [1, 1, 0],  # vertex 2
                                [0, 1, 0],  # vertex 3
                                [0, 0, 1],  # vertex 4
                                [1, 0, 1],  # vertex 5
                                [1, 1, 1],  # vertex 6
                                [0, 1, 1]   # vertex 7
                            ])    
        edges = [
                    # Bottom face
                    [vertices[0], vertices[1]],
                    [vertices[1], vertices[2]],
                    # Top face
                    [vertices[4], vertices[5]],
                    [vertices[5], vertices[6]],
                    [vertices[6], vertices[7]],
                    [vertices[7], vertices[4]],
                    # Connecting edges
                    [vertices[0], vertices[4]],
                    [vertices[1], vertices[5]],
                    [vertices[2], vertices[6]],
                ]
        # Plot the edges
        for edge in edges:
            x = [edge[0][0], edge[1][0]]
            y = [edge[0][1], edge[1][1]]
            z = [edge[0][2], edge[1][2]]
            ax.plot(x, y, z, 'k-', linewidth=1)  # k- means black solid line
        # Define which edges should be dashed (hidden edges)
        dashed_edges = [
            [vertices[2], vertices[3]],
            [vertices[3], vertices[0]],
            [vertices[3], vertices[7]],
        ]
        # Plot dashed edges
        for edge in dashed_edges:
            x = [edge[0][0], edge[1][0]]
            y = [edge[0][1], edge[1][1]]
            z = [edge[0][2], edge[1][2]]
            ax.plot(x, y, z, 'k:', linewidth=1)  # k-- means black dashed line
        
        # Set limits of ax
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_zlim(0, 1)

        ax.set_box_aspect([1, 1, 1])
        ax.set_zticks([])
        ax.set_axis_off()

        answer = 'quadrilateral'

    elif shape == 'cone':
        ax = fig.add_axes([0.1, 0.2, 0.23, .6])
        # Create an oval (ellipse)
        center = (0.5, 0.2)
        width, height = 0.6, 0.2
        # Create bottom half of ellipse (solid)
        arc1 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=0, theta2=180,  # Bottom half
                                        edgecolor='black', linewidth=1, linestyle=':')
        ax.add_patch(arc1)

        # Create top half of ellipse (dotted)
        arc2 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=180, theta2=360,  # Top half
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc2)
        # Create the two lines forming the triangle part
        apex = (0.5, 0.8)  # Top point
        left_point = (0.2, 0.2)  # Left edge of oval
        right_point = (0.8, 0.2)  # Right edge of oval

        # Draw lines
        ax.plot([left_point[0], apex[0]], [left_point[1], apex[1]], 'k-')  # Left line
        ax.plot([right_point[0], apex[0]], [right_point[1], apex[1]], 'k-')  # Right line

        # Set limits of ax
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        # Set equal aspect ratio
        ax.set_aspect('equal')

        if slice == 'vertically':
            answer = 'triangle'
        else:
            answer = 'circle'
    
    elif shape == 'hemisphere':
        ax = fig.add_axes([0.1, 0.2, 0.23, .6])
        # Create an oval (ellipse)
        center = (0.5, 0.2)
        width, height = 0.6, 0.2
        # Create bottom half of ellipse (solid)
        arc1 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=0, theta2=180,  # Bottom half
                                        edgecolor='black', linewidth=1, linestyle=':')
        ax.add_patch(arc1)

        # Create top half of ellipse (dotted)
        arc2 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=180, theta2=360,  # Top half
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc2)
        # Create the two lines forming the triangle part
        apex = (0.5, 0.8)  # Top point
        left_point = (0.2, 0.2)  # Left edge of oval
        right_point = (0.8, 0.2)  # Right edge of oval

        # Draw lines
        arc3 = plt.matplotlib.patches.Arc(center, width, .6, 
                                        theta1=0, theta2=180,  # roof
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc3)

        # Set limits of ax
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        # Set equal aspect ratio
        ax.set_aspect('equal')

        if slice == 'vertically':
            answer = 'semicircle'
        else:
            answer = 'circle'

    elif shape == 'cylinder':
        ax = fig.add_axes([0.1, 0.2, 0.23, .6])
        # Create an oval (ellipse)
        center = (0.5, 0.2)
        width, height = 0.6, 0.2
        # Create bottom half of ellipse (dotted)
        arc1 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=0, theta2=180,  # Bottom half
                                        edgecolor='black', linewidth=1, linestyle=':')
        ax.add_patch(arc1)

        # Create top half of ellipse (solid)
        arc2 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=180, theta2=360,  # Top half
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc2)

        # Create top half of ellipse (solid)
        center = (0.5, 0.8)

        arc3 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=0, theta2=180,  # Bottom half
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc3)

        # Create top half of ellipse (solid)
        arc4 = plt.matplotlib.patches.Arc(center, width, height, 
                                        theta1=180, theta2=360,  # Top half
                                        edgecolor='black', linewidth=1, linestyle='-')
        ax.add_patch(arc4)

        ax.plot([.2, .2], [.2, .8], 'k-', linewidth=1)
        ax.plot([.8, .8], [.2, .8], 'k-', linewidth=1)

        # Set limits of ax
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        # Set equal aspect ratio
        ax.set_aspect('equal')

        if slice == 'vertically':
            answer = 'quadrilateral'
        else:
            answer = 'circle'

    elif shape == 'triangular prism':
        ax = fig.add_axes([0.1, 0.2, 0.23, .6 ], projection='3d')

        # Set limits and remove axis
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_zlim(0, 1)
        ax.set_box_aspect([1, 1, 1])
        ax.set_axis_off()

        # Define the vertices of the triangular prism (triangle face down)
        vertices = np.array([
            [0, 0, 0],    # 0: bottom front left
            [1, 0, 0],    # 1: bottom front right
            [0.5, 1, 0],  # 2: bottom back middle
            [0, 0, 1],    # 3: top front left
            [1, 0, 1],    # 4: top front right
            [0.5, 1, 1]   # 5: top back middle
        ])

        # Visible edges (solid lines)
        visible_edges = [
            # Bottom triangle
            [vertices[0], vertices[1]],
            # Front vertical edges
            [vertices[0], vertices[3]],
            [vertices[1], vertices[4]],
            # Top triangle
            [vertices[3], vertices[4]],
            [vertices[4], vertices[5]],
            [vertices[5], vertices[3]]
        ]

        # Plot the visible edges
        for edge in visible_edges:
            x = [edge[0][0], edge[1][0]]
            y = [edge[0][1], edge[1][1]]
            z = [edge[0][2], edge[1][2]]
            ax.plot(x, y, z, 'k-', linewidth=1)  # Solid lines

        # Hidden edges (dotted lines)
        hidden_edges = [
            # Back vertical edge
            [vertices[2], vertices[5]],
            [vertices[1], vertices[2]],
            [vertices[2], vertices[0]]
        ]

        # Plot hidden edges
        for edge in hidden_edges:
            x = [edge[0][0], edge[1][0]]
            y = [edge[0][1], edge[1][1]]
            z = [edge[0][2], edge[1][2]]
            ax.plot(x, y, z, 'k:', linewidth=1)  # Dotted lines

        ax.view_init(elev=15, azim=-70)

        if slice == 'vertically':
            answer = 'quadrilateral'
        else:
            answer = 'triangle'
    else:
        pyramid_sides = random.randint(3,7)
        ax = fig.add_axes([0.1, 0.2, 0.23, .6 ], projection='3d')

        def pyramid(sides, rotate):
    
            # Common settings
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_zlim(0, 1.5)
            ax.set_box_aspect([1, 1, 1])
            # ax.set_axis_off()
            
            # Number of sides in the base
            n_sides = sides  # 3, 4, 5, 6 sides
            
            # Create base vertices
            theta = np.linspace(0, 2*np.pi, n_sides, endpoint=False)
            base_x = np.cos(theta)
            base_y = np.sin(theta)
            base_z = np.zeros_like(base_x)
            
            # Apex of the pyramid
            apex = np.array([0, 0, 1.2])
            
            # Plot the base edges
            for j in range(n_sides):
                next_j = (j + 1) % n_sides  # Wrap around for the last point
                ax.plot([base_x[j], base_x[next_j]],
                        [base_y[j], base_y[next_j]],
                        [base_z[j], base_z[next_j]], 'k-', linewidth=1)
            
            # Define visible and hidden edges
            visible_edges = []
            hidden_edges = []
            
            # Determine which edges are visible and which are hidden
            # This depends on the viewing angle
            for j in range(n_sides):
                # Edge from base to apex
                edge = [
                    [base_x[j], base_y[j], base_z[j]],
                    [apex[0], apex[1], apex[2]]
                ]
                
                # For a simple rule: front edges are visible, back edges are hidden
                # Front half of the base
                if j <= n_sides//2:
                    visible_edges.append(edge)
                else:
                    hidden_edges.append(edge)
            
            # Plot visible edges
            for edge in visible_edges:
                ax.plot([edge[0][0], edge[1][0]],
                        [edge[0][1], edge[1][1]],
                        [edge[0][2], edge[1][2]], 'k-', linewidth=1)
            
            # Plot hidden edges
            for edge in hidden_edges:
                ax.plot([edge[0][0], edge[1][0]],
                        [edge[0][1], edge[1][1]],
                        [edge[0][2], edge[1][2]], 'k:', linewidth=1)
            ax.set_zticks([])
            ax.set_axis_off()
            ax.view_init(elev=15, azim=rotate)

        if pyramid_sides == 3:
            pyramid(3, 50)
            if slice == 'vertically':
                answer = 'quadrilateral'
            else:
                answer = 'triangle'

        elif pyramid_sides == 4:
            pyramid(4, 60)
            if slice == 'vertically':
                answer = 'quadrilateral'
            else:
                answer = 'quadrilateral'
        elif pyramid_sides == 5:
            pyramid(5, 70)
            if slice == 'vertically':
                answer = 'quadrilateral'
            else:
                answer = 'pentagon'
        else:
            pyramid(6, 90)
            if slice == 'vertically':
                answer = 'quadrilateral'
            else:
                answer = 'hexagon'

    # all answers
    all_answers = [
                    'triangle',
                    'quadrilateral',
                    'pentagon',
                    'hexagon',
                    'semicircle',
                    'circle',
                ]
    
    # wrong answers
    wrong_answers = [option for option in all_answers if option != answer]

    # all answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"A plane is sliced {slice} through this {shape}. What two-dimensional shape could be formed?"
    # Plot question
    fig.text(0.01, .99, problem, 
                ha='left',
                va='top',
                fontsize=12,
                wrap=True,
                family='serif'
            )
    
    addStrChoices(fig, all_answers)

    # Add multiple choice options with proper spacing
    # fig.text(0.10, 0.1, f"[A] {all_answers[0]}", fontsize=12, family='serif')
    # fig.text(0.35, 0.1, f"[B] {all_answers[1]}", fontsize=12, family='serif')
    # fig.text(0.60, 0.1, f"[C] {all_answers[2]}", fontsize=12, family='serif')
    # fig.text(0.85, 0.1, f"[D] {all_answers[3]}", fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(86, fig, correct_letter, answer)

def generate_area_circumference_in_pi(questions):
    for _ in range(5):
        # Determine units
        units = [
                    ["yards", "yd"],
                    ["milimeters", "mm"],
                    ["feet", "ft"],
                    ["inches", "in"],
                    ["meters", "m"],
                    ["centimeters", "cm"]
                ]
        # Determine number type
        number_type = ['fraction', 'decimal', 'whole']
        # Determine radius or diameter
        dimensions = ['radius', 'diameter']
        # Determine question
        results = ['area', 'circumference']

        unit = random.choice(units)
        type = random.choice(number_type)
        dimension = random.choice(dimensions)
        question = random.choice(results)

        questions += [create_area_circumference_in_pi(unit, type, dimension, question)]

def create_area_circumference_in_pi(unit, type, dimension, question):
# Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7, 1.25))

    # 4 scenarios
        # 1. Given the radius -> find area
        # 2. Given the diameter -> find area
        # 3. Given the radius -> find circumference
        # 4. Given the diameter -> find circumference

    def mixed_to_improper(whole, numerator, denominator):
        """Convert mixed number to improper fraction"""
        return whole * denominator + numerator, denominator

    def improper_to_mixed(numerator, denominator):
        """Convert improper fraction to mixed number"""
        whole = numerator // denominator
        numerator = numerator % denominator
        return whole, numerator, denominator

    if type == 'fraction':
        if random.random() < 0.5:
            number = random.randint(1,5)
        else:
            number = 0
        denominator = random.randint(2,5)
        numerator = random.randint(1,denominator-1)

        problem = fr"The {dimension} of a circle is ${number}\frac{{{numerator}}}{{{denominator}}}$ {unit[0]}. What is the {question} of the circle in terms of π?" if number != 0 else fr"The {dimension} of a circle is $\frac{{{numerator}}}{{{denominator}}}$ {unit[0]}. What is the {question} of the circle in terms of π?"
        
        if dimension == 'radius' and question == 'area':
            # Calculate correct answer (πr²)
            answer_numerator, answer_denominator = mixed_to_improper(number, numerator, denominator)
            # Square the radius
            squared_num = answer_numerator * answer_numerator
            squared_den = answer_denominator * answer_denominator
            answer_number, answer_numerator, answer_denominator = improper_to_mixed(squared_num, squared_den)
            
            # Format correct answer with π
            if answer_number == 0:
                answer = fr"$\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[1]}²"
            elif squared_num == 0:
                answer = fr"${answer_number}\pi$ {unit[1]}²"
            else:
                answer = fr"${answer_number}\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[1]}²"
            
            # Wrong answers
            # Using circumference formula (2πr) instead of area formula (πr²)
            wrong1_numerator, wrong1_denominator = mixed_to_improper(number, numerator, denominator)
            wrong1_number, wrong1_numerator, wrong1_denominator = improper_to_mixed(wrong1_numerator * 2, wrong1_denominator)
            
            # Using diameter formula (2r) instead of radius squared (r²)
            wrong2_numerator, wrong2_denominator = mixed_to_improper(number, numerator, denominator)
            wrong2_number, wrong2_numerator, wrong2_denominator = improper_to_mixed(wrong2_numerator * 2, wrong2_denominator)
            
            # Just squaring the numerator but not the denominator (common mistake)
            wrong3_numerator, wrong3_denominator = mixed_to_improper(number, numerator, denominator)
            wrong3_number, wrong3_numerator, wrong3_denominator = improper_to_mixed(wrong3_numerator * wrong3_numerator, wrong3_denominator)
            
            wrong_answers = [
                fr"${number}$ {unit[0]}²" if numerator == 0 else (fr"${wrong1_number}\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[1]}²" if wrong1_number != 0 else fr"$\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[1]}²"),
                
                fr"${number}$ {unit[0]}²" if numerator == 0 else (fr"${wrong2_number}\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[1]}²" if wrong2_number != 0 else fr"$\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[1]}²"),
                
                fr"${number}$ {unit[0]}²" if numerator == 0 else (fr"${wrong3_number}\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[1]}²" if wrong3_number != 0 else fr"$\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[1]}²"),
            ]
        elif dimension == 'radius' and question == 'circumference':
            answer_numerator, answer_denominator = mixed_to_improper(number, numerator, denominator)
            answer_number, answer_numerator, answer_denominator = improper_to_mixed(answer_numerator * 2, answer_denominator)
            if answer_number != 0:
                answer = fr"${answer_number}\frac{{{answer_numerator}}}{{{answer_denominator}}}$ {unit[0]}"
            else:
                answer = fr"$\frac{{{answer_numerator}}}{{{answer_denominator}}}$ {unit[0]}"
            
            # Using area formula (πr²) instead of circumference (2πr)
            wrong3_number, wrong3_denominator = mixed_to_improper(number, numerator, denominator)
            wrong3_number, wrong3_numerator, wrong3_denominator = improper_to_mixed(wrong3_number * wrong3_number, wrong3_denominator * wrong3_denominator)

            wrong_answers = [
                                fr"${number}$ {unit[0]}" if numerator == 0 else (fr"$\frac{{{numerator}}}{{{denominator}}}$ {unit[0]}" if number == 0 else fr"${number}\frac{{{numerator}}}{{{denominator}}}$ {unit[0]}"),
                                fr"${number}$ {unit[0]}" if numerator == 0 else (fr"${3 * number}\frac{{{3 * numerator}}}{{{denominator}}}$ {unit[0]}" if number != 0 else fr"$\frac{{{3 * numerator}}}{{{denominator}}}$ {unit[0]}"),
                                fr"${number}$ {unit[0]}" if numerator == 0 else (fr"${wrong3_number}\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}$ {unit[0]}" if number != 0 else fr"$\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}$ {unit[0]}"),
                            ]
        
        elif dimension == 'diameter' and question == 'area':
            # Calculate correct answer (π(d/2)² = πd²/4)
            # First convert to radius (half the diameter)
            radius_numerator, radius_denominator = mixed_to_improper(number, numerator, denominator)
            radius_denominator = radius_denominator * 2  # divide by 2 to get radius
            
            # Square the radius
            squared_num = radius_numerator * radius_numerator
            squared_den = radius_denominator * radius_denominator
            
            # Calculate area = πr²
            answer_number, answer_numerator, answer_denominator = improper_to_mixed(squared_num, squared_den)
            
            # Format correct answer with π
            if answer_numerator == 0:
                answer = fr"${answer_number}\pi$ {unit[1]}²"
            elif answer_number == 0:
                answer = fr"$\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[1]}²"
            else:
                answer = fr"${answer_number}\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[1]}²"
            
            # WRONG ANSWERS
            # Wrong 1: Using πd² (forgetting to divide by 4)
            wrong1_numerator, wrong1_denominator = mixed_to_improper(number, numerator, denominator)
            wrong1_num = wrong1_numerator * wrong1_numerator
            wrong1_den = wrong1_denominator * wrong1_denominator
            wrong1_number, wrong1_numerator, wrong1_denominator = improper_to_mixed(wrong1_num, wrong1_den)
            
            # Wrong 2: Using πd (confusing area and circumference formulas)
            wrong2_numerator, wrong2_denominator = mixed_to_improper(number, numerator, denominator)
            wrong2_number, wrong2_numerator, wrong2_denominator = improper_to_mixed(wrong2_numerator, wrong2_denominator)
            
            # Wrong 3: Using πd/2 (using radius formula but with diameter)
            wrong3_numerator, wrong3_denominator = mixed_to_improper(number, numerator, denominator)
            wrong3_denominator = wrong3_denominator * 2  # divide by 2
            wrong3_number, wrong3_numerator, wrong3_denominator = improper_to_mixed(wrong3_numerator, wrong3_denominator)
            
            wrong_answers = [
                # Using πd² (forgetting to divide by 4)
                fr"${wrong1_number}\pi$ {unit[1]}²" if wrong1_numerator == 0 else 
                    (fr"$\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[1]}²" if wrong1_number == 0 else 
                    fr"${wrong1_number}\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[1]}²"),
                
                # Using πd (confusing area and circumference formulas)
                fr"${wrong2_number}\pi$ {unit[1]}²" if wrong2_numerator == 0 else 
                    (fr"$\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[1]}²" if wrong2_number == 0 else 
                    fr"${wrong2_number}\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[1]}²"),
                
                # Using πd/2 (using radius formula but with diameter)
                fr"${wrong3_number}\pi$ {unit[1]}²" if wrong3_numerator == 0 else 
                    (fr"$\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[1]}²" if wrong3_number == 0 else 
                    fr"${wrong3_number}\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[1]}²"),
            ]
        elif dimension == 'diameter' and question == 'circumference':
            # Calculate correct answer (πd)
            diameter_numerator, diameter_denominator = mixed_to_improper(number, numerator, denominator)
            answer_number, answer_numerator, answer_denominator = improper_to_mixed(diameter_numerator, diameter_denominator)
            
            # Format correct answer with π
            if answer_numerator == 0:
                answer = fr"${answer_number}\pi$ {unit[0]}"
            elif answer_number == 0:
                answer = fr"$\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[0]}"
            else:
                answer = fr"${answer_number}\frac{{{answer_numerator}}}{{{answer_denominator}}}\pi$ {unit[0]}"
            
            # WRONG ANSWERS
            # Wrong 1: Using 2πd (applying radius formula to diameter)
            wrong1_numerator, wrong1_denominator = mixed_to_improper(number, numerator, denominator)
            wrong1_numerator = wrong1_numerator * 2
            wrong1_number, wrong1_numerator, wrong1_denominator = improper_to_mixed(wrong1_numerator, wrong1_denominator)
            
            # Wrong 2: Using πd/2 (dividing by 2 incorrectly)
            wrong2_numerator, wrong2_denominator = mixed_to_improper(number, numerator, denominator)
            wrong2_denominator = wrong2_denominator * 2
            wrong2_number, wrong2_numerator, wrong2_denominator = improper_to_mixed(wrong2_numerator, wrong2_denominator)
            
            # Wrong 3: Using πd² (confusing area and circumference)
            wrong3_numerator, wrong3_denominator = mixed_to_improper(number, numerator, denominator)
            wrong3_numerator = wrong3_numerator * wrong3_numerator
            wrong3_denominator = wrong3_denominator * wrong3_denominator
            wrong3_number, wrong3_numerator, wrong3_denominator = improper_to_mixed(wrong3_numerator, wrong3_denominator)
            
            wrong_answers = [
                # Using 2πd (applying radius formula to diameter)
                fr"${wrong1_number}\pi$ {unit[0]}" if wrong1_numerator == 0 else 
                    (fr"$\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[0]}" if wrong1_number == 0 else 
                    fr"${wrong1_number}\frac{{{wrong1_numerator}}}{{{wrong1_denominator}}}\pi$ {unit[0]}"),
                
                # Using πd/2 (dividing by 2 incorrectly)
                fr"${wrong2_number}\pi$ {unit[0]}" if wrong2_numerator == 0 else 
                    (fr"$\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[0]}" if wrong2_number == 0 else 
                    fr"${wrong2_number}\frac{{{wrong2_numerator}}}{{{wrong2_denominator}}}\pi$ {unit[0]}"),
                
                # Using πd² (confusing area and circumference)
                fr"${wrong3_number}\pi$ {unit[0]}" if wrong3_numerator == 0 else 
                    (fr"$\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[0]}" if wrong3_number == 0 else 
                    fr"${wrong3_number}\frac{{{wrong3_numerator}}}{{{wrong3_denominator}}}\pi$ {unit[0]}"),
            ]
    else:
        if type == 'decimal':
            number = round(random.randint(5,100) * .1, 2)
        else:
            number = random.randint(5,30)

        problem = f"The {dimension} of a circle is {number} {unit[0]}. What is the {question} of the circle in terms of π?"
        if dimension == 'radius' and question == 'area':
            answer = f"{round(number ** 2, 2)} {unit[1]}²"
            wrong_answers = [
                                f"{round(number, 2)}π {unit[1]}²",
                                f"{round(number * 2, 2)}π {unit[1]}²",
                                f"{round((number * 2) ** 2, 2)}π {unit[1]}²"
                            ]
        elif dimension == 'radius' and question == 'circumference':
            answer_value = round(number * 2, 2)
            answer = f"{answer_value}π {unit[1]}"
            wrong_answers = [
                                f"{round(number, 2)}π {unit[1]}",
                                f"{round(number ** 2, 2)}π {unit[1]}",
                                f"{round(2 * (number ** 2), 2)}π {unit[1]}"
                            ]
        elif dimension == 'diameter' and question == 'area':
            answer_value = round((number ** 2) / 4, 2)
            answer = f"{answer_value}π {unit[1]}²"
            wrong_answers = [
                                f"{round(number ** 2, 2)}π {unit[1]}²",
                                f"{round(number, 2)}π {unit[1]}²",
                                f"{round(number / 2, 2)}π {unit[1]}²"
                            ]
        elif dimension == 'diameter' and question == 'circumference':
            # Calculate correct answer (πd)
            answer_value = round(number, 2)
            answer = f"{answer_value}π {unit[1]}"
            wrong_answers = [
                                f"{round(number * 2, 2)}π {unit[1]}",
                                f"{round(number / 2, 2)}π {unit[1]}",
                                f"{round(number ** 2, 2)}π {unit[1]}"
                            ]

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.1, fr"[A] {all_answers[0]}", fontsize=12, family='serif')
    fig.text(0.32, 0.1, fr"[B] {all_answers[1]}", fontsize=12, family='serif')
    fig.text(0.52, 0.1, fr"[C] {all_answers[2]}", fontsize=12, family='serif')
    fig.text(0.72, 0.1, fr"[D] {all_answers[3]}", fontsize=12, family='serif')

    addQuestion(fig, problem)
    
    return saveQuestion(87, fig, correct_letter, answer)

def generate_circle_area_question(questions):
        unique_numbers = random.sample(range(1, 20), 5)

        for rad in unique_numbers:
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

    pi = 3.14
    
    # Add choices at bottom
    area = pi * radius**2
    answer = round(area)
    
    # Generate plausible wrong answers
    wrong_answers = [
        round(pi * radius),
        round(2 * pi * radius),
        round(area - random.randint(5, 10))
    ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
    
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D
        
    problem = f"What is the area of the circle? Use 3.14 for π and round to the nearest whole number."
    addQuestion(fig, problem)
    
    addIntChoices(fig, all_answers, "ft\u00B2")

    cleanAx(ax)

    return saveQuestion(88, fig, correct_letter, answer)

def generate_area_circumference_wp(questions):
        names = [
                    "Evans",
                    "Davis",
                    "Taft",
                    "Perkins",
                    "Kim",
                    "Webb",
                ]

        units = [
                    ["yards", "yard", "yd"],
                    ["feet", "foot", "ft"],
                    ["inches", "inch", "in"],
                    ["meters", "meter", "m"],
                    ["centimeters", "centimeter", "cm"]
                ]

        for _ in range(5):
            # Question options
            # Determine radius or diameter
            dimensions = ['radius', 'diameter']
            # Determine question
            results = ['area', 'circumference']

            name = random.choice(names)
            unit = random.choice(units)
            dimension = random.choice(dimensions)
            question = random.choice(results)
            value = random.randint(10, 400) * .1

            questions += [create_area_circumference_wp(unit, dimension, question, name, value)]

def create_area_circumference_wp(unit, dimension, question, name, value):
    # Create fig that is 7.7 in. wide and 3 in. tall
    fig = plt.figure(figsize=(7.7, 1.25))

    prefix = random.choice(['Mr.', 'Ms.'])

    diameter_area_small = [
                        f"{prefix} {name} made a circular gameboard with a diameter of {intify(value)} {unit[0]}. A layer of paper is going to cover the gameboard. What is the area of the gameboard? Use 3.14 for π and round to the nearest {unit[1]}.",
                    ]
    
    diameter_area_large = [
                        f"{prefix} {name} is spraying grass seed across a lawn. The lawn is in a circular shape with a diameter of {intify(value)} {unit[0]}. What is the area of the lawn? Use 3.14 for π and round to the nearest {unit[1]}.",
                        f"{prefix} {name} is pouring concrete for the floor of a circular building. The planned floor of the building has a diameter of {intify(value)} {unit[0]}. What is the area of the floor? Use 3.14 for π and round to the nearest {unit[1]}."
                    ]

    radius_circumference_small = [
                                f"A market scale has a dial with a needle {intify(value)} {unit[0]} long. How far does the tip of the needle move when it makes one complete rotation? Use 3.14 for π and round to the nearest {unit[1]}.",
                                f"{prefix} {name} is making a circular tablecloth. The tablecloth will be trimmed with a lace strip. Before {prefix} {name} goes to the fabric store, he finds the distance around the edge of the tablecloth. The radius of the tablecloth is {intify(value)} {unit[1]}. What is the distance around the edge of the tablecloth? Use 3.14 for π and round to the nearest inch.",
                                f"A bathroom scale has a dial with a needle {intify(value)} {unit[0]} long. How far does the tip of the needle move when it makes one complete rotation? Use 3.14 for π and round to the nearest {unit[1]}.",
                                f"A clock has a minute hand {intify(value)} {unit[0]} long. How far does the tip of the hand move when it makes one complete rotation? Use 3.14 for π and round to the nearest {unit[1]}.",
                            ]
    
    radius_circumference_large = [
                                f"{prefix} {name} wants to put a string of lights around the outside edge of a Ferris wheel. Before they orders the lights, {prefix} {name} wants to know the distance around the edge of the Ferris wheel. The radius of the wheel is {intify(value)} {unit[1]}. What is the distance around the edge of the Ferris wheel? Use 3.14 for π and round to the nearest {unit[1]}.",
                                f"{prefix} {name} is putting a tile walkway around the edge of their circular fishpond. The radius of the pond is {intify(value)} {unit[0]}. What is the distance around the pond? Use 3.14 for π and round to the nearest {unit[1]}.",
                            ]
    
    radius_area_small = [
                            f"{prefix} {name} is making a clock with a radius of {intify(value)} {unit[0]}. The clock will have a layer of protective coating on it's face. What is the area of the clock face? Use 3.14 for π and round to the nearest {unit[1]}"
                        ]
    
    radius_area_large = [
                            f"A layer of rubber chips is going to be spread over a circular playground. The playground has a radius of {intify(value)} {unit[0]}. What is the area of the playground? Use 3.14 for π and round to the nearest {unit[1]}.",     
                            f"A sprinkler sprays water a distance of {intify(value)} {unit[0]} in a circular pattern. How much area does the sprinkler cover in one complete rotation? Use 3.14 for π and round to the nearest {unit[1]}.",
                        ]

    if unit[2] == 'in' or unit[2] == 'cm':
        if dimension == 'diameter':
            problem = random.choice(diameter_area_small)
            answer = f"{round((value/2) ** 2 * 3.14)} {unit[2]}²"
            wrong_answers = [
                                f"{round(value)} {unit[2]}²",
                                f"{round(value ** 2)} {unit[2]}²",
                                f"{round(value * 3.14)} {unit[2]}²"
                            ]
        else:
            if question == 'circumference':
                # small radius -> circumference
                problem = random.choice(radius_circumference_small)
                answer = f"{round(2 * value * 3.14)} {unit[2]}²"
                wrong_answers = [
                    f"{round(value * 3.14)} {unit[2]}²",
                    f"{round(value ** 2 * 3.14)} {unit[2]}²",
                    f"{round(2 * value)} {unit[2]}²"
                ]
            else:
                #  small radius -> area
                problem = random.choice(radius_area_small)
                answer = f"{round(value ** 2 * 3.14)} {unit[2]}²"
                wrong_answers = [
                    f"{round(2 * value * 3.14)} {unit[2]}²",
                    f"{round((value * 2) ** 2 * 3.14)} {unit[2]}²",
                    f"{round(value ** 2)} {unit[2]}²"
                ]
    else:
        if dimension == 'diameter':
            problem = random.choice(diameter_area_large)
            answer = f"{round((value/2) ** 2 * 3.14)} {unit[2]}²"
            wrong_answers = [
                                f"{round(value)} {unit[2]}²",
                                f"{round(value ** 2)} {unit[2]}²",
                                f"{round(value ** 2 * 3.14)} {unit[2]}²"
                            ]

        else:
            if question == 'circumference':
                # large radius -> circumference
                problem = random.choice(radius_circumference_large)
                answer = f"{round(2 * value * 3.14)} {unit[2]}²"
                wrong_answers = [
                    f"{round(value * 3.14)} {unit[2]}²",
                    f"{round((value * 2) ** 2 * 3.14)} {unit[2]}²",
                    f"{round(2 * value)} {unit[2]}²"
                ]

            else:
                #  large radius -> area
                problem = random.choice(radius_area_large)
                answer = f"{round(value ** 2 * 3.14)} {unit[2]}²"
                wrong_answers = [
                                    f"{round(value)} {unit[2]}²",
                                    f"{round(value ** 2)} {unit[2]}²",
                                    f"{round(value ** 2 * 3.14)} {unit[2]}²"
                                ]

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    addQuestion(fig, problem)

    addStrChoices(fig, all_answers)

    return saveQuestion(89, fig, correct_letter, answer)

def generate_diameter_area_question(questions):
    unique_numbers = random.sample(range(1, 10), 5)

    for rad in unique_numbers:
        # print(f"Generating question with area {rad * rad}")
        questions += [create_diameter_area_question(rad)]

def create_diameter_area_question(radius):
    # Create figure and axis
    fig = plt.figure(1, figsize=(7.7,1))

    fig.patch.set_facecolor('white')

    # Add choices at bottom
    answer = radius * 2
    
    # Generate plausible wrong answers
    wrong_answers = [
        radius,  # Using radius instead of diameter
        radius/2,  # Using circumference
        round(answer - random.randint(1, 2))  # Just wrong
    ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    problem = f"The area of a circle is {radius**2}$\\pi$ cm$^2$. What is the diameter of the circle?"
    addQuestion(fig, problem)

    addIntChoices(fig, all_answers, "cm")

    return saveQuestion(90, fig, correct_letter, answer)
