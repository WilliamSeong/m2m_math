from backend.registry import register

import random
import math
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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

@register('68066870b5950060f20457d9')
def generate_grade1_q11(questions):
    for _ in range(5):

        ten = random.randint(2,9)
        one = random.randint(2,9)

        questions += [create_grade1_q11(ten, one)]

def create_grade1_q11(ten, one):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    choice = random.randint(0,1)
    questions = [
                    f"{ten*10} + {one} = _____ + {one+10}",
                    f"_____ + {one} = {ten*10} + {one+10}",
                    f"{ten*10} + {one} = {(ten-1)*10} + _____",
                    f"{ten*10} + _____ = {(ten-1)*10} + {one}"
                ]

    # Answer choices
    if choice == 0 or choice == 1:
        answer = f"{(ten - 1)*10}"
        wrong_answers = [
                            f"{(ten + 1)*10}",
                            f"{(ten)*10}",
                            f"{(ten + 2)*10}"
                        ]
    else:
        answer = f"{one+10}"
        wrong_answers = [
                            f"{one + 1}",
                            f"{one + 11}",
                            f"{one - 1}"
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

    return saveQuestion(11, fig, correct_letter, answer)

@register('680668c7b5950060f20457db')
def generate_grade1_q12(questions):
    for _ in range(5):

        options = random.sample(list(range(1, 10)), 2)
        a, b = options

        questions += [create_grade1_q12(a, b)]

def create_grade1_q12(a, b):
    fig = plt.figure(figsize=(7.7, 3))
    ax = fig.add_axes([0.15, .2, .8, .5 ])
    # ax.set_aspect('equal')
    
    # Problem
    problem = f"Which picture shows {a} + {b}?"

    # Answer choices
    # Set the vertical positions for each number line
    line_positions = [0.4, -0.2, -0.8]  # Top, middle, bottom lines

    # Draw the three number lines
    for i, pos in enumerate(line_positions):
        # Draw the horizontal line
        ax.axhline(y=pos, color='black', linestyle='-', linewidth=2)
        
        # Create custom ticks for each line
        if i == 0:  # Top line
            ticks = np.arange(0, 21)  # Ticks at even numbers
        elif i == 1:  # Middle line
            ticks = np.arange(0, 21)  # Ticks at all integers
        else:  # Bottom line
            ticks = np.arange(0, 21)  # Ticks at multiples of 5
        
        # Add tick marks on each line
        for tick in ticks:
            ax.plot([tick, tick], [pos-0.05, pos+0.05], color='black', linewidth=1)
            ax.text(tick, pos-0.2, str(tick), ha='center', va='top')

    # Add sample hopping dotted lines
    answer = {'from': a, 'to': a+b, 'y_pos': line_positions[0], 'color': 'black'}
    wrong_answers = [
        {'from': b, 'to': b+b, 'y_pos': line_positions[1], 'color': 'black'},
        {'from': a, 'to': b, 'y_pos': line_positions[2], 'color': 'black'}
    ]

    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)

    for hop in all_answers:
        for interval in range(min(hop['from'], hop['to']), max(hop['from'], hop['to'])):
            x_hop = np.linspace(interval, interval+1, 100)
            y_hop = hop['y_pos'] + 0.2 * np.sin(np.linspace(0, np.pi, 100))
            ax.plot(x_hop, y_hop, color='black', linestyle='--', linewidth=1.5)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.1, 0.64, f"[A]", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.1, 0.46, f"[B]", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.1, 0.27, f"[C]", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(12, fig, correct_letter, answer)

@register('680668e7b5950060f20457dc')
def generate_grade1_q13(questions):
    for _ in range(5):
        a = random.randint(1,9)
        b = random.randint(1,9)
        questions += [create_grade1_q13(a, b)]

def create_grade1_q13(a, b):
    fig = plt.figure(figsize=(7.7, 2))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    if a + b > 10:
        image = Image.open('./backend/assets/grade1/q13/q13_line.png')
    else:
        image = Image.open('./backend/assets/grade1/q13/q13_blocks.png')

    # Problem
    img_array = np.array(image)
    ax.imshow(img_array)
    problem = f"Which picture shows {a} + {b}?"

    # Answer
    answer = f"{a + b}"

    # Wrong answers
    all_wrong_answers = [
                        f"{max(a,b) - min(a,b)}",
                        f"{a + b + 1}",
                        f"{a + b - 1}",
                    ]
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.2, 0.3, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.4, 0.3, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.6, 0.3, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(13, fig, correct_letter, answer)

@register('68066900b5950060f20457dd')
def generate_grade1_q14(questions):
    for _ in range(5):
        a = random.randint(1,19)
        b = random.randint(1,19)
        questions += [create_grade1_q14(max(a,b), min(a, b))]

def create_grade1_q14(a, b):
    fig = plt.figure(figsize=(7.7, 2))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    if a + b > 10:
        image = Image.open('./backend/assets/grade1/q13/q13_line.png')
    else:
        image = Image.open('./backend/assets/grade1/q13/q13_blocks.png')

    # Problem
    img_array = np.array(image)
    ax.imshow(img_array)
    problem = f"Which picture shows {a} - {b}?"

    # Answer
    answer = f"{a - b}"

    # Wrong answers
    all_wrong_answers = [
                        f"{a + b}",
                        f"{a - b + 1}",
                        f"{a - b + 2}",
                    ]
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.2, 0.3, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.4, 0.3, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.6, 0.3, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(14, fig, correct_letter, answer)

@register('6806691eb5950060f20457de')
def generate_grade1_q15(questions):
    for _ in range(5):
        values = random.sample(list(range(1,20)), 2)
        a, b = values
        questions += [create_grade1_q15(max(a, b), min(a, b))]

