import json
import random
import os

# Load questions from JSON file
def load_questions():
    """Load questions from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'questions_bank.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ questions_bank.json not found!")
        return {}
    except Exception as e:
        print(f"⚠️ Error loading questions: {e}")
        return {}

# Load questions at import time
QUESTIONS = load_questions()

def get_question(subject, question_id=None, language='en'):
    """Get a question from the bank"""
    if subject not in QUESTIONS:
        return None
    
    questions = QUESTIONS[subject]
    
    if not questions:
        return None
    
    if question_id is not None:
        for q in questions:
            if q['id'] == question_id:
                return format_question_for_language(q, language)
        return None
    
    # Get random unanswered question
    question = random.choice(questions)
    return format_question_for_language(question, language)

def format_question_for_language(question, language='en'):
    """Format question text based on language"""
    lang_suffix = {
        'en': '_en',
        'ru': '_ru',
        'kk': '_kk'
    }.get(language, '_en')
    
    # Get question text in correct language
    question_key = f'question{lang_suffix}'
    explanation_key = f'explanation{lang_suffix}'
    
    formatted = {
        'id': question['id'],
        'text': question.get(question_key, question.get('question_en', 'Question not available')),
        'options': question['options'],
        'correct': question['correct'],
        'explanation': question.get(explanation_key, question.get('explanation_en', 'Explanation not available'))
    }
    
    return formatted

def format_question(question):
    """Format question for display"""
    if not question:
        return "No questions available"
    
    text = f"❓ **Question:**\n{question['text']}\n\n"
    
    for key, value in question['options'].items():
        text += f"{key}) {value}\n"
    
    text += "\n💡 Type your answer (A, B, C, D, or E):"
    return text

def get_all_subjects():
    """Get list of available subjects"""
    return list(QUESTIONS.keys())

def get_question_count(subject):
    """Get number of questions for a subject"""
    if subject not in QUESTIONS:
        return 0
    return len(QUESTIONS[subject])