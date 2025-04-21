from backend.registry import register

import random
import math
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from io import BytesIO

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

@register('680271ddb5950060f2045786')
def generate_grade1_q1(questions):
    for _ in range(5):
        start = random.randint(1,117)
        questions += [create_grade1_q1(start)]

def create_grade1_q1(start):
    image_choice = random.randint(0,2)
    images = [
                "./backend/assets/grade1/q1/q1_train.png",
                "./backend/assets/grade1/q1/q1_bike.png",
                "./backend/assets/grade1/q1/q1_skateboard.png"
            ]

    # Create fig that is 7.7 in. wide and 3 in. tall
    if image_choice == 0:
        fig = plt.figure(figsize=(7.7, 2))
        
    else:
        fig = plt.figure(figsize=(7.7, 4))
    # Create ax .1 from left .1 from bottom .6 of the length of fig and .6 of the height of fig
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # # Set limits of ax
    # ax.set_xlim(0, 10)
    # ax.set_ylim(0, 5)
    if image_choice == 0:
        ax.text(390, 135, start, ha='center', va='center', size='x-large', family='serif')
        ax.text(600, 135, start+1, ha='center', va='center', size='x-large', family='serif')
        ax.text(810, 135, start+2, ha='center', va='center', size='x-large', family='serif')
    elif image_choice == 1:
        ax.text(120, 370, start, ha='center', va='center', size='x-large', family='serif')
        ax.text(280, 370, start+1, ha='center', va='center', size='x-large', family='serif')
        ax.text(450, 370, start+2, ha='center', va='center', size='x-large', family='serif')
    else:
        ax.text(70, 350, start-1, ha='center', va='center', size='x-large', family='serif')
        ax.text(170, 350, start, ha='center', va='center', size='x-large', family='serif')
        ax.text(260, 350, start+1, ha='center', va='center', size='x-large', family='serif')
        ax.text(360, 350, start+2, ha='center', va='center', size='x-large', family='serif')

    # Add image to Ax
    image = Image.open(images[image_choice])
    img_array = np.array(image)
    ax.imshow(img_array)


    # Correct answer
    answer = f"{start+3}, {start+4}, {start+5}"

    # Wrong answers
    all_wrong_answers = [
                        f"{start+4}, {start+5}, {start+6}",
                        f"{start+3}, {start+5}, {start+7}",
                        f"{start+4}, {start+6}, {start+8}",
                        f"{start+2}, {start+3}, {start+4}",
                        f"{start+2}, {start+4}, {start+6}"
                    ]
    wrong_answers = random.sample(all_wrong_answers, 3)

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    # Add multiple choice options with proper spacing
    fig.text(0.12, 0.1, fr"[A] {all_answers[0]}", ha='center', va='center', fontsize=12, family='serif')
    fig.text(0.37, 0.1, fr"[B] {all_answers[1]}", ha='center', va='center', fontsize=12, family='serif')
    fig.text(0.62, 0.1, fr"[C] {all_answers[2]}", ha='center', va='center', fontsize=12, family='serif')
    fig.text(0.87, 0.1, fr"[D] {all_answers[3]}", ha='center', va='center', fontsize=12, family='serif')

    problem = f"Count on by 1s. What three numbers come next?"
    addQuestion(fig, problem)

    cleanAx(ax)

    return saveQuestion(1, fig, correct_letter, answer)


@register('680271ddb5950060f2045787')
def generate_grade1_q2(questions):
    for _ in range(1):

        count = random.randint(10,119)

        questions += [create_grade1_q2(count)]

