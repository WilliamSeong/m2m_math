from flask import Blueprint, jsonify, send_file
from fpdf import FPDF
import io

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


        for _ in range(1):
            # Question options
            # Determine radius or diameter
            dimensions = ['radius', 'diameter']
            # Determine question
            questions = ['area', 'circumference']

            name = random.choice(names)
            unit = random.choice(units)
            dimension = random.choice(dimensions)
            question = random.choice(questions)
            value = random.randint(10, 400) * .1

            create_question(unit, dimension, question, name, value)
        return jsonify({'success' : True})

    except Exception as e:
        return jsonify({'error' : e})
    
def intify(value):
    return int(value) if (value == int(value)) else round(value, 2)

def create_question(unit, dimension, question, name, value):
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
        
    # # Find index of correct answer
    # correct_index = all_answers.index(answer)
    # correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.97,
                problem, 
                ha='left',
                va='top',
                fontsize=12,
                wrap=True,
                family='serif'
            )

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.1, fr"[A] {all_answers[0]}", fontsize=12, family='serif')
    fig.text(0.32, 0.1, fr"[B] {all_answers[1]}", fontsize=12, family='serif')
    fig.text(0.52, 0.1, fr"[C] {all_answers[2]}", fontsize=12, family='serif')
    fig.text(0.72, 0.1, fr"[D] {all_answers[3]}", fontsize=12, family='serif')
    
    # Clean up
    # Get rid of x and y axis
    # ax.set_xticks([])
    # ax.set_yticks([])
    # ax.set_zticks([])
    # Get rid of ax border
    # for spine in ax.spines.values():
    #     spine.set_visible(False)
    # # Add grid
    # ax.grid(True, linestyle='-', alpha=0.7)

    fig.savefig('question.png')

    matplotlib.pyplot.close()

    return jsonify({'success' : True})