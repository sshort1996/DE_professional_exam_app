import streamlit as st
import csv
import json
import random
import textwrap
from bs4 import BeautifulSoup

def _create_session():
    
    # Initialize counters for correct and incorrect answers
    session_vars = {
        'questions':[],
        'correct_count': 0,
        'incorrect_count': 0,
        'attempted': [],
        'initial_read': True,
        'question_file_path': None
    }

    for key, var in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = var


def _space_lines(string):
    split_string = string.split('\n')
    result = []
    for line in split_string:
        if len(line) <= 80:
            result.append(line)
        else:
            wrapped_lines = textwrap.wrap(line, width=80)
            result.extend(wrapped_lines)
    return '\n'.join(result)


def _render_questions(questions, index=False):
    
    # Iterate over each question
    for i, question in enumerate(questions):
        
        try: 
            answers = [BeautifulSoup(str(html), 'html.parser').get_text() for html in question[1]]
            sanitised_answers = sanitised_answers = [answer.replace("(Correct)", "") if "(Correct)" in answer else answer for answer in answers]
            correct_ans = list(set(sanitised_answers).difference(answers))[0]
        except Exception as err:
            print(f'Error: {err}, html: {question[1]}')
        

        if question is not None:
            if index is False:
                st.title(f"Question {i+1}")
            else: 
                st.title(f"Question {index+1}")

            # Check if the question has been attempted
            if i in [index for _, index in st.session_state['attempted']]:
                # Apply grey color using HTML/CSS
                st.markdown(
                    f"<style>.question-{i} {{ color: grey; }}</style>",
                    unsafe_allow_html=True
                )
            
            # Grey out submit button and radio button if the question has been attempted
            if i in [index for _, index in st.session_state['attempted']]:
                button_text = "Question Attempted"
                button_disabled = True
                radio_disabled = True
            else:
                button_text = f'Submit#{i + 1}'
                button_disabled = False
                radio_disabled = False
            
            # print(f'question: {question[0]}')
            # st.markdown()
            st.markdown(question[0][0], unsafe_allow_html=True)
            
            # Show multiple choices as radio buttons
            selected_choice = st.radio("Select your answer:", 
                                       options=sanitised_answers, 
                                       disabled=radio_disabled, 
                                       key=f"radio_{i}_{index}")
            
            # Check if the selected choice is correct or incorrect
            if st.button(button_text, 
                         key=f"submit_{i}_{index}", 
                         disabled=button_disabled):
                if selected_choice == correct_ans:
                    st.write("You chose correctly!")
                    st.session_state['correct_count'] += 1
                else:
                    st.write("You chose incorrectly!")
                    st.session_state['incorrect_count'] += 1
                    st.write(f'correct answer is:\n \n{correct_ans}')

                st.session_state['attempted'].append((selected_choice, i))
                st.write(f"Correct count: {st.session_state['correct_count']}, Incorrect count: {st.session_state['incorrect_count']}")
                st.write(f"{st.session_state['correct_count']}/{st.session_state['incorrect_count']+st.session_state['correct_count']}")

                # write explanation to screen
                st.markdown('## Explanation')
                try:
                    st.markdown(f'<div style="background-color: grey; padding: 10px; border-radius: 5px;">{question[2][0]}</div>', unsafe_allow_html=True)
                except IndexError:
                    print('No explanation given in html')


def read_html(question_file_path):
    file_path = f'{question_file_path}.html'  # Replace with your file path
    with open(file_path, 'r', encoding='utf-8') as file:
        response = file.read()

    soup = BeautifulSoup(response, "html.parser")
    forms = soup.find_all('form', class_='mc-quiz-question--container--3GZ4h')
    return forms

def parse_questions(forms):
    html = []
    for form in forms:
        question = form.find_all('div', class_='ud-text-bold mc-quiz-question--question-prompt--2_dlz rt-scaffolding')
        answer  = form.find_all('div', class_='mc-quiz-answer--answer-inner--3WH_P')
        explanation = form.find_all('div', class_="mc-quiz-question--explanation--Q5KHQ")
        # print(f'question: {question}')
        # print(f'answer: {answer}')
        # print(f'explanation: {explanation}')
        html.append((question, answer, explanation))
    return html

