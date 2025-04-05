from flask import Blueprint, jsonify, send_file
from fpdf import FPDF
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import math
import random

# Create a blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route("/1")
def test():
    print("Generating pdf with latex")
    return jsonify({"message": "Test received"})

@test_bp.route("/2")
def test2():
    print("Test 2 request received")
    return jsonify({"message": "Test 2 received"})

@test_bp.route("/pdf")
def pdf():
    try:
        pdf = FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test Packet!", align="C")

        unique_numbers = random.sample(range(0, 20), 5)

        for i, rad in enumerate(unique_numbers):
            question = create_circle_area_question(rad, i)
            # add_question_to_pdf(pdf, question)

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


def create_circle_area_question(radius, question_number):
    # Create figure and axis
    fig = plt.figure(figsize=(8.5,2.5))

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
    fig.text(0.05, 0.8, f"{question_number}. The area of a circle is {radius**2}$\pi$ cm$^2$. What is the diameter of the circle?", fontsize=12)

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.4, f"[A] {all_answers[0]} cm", fontsize=12, family='Helvetica')
    fig.text(0.32, 0.4, f"[B] {all_answers[1]} cm", fontsize=12, family='Helvetica')
    fig.text(0.52, 0.4, f"[C] {all_answers[2]} cm", fontsize=12, family='Helvetica')
    fig.text(0.72, 0.4, f"[D] {all_answers[3]} cm", fontsize=12, family='Helvetica')

    # Remove axes ticks and labels for a cleaner look, if desired
    # ax.set_xticks([])
    # ax.set_yticks([])
    # for spine in ax.spines.values():
    #     spine.set_visible(False)

    plt.axis('off')

    fig.savefig('diameter.png')


    # # Save to BytesIO
    # img_data = BytesIO()
    # plt.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
    # plt.close(fig)
    # img_data.seek(0)
    
    # return {
    #     'image': img_data,
    #     'correct_answer': correct_letter,
    #     'correct_value': diameter
    # }

    return jsonify({'success' : True})

# def add_question_to_pdf(pdf, question):

#     # Calculate width (8.5 inches minus 1-inch total margins)
#     page_width = pdf.w  # Total page width in points (1 inch = 72 points)
#     # print(f"page width: {page_width}")
#     margin = 12.7  # 0.5 inch = 36 points
#     usable_width = page_width - (2 * margin)

#     # Add the complete question image (includes question number, text, diagram, and choices)
#     pdf.image(question['image'], x=margin, w=usable_width)
#     pdf.ln(10)  # Small space after the question
#     return pdf

