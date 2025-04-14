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

        for _ in range(1):
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

            create_question(shape, slice)
        return jsonify({'success' : True})

    except Exception as e:
        return jsonify({'error' : e})

def create_question(shape, slice):
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

    problem = f"A plane is sliced {slice} through this {shape}. What two-dimensional shape could be formed?"
    # Plot question
    fig.text(0.01, .99, problem, 
                ha='left',
                va='top',
                fontsize=12,
                wrap=True,
                family='serif'
            )

    # Add multiple choice options with proper spacing
    fig.text(0.10, 0.1, f"[A] {all_answers[0]}", fontsize=12, family='serif')
    fig.text(0.35, 0.1, f"[B] {all_answers[1]}", fontsize=12, family='serif')
    fig.text(0.60, 0.1, f"[C] {all_answers[2]}", fontsize=12, family='serif')
    fig.text(0.85, 0.1, f"[D] {all_answers[3]}", fontsize=12, family='serif')   
    
    # Clean up
    # Get rid of x and y axis
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.set_zticks([])
    # Get rid of ax border
    for spine in ax.spines.values():
        spine.set_visible(False)
    # # Add grid
    # ax.grid(True, linestyle='-', alpha=0.7)

    fig.savefig('question.png')

    matplotlib.pyplot.close()

    return jsonify({'success' : True})