def st_question(html_text, num):
    st.markdown(f'## Question {num+1}')
    st.markdown(html_text[0][0], unsafe_allow_html=True)
    for option in html_text[1]:
        st.markdown(option, unsafe_allow_html=True)

_create_session()

# select which question set to use
st.session_state['question_file_path'] = st.selectbox('Select question set', [None, 'questions1', 'questions2', 'questions3', 'all'])
st.write(f'Using test set: {st.session_state["question_file_path"]}')

# select which question set to use
st.session_state['num_questions'] = st.selectbox('Select size of question set', [None] + list(range(1, 181)))
html = []
if st.session_state['question_file_path'] and st.session_state['num_questions']:
    if st.session_state['initial_read']:

        # with open("questions.json") as f:
        #     questions = json.load(f)
        if st.session_state['question_file_path'] == 'all':
            for path in ['questions1', 'questions2', 'questions3']:
                forms = read_html(path)
                html.extend(parse_questions(forms))
                # st.write(f'all html: {html}')
        else:
            forms = read_html(st.session_state['question_file_path'])
            html = parse_questions(forms)
        st.write(f'size of html: {len(html)}')
        # for index, question in enumerate(html):
        #     st_question(question, index)

        # Process and format the strings
        # formatted_strings = [textwrap.fill(string, width=80) for string in questions['question']]

        html = random.sample(html, k = st.session_state['num_questions'])
        print(f'len(html): {len(html)}')
        st.session_state['questions'] = html

        st.session_state['initial_read'] = False
    else: 
        html = st.session_state['questions']

    _render_questions(html)

    # Summary section
    st.title("Summary")
    st.write("Here are the incorrect questions and their answers:")
    if len(st.session_state['attempted'])==st.session_state['num_questions']:
        Score = f'''
            {st.session_state['correct_count']}/
            {len(st.session_state['attempted'])}
            ={round((st.session_state['correct_count']/len(st.session_state['attempted'])*100.0), 2)}%
        '''
        st.markdown(f'<div style="background-color: red; padding: 10px; border-radius: 5px;">{Score}</div>', unsafe_allow_html=True)

    # Iterate over attempted questions to find incorrect ones
    for selected_choice, question_index in st.session_state['attempted']:
        question = html[question_index][0]

        answers = [BeautifulSoup(str(html), 'html.parser').get_text() for html in html[question_index][1]]
        sanitised_answers = sanitised_answers = [answer.replace("(Correct)", "") if "(Correct)" in answer else answer for answer in answers]
        correct_ans = list(set(sanitised_answers).difference(answers))[0]

        if selected_choice != correct_ans:
            answers_text = f"""
            <h2>Question {question_index + 1}:
            \n> {question[0]}  
            \n> Your answer: {selected_choice}   
            \n> Correct answer: {correct_ans}
            """

            json_mistakes = {
                "Question": str(question[0]),
                "Given_answer": str(selected_choice),
                "Correct_answer": str(correct_ans)
            }

            # Check if question exists in mistakes.json
            question_exists = False

            if st.button("Log results (Don't click me I'm Broken)", key=f"Log_results_{question_index}"):
                with open('mistakes.json', 'r') as file:
                    data = json.load(file)
                    for mistake in data['mistakes']:
                        if mistake['Question'] == str(question[0]):
                            question_exists = True
                            break

                # If question does not exist, append json_mistakes to mistakes.json
                if not question_exists:
                    with open('mistakes.json', 'w') as file:
                        data['mistakes'].append(json_mistakes)
                        json.dump(data, file)

            st.markdown(f'<div style="background-color: grey; padding: 10px; border-radius: 5px;">{answers_text}</div>', unsafe_allow_html=True)