def create_grade1_q15(a, b):
    fig = plt.figure(figsize=(7.7, 2))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    problem = f"What number is missing?"
    example1 = f"_____ + {b} = {a}"
    example2 = f"{a} – {b} = _____"
    fig.text(.05, .65, example1)
    fig.text(.05, .45, example2)


    # Answer
    answer = f"{a - b}"

    # Wrong answers
    all_wrong_answers = [
                        f"{(a - b - 1) if a-b > 1 else a-b+3}",
                        f"{a - b + 1}",
                        f"{a - b + 2}",
                    ]
    wrong_answers = random.sample(all_wrong_answers, 2)

    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D

    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.4, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.6, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.8, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(15, fig, correct_letter, answer)

@register('6806693eb5950060f20457df')
def generate_grade1_q16(questions):
    for _ in range(5):
        values = random.sample(list(range(1,9)), 2)
        a, b = values
        questions += [create_grade1_q16(a, b)]

def create_grade1_q16(a, b):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    problem = f"{a} + {b} = "
    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )

    # Answer
    answer = f"{a + b}"

    # Wrong answers
    wrong_answers = [
                        f"{a+b-1}",
                        f"{a + b + 1}",
                        f"{a + b + 2}",
                    ]
    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D
    
    fig.text(0.3, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.5, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[D] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(16, fig, correct_letter, answer)

@register('6806696cb5950060f20457e0')
def generate_grade1_q17(questions):
    for _ in range(5):
        values = random.sample(list(range(1,9)), 2)
        a, b = values
        questions += [create_grade1_q17(a, b)]

def create_grade1_q17(a, b):
    fig = plt.figure(figsize=(7.7, .5))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    problem_top = f"{a}"
    problem_bottom = f"+   {b}"

    fig.text(0.1, 0.85,
            problem_top, 
            ha='right',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.1, 0.55,
        problem_bottom, 
        ha='right',
        va='top',
        fontsize=12,
        wrap=True,
        family='serif'
    )

    line = Line2D([0.04, 0.11], [0.25, 0.25], linewidth=1, color='black')
    fig.add_artist(line)

    # Answer
    answer = f"{a + b}"

    # Wrong answers
    wrong_answers = [
                        f"{a+b-1}",
                        f"{a + b + 1}",
                        f"{a + b + 2}",
                    ]
    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)
    
    fig.text(0.3, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.5, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[D] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(17, fig, correct_letter, answer)

@register('68066990b5950060f20457e2')
def generate_grade1_q18(questions):
    for _ in range(5):
        values = random.sample(list(range(1,9)), 2)
        a, b = values
        questions += [create_grade1_q18(max(a, b), min(a, b))]

def create_grade1_q18(a, b):
    fig = plt.figure(figsize=(7.7, .25))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    problem = f"{a} - {b} = "
    fig.text(0.01, 0.85,
            problem, 
            ha='left',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )

    # Answer
    answer = f"{a - b}"

    # Wrong answers
    wrong_answers = [
                        f"{a-b-1 if a-b > 1 else a-b+3}",
                        f"{a - b + 1}",
                        f"{a - b + 2}",
                    ]
    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)  # Convert to A, B, C, D
    
    fig.text(0.3, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.5, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[D] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(18, fig, correct_letter, answer)

@register('680669a5b5950060f20457e3')
def generate_grade1_q19(questions):
    for _ in range(5):
        values = random.sample(list(range(1,9)), 2)
        a, b = values
        questions += [create_grade1_q19(max(a,b), min(a,b))]

def create_grade1_q19(a, b):
    fig = plt.figure(figsize=(7.7, .5))
    ax = fig.add_axes([0.05, .3, .8, .5 ])

    # Problem
    problem_top = f"{a}"
    problem_bottom = f"–   {b}"

    fig.text(0.1, 0.85,
            problem_top, 
            ha='right',
            va='top',
            fontsize=12,
            wrap=True,
            family='serif'
        )
    
    fig.text(0.1, 0.55,
        problem_bottom, 
        ha='right',
        va='top',
        fontsize=12,
        wrap=True,
        family='serif'
    )

    line = Line2D([0.04, 0.11], [0.25, 0.25], linewidth=1, color='black')
    fig.add_artist(line)

    # Answer
    answer = f"{a - b}"

    # Wrong answers
    wrong_answers = [
                        f"{a-b-1 if a-b > 1 else a-b+3}",
                        f"{a - b + 1}",
                        f"{a - b + 2}",
                    ]
    # All answers
    all_answers = wrong_answers + [answer]
    random.shuffle(all_answers)
        
    # Find index of correct answer
    correct_index = all_answers.index(answer)
    correct_letter = chr(65 + correct_index)
    
    fig.text(0.3, 0.85, f"[A] {all_answers[0]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.5, 0.85, f"[B] {all_answers[1]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.7, 0.85, f"[C] {all_answers[2]}", ha='center', va='top', fontsize=12, family='serif')
    fig.text(0.9, 0.85, f"[D] {all_answers[3]}", ha='center', va='top', fontsize=12, family='serif')

    cleanAx(ax)

    return saveQuestion(19, fig, correct_letter, answer)

@register('680669c3b5950060f20457e4')
def generate_grade1_q20(questions):
    for _ in range(5):
        a = random.randint(1,9)
        b = random.randint(1,9)
        questions += [create_grade1_q20(a, b)]

def create_grade1_q20(a, b):
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

    cleanAx(ax)

    return saveQuestion(20, fig, correct_letter, answer)
