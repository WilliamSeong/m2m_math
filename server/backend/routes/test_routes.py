from flask import Blueprint, jsonify, send_file
from fpdf import FPDF
import io
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from io import BytesIO
import math
import random
from PIL import Image

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

        questions = []

        for _ in range(1):
            a = random.randint(1,9)
            b = random.randint(1,9)
            questions += [create_question(a, b)]

        return jsonify({'success' : True})

    except Exception as e:
        return jsonify({'error' : e})
    
def intify(value):
    return int(value) if (value == int(value)) else round(value, 2)

def cleanAx(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def create_question(a, b):
    fig = plt.figure(figsize=(7.7, .75))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    word_problems = [
                        [f"{a} kittens were in a room. {b} more kittens were added. How many kittens are there now?", 'kittens', 'kitten'],
                        [f"Camilla had {a} toy cars. Ann gave her {b} more. How many toy cars does Camilla have now?", 'toy cars', 'toy car'],
                        [f"A jar had {a} pins in it. Lucy added {b} more. How many pins are in the jar now?", 'pins', 'pin'],
                        [f"{a} dog is in a park. {b} more dogs come over. How many dogs are in the park now?", 'dogs', 'dog'],
                        [f"There were {a} pencils in the box. A boy put in {b} more pencils. How many pencils are in the box now?", 'pencils', 'pencil']
                    ]
    
    choice = random.choice(word_problems)

    problem = choice[0]

    fig.text(0.01, 0.99,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )

    # Answer
    answer = f"{a + b} {choice[1]}"

    # Wrong answers
    wrong_answers = [
                        f"{a+b-1} {choice[2] if a+b-1 == 1 else choice[1]} ",
                        f"{a + b + 1} {choice[1]}",
                        f"{a + b + 2} {choice[1]}",
                    ]
    
    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D
    
    fig.text(0.2, 0.2, f"[A] {all_answers[0]}", ha='center', va='bottom', fontsize=12, family='serif')
    fig.text(0.4, 0.2, f"[B] {all_answers[1]}", ha='center', va='bottom', fontsize=12, family='serif')
    fig.text(0.6, 0.2, f"[C] {all_answers[2]}", ha='center', va='bottom', fontsize=12, family='serif')
    fig.text(0.8, 0.2, f"[D] {all_answers[3]}", ha='center', va='bottom', fontsize=12, family='serif')

    # ax.grid(True, linestyle='--', alpha=0.7)

    # Clean up
    cleanAx(ax)

    fig.savefig('question.png')

    matplotlib.pyplot.close()

    return jsonify({'success' : True})