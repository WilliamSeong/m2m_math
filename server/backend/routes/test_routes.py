from flask import Blueprint, jsonify, send_file
from fpdf import FPDF
import io
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

        for _ in range(1):

            ten = random.randint(2,9)
            one = random.randint(2,9)

            create_question(ten, one)
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


def create_question(ten, one):

    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    ten_word = 'ten' if ten == 1 else 'tens'
    one_word = 'one' if one == 1 else 'ones'
    minus_ten_word = 'ten' if ten - 1 == 1 else 'tens'

    choice = random.randint(0,1)
    
    questions = [f"{ten} {ten_word} + {one} {one_word} = _____ + {one+10} ones", f"{ten} {ten_word} + {one} {one_word} = {ten-1} {minus_ten_word} + _____"]

    # Answer choices
    if choice == 0:
        answer = f"{ten - 1} {minus_ten_word}"
        wrong_answers = [
                            f"{ten + 10} {minus_ten_word}",
                            f"{ten + one} {minus_ten_word}",
                            f"{ten - 1 + random.randint(1,2)} {minus_ten_word}"
                        ]
    else:
        answer = f"{one+10} ones"
        wrong_answers = [
                            f"{one+1} ones",
                            f"{one+11} ones",
                            f"{one - 1} {'one' if one-1 == 1 else 'ones'}"
                        ]

    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # # Find index of correct answer
    # correct_index = all_answers.index(answer)
    # correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            questions[choice], 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.45, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.6, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.75, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[C] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    # Clean up
    cleanAx(ax)

    fig.savefig('question.png')

    matplotlib.pyplot.close()

    return jsonify({'success' : True})