def create_grade1_q2(count):
    fig = plt.figure(figsize=(7.7, 3))
    # ax = fig.add_axes([0.05, .3, .8, .5 ])

    if count <= 10:
        images = [
                    ["./backend/assets/grade1/q2/q2_star.png"],
                    ["./backend/assets/grade1/q2/q2_triangle.png"],
                    ["./backend/assets/grade1/q2/q2_flower.png"],
                    ["./backend/assets/grade1/q2/q2_apple.png"]
                ]
    else:
        images = [
                    ["./backend/assets/grade1/q2/q2_baseball.png", "./backend/assets/grade1/q2/q2_10baseball.png"],
                    ["./backend/assets/grade1/q2/q2_bead.png", "./backend/assets/grade1/q2/q2_10bead.png"],
                    ["./backend/assets/grade1/q2/q2_pencil.png", "./backend/assets/grade1/q2/q2_10pencil.png"],
                ]

    if count <= 10:
        image_path = random.choice(images)
        single_image = Image.open(image_path)
        img_array = np.array(single_image)
        
        # Place individual images
        for i in range(count):
            row = i // 5
            col = i % 5
            x = 0.1 + col * 0.15
            y = 0.6 - row * 0.15
            ax_img = fig.add_axes([x, y, 0.3, 0.3])
            ax_img.imshow(img_array)
            ax_img.axis('off')
    else:
        # Get tens and ones
        count10 = count // 10
        count1 = count % 10
        
        image_paths = random.choice(images)
        single_path, group10_path = image_paths
        
        # Place groups of 10
        for i in range(count10):
            group10_image = Image.open(group10_path)
            group10_array = np.array(group10_image)
            x = 0.1 + i * 0.2
            ax_img = fig.add_axes([x, 0.5, 0.3, 0.3])
            ax_img.imshow(group10_array)
            ax_img.axis('off')
        
        # Place individual items
        if count1 > 0:
            single_image = Image.open(single_path)
            single_array = np.array(single_image)
            
            for i in range(count1):
                x = 0.1 + i * 0.08
                ax_img = fig.add_axes([x, 0.3, 0.1, 0.1])
                ax_img.imshow(single_array)
                ax_img.axis('off')

    fig.text(0,0,count)

@register('680271ddb5950060f2045788')
def generate_grade1_q3(questions):
    print("Hello")

def create_grade1_q3():
    print("Hello")

@register('680271ddb5950060f2045789')
def generate_grade1_q4(questions):
    counts = random.sample(list(range(11,20)), 5)
    for x in counts:
        questions += [create_grade1_q4(x)]


def create_grade1_q4(count):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    question = f"{count}=____________"

    # Answer
    count10 = count//10
    count1 = count%10
    tens_word = "ten" if count10 == 1 else "tens"
    ones_word = "one" if count1 == 1 else "ones"
    answer = f"{count10} {tens_word} and {count1} {ones_word}"

    # Wrong answers
    inverse_tens_word = "ten" if count1 == 1 else "tens"
    inverse_ones_word = "one" if count10 == 1 else "ones"
    all_wrong_answers = [
                        f"{count10+1} tens and {count1} {ones_word}",
                        f"{count10} {tens_word} and {count1+1} ones",
                        f"{count1} {inverse_tens_word} and {count10} {inverse_ones_word}"
                    ]
    
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D


    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.35, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.60, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.85, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(4, fig, correct_letter, answer)

@register('680271ddb5950060f204578a')
def generate_grade1_q5(questions):
    counts = random.sample(list(range(22,99)), 5)
    for x in counts:
        questions += [create_grade1_q5(x)]


def create_grade1_q5(count):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    question = f"{count}=____________"

    # Answer
    count10 = count//10
    count1 = count%10
    tens_word = "ten" if count10 == 1 else "tens"
    ones_word = "one" if count1 == 1 else "ones"
    answer = f"{count10} {tens_word} and {count1} {ones_word}"

    # Wrong answers
    inverse_tens_word = "ten" if count1 == 1 else "tens"
    inverse_ones_word = "one" if count10 == 1 else "ones"
    all_wrong_answers = [
                        f"{count10+1} tens and {count1} {ones_word}",
                        f"{count10} {tens_word} and {count1+1} ones",
                        f"{count1} {inverse_tens_word} and {count10} {inverse_ones_word}"
                    ]
    
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D


    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.35, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.60, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.85, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(5, fig, correct_letter, answer)

@register('680271ddb5950060f204578b')
def generate_grade1_q6(questions):
    counts = random.sample(list(range(10,99)), 5)
    for x in counts:
        questions += [create_grade1_q6(x)]

