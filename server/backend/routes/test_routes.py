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
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test Packet!", align="C")

        question = create_circle_area_question(3, 2)

        add_question_to_pdf(pdf, question)


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
    # Create a single figure with both question text and diagram
    fig = plt.figure(figsize=(8, 6))
    
    # Set up grid: question text at top, diagram below
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 5])
    
    # Question text area
    ax_text = fig.add_subplot(gs[0])
    ax_text.axis('off')
    ax_text.text(0.5, 0.5, f"{question_number}. What is the area of the circle? Use 3.14 for π and round to the nearest whole number.", 
                fontsize=12, ha='center', va='center')
    
    # Circle diagram area
    ax_circle = fig.add_subplot(gs[1], aspect='equal')
    
    # Draw circle
    circle = plt.Circle((0, 0), radius, fill=False)
    ax_circle.add_patch(circle)
    
    # Draw radius line
    ax_circle.plot([0, radius], [0, 0], 'k-')
    ax_circle.plot(0, 0, 'ko', markersize=4)  # Center dot
    
    # Add radius label
    ax_circle.text(radius/2, 0.2, f"{radius} ft", ha='center')
    
    # Set limits and turn off axis
    ax_circle.set_xlim(-radius-1, radius+1)
    ax_circle.set_ylim(-radius-1, radius+1)
    ax_circle.axis('off')
    
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
    
    # Add choices at bottom
    y_pos = -radius-2
    x_positions = [-3*radius/2, -radius/2, radius/2, 3*radius/2]
    
    for i, choice in enumerate(all_answers):
        letter = chr(65 + i)  # A, B, C, D
        ax_circle.text(x_positions[i], y_pos, f"[{letter}]", ha='center')
        ax_circle.text(x_positions[i], y_pos-1, f"{choice} ft²", ha='center')
    
    plt.tight_layout()
    
    # Save to BytesIO
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    img_data.seek(0)
    
    return {
        'image': img_data,
        'correct_answer': correct_letter,
        'correct_value': rounded_area
    }

def add_question_to_pdf(pdf, question):
    # Add the complete question image (includes question number, text, diagram, and choices)
    pdf.image(question['image'], x=10, w=180)
    pdf.ln(10)  # Small space after the question
    return pdf

