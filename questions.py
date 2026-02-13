# questions.py - Load and manage questions
import json
import random
from pathlib import Path

# Map subject names to actual filenames
# IMPORTANT: Both 'math' and 'mathematics' point to same file!
SUBJECT_FILES = {
    'math': 'math_questions.json',                # ✅ Your actual file name
    'mathematics': 'math_questions.json',         # ✅ Alternative name (both work!)
    'physics': 'physics_questions.json',
    'chemistry': 'chemistry_questions.json',
    'biology': 'biology_questions.json',
    'history': 'history_questions.json',
    'geography': 'geography_questions.json'                 # ✅ Your actual filename (no _questions)
}

# Cache for loaded questions
QUESTIONS = {}

def load_questions_from_file(subject):
    """Load questions from JSON file for a subject"""
    try:
        # Get the correct filename
        filename = SUBJECT_FILES.get(subject)
        if not filename:
            print(f"❌ Unknown subject: {subject}")
            print(f"   Available subjects: {list(SUBJECT_FILES.keys())}")
            return None
        
        # Try to load from question_sources folder first
        filepath = Path('question_sources') / filename
        
        if not filepath.exists():
            # Try current directory
            filepath = Path(filename)
        
        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            print(f"   Tried: question_sources/{filename} and {filename}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {filename} ({len(data.get('questions', []))} questions)")
        return data
        
    except Exception as e:
        print(f"❌ Error loading {subject}: {e}")
        return None


def get_topics(subject):
    """Get list of topics for a subject"""
    if subject not in QUESTIONS:
        QUESTIONS[subject] = load_questions_from_file(subject)
    
    if not QUESTIONS[subject]:
        return []
    
    # Get topics from metadata
    topics = QUESTIONS[subject].get('metadata', {}).get('topics', {})
    return list(topics.keys())


def get_question(subject, language='en', topic=None):
    """
    Get a random question for a subject
    
    Args:
        subject: Subject name (math, physics, etc.)
        language: Language code (en, ru, kk)
        topic: Optional topic filter
    
    Returns:
        Question dict with text, options, correct answer, explanation
    """
    # Load questions if not cached
    if subject not in QUESTIONS:
        QUESTIONS[subject] = load_questions_from_file(subject)
    
    if not QUESTIONS[subject]:
        print(f"❌ No questions loaded for subject: {subject}")
        return None
    
    # Get questions array
    questions = QUESTIONS[subject].get('questions', [])
    
    if not questions:
        print(f"❌ No questions found in file for subject: {subject}")
        return None
    
    # Filter by topic if specified
    if topic:
        questions = [q for q in questions if q.get('topic') == topic]
        if not questions:
            print(f"❌ No questions found for topic: {topic}")
            return None
    
    # Pick random question
    question = random.choice(questions)
    
    # Format for the language
    return {
        'id': question['id'],
        'topic': question['topic'],
        'text': question.get(f'question_{language}', question.get('question_en', '')),
        'options': question.get('options', {}),
        'correct': question.get('correct', 'A'),
        'explanation': question.get(f'explanation_{language}', question.get('explanation_en', ''))
    }


def format_question(question):
    """Format question for display"""
    text = f"❓ **Question #{question['id']}**\n\n{question['text']}\n\n"
    
    # Add options
    for option, value in sorted(question['options'].items()):
        text += f"{option}) {value}\n"
    
    return text


if __name__ == "__main__":
    # Test loading
    print("="*60)
    print("TESTING QUESTION LOADER")
    print("="*60)
    print()
    
    subjects = ['math', 'physics', 'chemistry', 'biology', 'history', 'geography']
    
    for subject in subjects:
        print(f"\nTesting: {subject}")
        print("-"*40)
        
        # Load questions
        data = load_questions_from_file(subject)
        if data:
            questions = data.get('questions', [])
            topics = data.get('metadata', {}).get('topics', {})
            print(f"✅ Questions: {len(questions)}")
            print(f"✅ Topics: {list(topics.keys())}")
            
            # Test getting a question
            q = get_question(subject, 'en')
            if q:
                print(f"✅ Sample question:")
                print(f"   ID: {q['id']}")
                print(f"   Topic: {q['topic']}")
                print(f"   Text: {q['text'][:50]}...")
            else:
                print("❌ Could not get sample question")
        else:
            print(f"❌ Failed to load")
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60)