def create_grade1_q6(count):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    question = f"{count}=____________"

    # Answer
    count10 = count//10
    count1 = count%10
    tens_word = "ten" if count10 == 1 else "tens"
    ones_word = "one" if count1 == 1 else "ones"
    answer = f"{count10} {tens_word} + {count1} {ones_word}"

    # Wrong answers
    inverse_tens_word = "ten" if count1 == 1 else "tens"
    inverse_ones_word = "one" if count10 == 1 else "ones"
    all_wrong_answers = [
                        f"{count10+1} tens + {count1} {ones_word}",
                        f"{count10} {tens_word} + {count1+1} ones",
                        f"{count1} {inverse_tens_word} + {count10} {inverse_ones_word}"
                    ]
    
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.35, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.60, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.85, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(6, fig, correct_letter, answer)

@register('680271ddb5950060f204578c')
def generate_grade1_q7(questions):
    for _ in range(5):

        ten = random.randint(1,9)
        one = random.randint(1,9)

        questions += [create_grade1_q7(ten, one)]

def create_grade1_q7(ten, one):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    tens_word = "ten" if ten == 1 else "tens"
    ones_word = "one" if one == 1 else "ones"

    question = f"{ten} {tens_word} + {one} {ones_word}=____________"

    # Answer
    answer = f"{10*ten + one}"

    # Wrong answers
    wrong_answers = [
                        f"{10*one + ten}",
                        f"{ten+one}",
                        f"{10*ten + one + random.randint(1,10)}"
                    ]
    
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.4, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.55, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.85, 0.85, f"[C] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(7, fig, correct_letter, answer)

@register('680271ddb5950060f204578d')
def generate_grade1_q8(questions):
    for _ in range(5):

        ten = random.randint(1,9)
        one = random.randint(1,9)

        questions += [create_grade1_q7(ten, one)]

def create_grade1_q7(ten, one):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    tens_word = "ten" if ten == 1 else "tens"
    ones_word = "one" if one == 1 else "ones"

    options = [[ten, tens_word, 'ten'], [one, ones_word, 'one']]
    random.shuffle(options)
    question = f"What does the {options[0][0]} mean in {ten}{one}?"


    # Answer
    answer = f"{options[0][0]} {options[0][1]}"

    # Wrong answers
    if options[0][2] == 'ten': #61
        inverse_tens_word = "ten" if one == 1 else "tens"
        inverse_ones_word = "one" if ten == 1 else "ones"
        wrong_answers = [
                            f"{options[0][0]} {inverse_ones_word}",
                            f"{options[0][0]}0 {options[0][1]}",
                        ]
    else: #61
        inverse_tens_word = "ten" if one == 1 else "tens"
        inverse_ones_word = "one" if ten == 1 else "ones"
        wrong_answers = [
                            f"{options[0][0]}0 {inverse_ones_word}",
                            f"{options[0][0]} {inverse_tens_word}"
                        ]
    # All answer choices
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.5, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.65, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.8, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(8, fig, correct_letter, answer)

@register('680271ddb5950060f204578e')
def generate_grade1_q9(questions):
    for _ in range(5):

        a = random.randint(10,90)
        b = random.randint(10,99)

        questions += [create_grade1_q9(a, b)]

def create_grade1_q9(a, b):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    question = f"Which number sentence is true?"

    # Answer
    if a < b:
        answer = f"{a} < {b}"
    elif b < a:
        answer = f"{a} > {b}"
    else:
        answer = f"{a} = {b}"
    
    # All answer choices
    all_answers = [
                    f"{a} < {b}",
                    f"{a} > {b}",
                    f"{a} = {b}"
                    ]
    # random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            question, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.5, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(9, fig, correct_letter, answer)

@register('680271ddb5950060f204578f')
def generate_grade1_q10(questions):
    for _ in range(5):

        ten = random.randint(2,9)
        one = random.randint(2,9)

        questions += [create_grade1_q10(ten, one)]

def create_grade1_q10(ten, one):
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
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

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

    cleanAx(ax)

    return saveQuestion(10, fig, correct_letter, answer)
