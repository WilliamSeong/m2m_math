from flask import Blueprint, jsonify, send_file
from fpdf import FPDF
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

        unique = random.sample(range(0, 20), 1)

        for _ in range(5):
            a = random.randint(1,5)
            if a <= 5:
                b = random.randint(a, 10)
                c = random.randint(1,10)
            else:
                b = 1
                c = random.randint(a, 10)


            question = create_question(a, b, c)

    except Exception as e:
        return jsonify({'error' : e})

def create_question(a, b, c):
    # Create figure and axis

    # Create fig that is 7.7 in. wide and 3 in. tall
    if a > b:
        fig = plt.figure(figsize=(7.7,2))
    else:
        fig = plt.figure(figsize=(7.7,3))

    # Add axes that is 0.1 from left, 0.2 from top, 0.7 width of fig and .5 heigh of fig
    ax = fig.add_axes([0.1, 0.2, 0.7, .5 ])

    # Set limits of ax
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3.5)

    # Question options
    questions = [
                    "What is the actual length of the entire dock?",
                    "What is the actual width of the dock's walkway?",
                    "What is the actual length of the dock's walkway?"
                ]

    # Plot question
    fig.text(0.05, 0.8, f"A catalog has a scale drawing of a floating dock. The dock is a regular octagon attached to a rectangular walkway. The scale drawing has a scale of 1 inch?", ha='left', fontsize=12, wrap=True)

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.1, f"[A]", fontsize=12, family='Helvetica')
    fig.text(0.32, 0.1, f"[B]", fontsize=12, family='Helvetica')
    fig.text(0.52, 0.1, f"[C]", fontsize=12, family='Helvetica')
    fig.text(0.72, 0.1, f"[D]", fontsize=12, family='Helvetica')

    # Clean up
    # Get rid of x and y axis
    # ax.set_xticks([])
    # ax.set_yticks([])
    # Get rid of ax border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # Add grid
    ax.grid(True, linestyle='-', alpha=0.7)


    fig.savefig('question.png')

    return jsonify({'success' : True})