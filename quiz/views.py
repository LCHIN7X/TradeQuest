from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from groq import Groq

import os
from user.models import User
from flask_login import current_user, login_required
from models import db


quiz = Blueprint('quiz',__name__,template_folder='templates',static_folder='static')
QUIZ_LENGTH = 5
API_KEY = "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"
client = Groq(api_key=API_KEY)

# functions to get quiz questions from API 
def get_questions_from_api():
    questions = []

    for _ in range(QUIZ_LENGTH):
        prompt = """Generate a multiple-choice question regarding finances, with the goal of educating the user and increasing their financial literacy. 
        Format each question like so: 
        Question: <question text> \n A) <option A> \n B) <option B> \n C) <option C> \n Correct answer: <correct answer, including option text>. 
        Only include the question, question selections and the answer, nothing else. 
        Every answer option must be valid and not None."""
        chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": 'system',
                        'content': 'Assume the role of a financial expert.'
                    },
                    {
                        "role": 'user',
                        'content': prompt
                    }
                ],
                model="llama3-8b-8192",
            )
        

        question_content = chat_completion.choices[0].message.content
        question, option_a, option_b, option_c, correct_answer = extract_question_and_answer(question_content)
        questions.append({'question': question, 'option_a' : option_a, 'option_b' : option_b, 'option_c' : option_c, 'answer': correct_answer})

    return questions
        

def extract_question_and_answer(question_content):
    lines = question_content.split('\n')
    question = lines[0]

    options = {}
    correct_answer = None

    for line in lines[1:]:
        if line.strip().startswith('A)'):
            options['option_a'] = line.strip()
        elif line.strip().startswith('B)'):
            options["option_b"] = line.strip()
        elif line.strip().startswith('C)'):
            options["option_c"] = line.strip()
        elif line.strip().startswith('Correct answer:'):
            line = line.strip()
            correct_answer = line.replace('Correct answer:', '').strip()
    
    return question, options.get('option_a'), options.get('option_b'), options.get('option_c'), correct_answer


@quiz.route('/generate-explanation', methods=['POST'])
def generate_explanation():
    data = request.get_json()
    question = data.get('question')
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    option_a = data.get('option_a')
    option_b = data.get('option_b')
    option_c = data.get('option_c')

    explanation_prompt = f"""
    Consider the question below, and the answer options.
    Question: {question}
    Options:
    A) {option_a}
    B) {option_b}
    C) {option_c}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    If the user's answer was wrong, please provide an explanation for why the correct answer is correct and why the user's answer is incorrect.
    If the user's answer was correct, also provide an explanation to elaborate more on why the other 2 answers are incorrect.
    Respond as if you are talking to the user one-on-one. An explanation must be generated for each prompt. Only provide the explanation, nothing else.
    """

    answers_chat = client.chat.completions.create(
                messages=[
                    {
                        "role": 'system',
                        'content': 'Assume the role of a financial expert who is also very good at teaching laymen technical finance knowledge.'
                    },
                    {
                        "role": 'user',
                        'content': explanation_prompt
                    }
                ],
                model="llama3-8b-8192",
            )

    explanation = answers_chat.choices[0].message.content
    return jsonify({'explanation': explanation})

    

# routes for 'quiz' blueprint
@quiz.route('/take_quiz',methods=["GET"])
@login_required
def quiz_page():        
    cash = current_user.cash
    return render_template('quiz.html',cash=cash)


@quiz.route('/get-questions',methods=['GET'])
@login_required
def get_questions():
    questions = get_questions_from_api()
    return jsonify({'questions' : questions}) 


@quiz.route('/increment-cash')
@login_required
def increment_cash():
    current_user.cash += 5.00
    db.session.commit()


    return jsonify({'new_cash' : current_user.cash})