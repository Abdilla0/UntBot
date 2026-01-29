# admin_tools/validate_questions.py
"""
Validate question files for UNT Silkway Bot
Updated: 2026-01-29
Supports new topic-based structure with 6 subjects
"""

import json
import sys
import os
from typing import List, Dict, Tuple

def validate_question(question: dict, question_num: int, subject: str, topic: str) -> List[str]:
    """Validate a single question structure and content"""
    errors = []
    
    # Check required fields
    required_fields = [
        'id', 'topic', 
        'question_en', 'question_ru', 'question_kk',
        'options', 'correct',
        'explanation_en', 'explanation_ru', 'explanation_kk'
    ]
    
    for field in required_fields:
        if field not in question:
            errors.append(f"Question {question_num} ({topic}): Missing field '{field}'")
        elif not question[field]:  # Check if field is empty
            errors.append(f"Question {question_num} ({topic}): Empty field '{field}'")
    
    # Validate ID
    if 'id' in question:
        if not isinstance(question['id'], int):
            errors.append(f"Question {question_num} ({topic}): ID must be an integer, got {type(question['id']).__name__}")
    
    # Validate topic matches
    if 'topic' in question and question['topic'] != topic:
        errors.append(f"Question {question_num}: Topic mismatch - declared '{question['topic']}' but in '{topic}' section")
    
    # Validate options (must have exactly A, B, C, D, E)
    if 'options' in question:
        if not isinstance(question['options'], dict):
            errors.append(f"Question {question_num} ({topic}): 'options' must be a dictionary")
        else:
            required_options = ['A', 'B', 'C', 'D', 'E']
            for opt in required_options:
                if opt not in question['options']:
                    errors.append(f"Question {question_num} ({topic}): Missing option '{opt}'")
                elif not question['options'][opt]:  # Check if option is empty
                    errors.append(f"Question {question_num} ({topic}): Option '{opt}' is empty")
    
    # Validate correct answer
    if 'correct' in question:
        if question['correct'] not in ['A', 'B', 'C', 'D', 'E']:
            errors.append(f"Question {question_num} ({topic}): Invalid correct answer '{question['correct']}' (must be A, B, C, D, or E)")
    
    # Validate questions are different in each language (at least somewhat)
    if 'question_en' in question and 'question_ru' in question and 'question_kk' in question:
        if question['question_en'] == question['question_ru'] == question['question_kk']:
            errors.append(f"Question {question_num} ({topic}): All language versions are identical (translations missing?)")
    
    # Check for reasonable text lengths
    if 'question_en' in question:
        if len(question['question_en']) < 10:
            errors.append(f"Question {question_num} ({topic}): Question text seems too short")
        if len(question['question_en']) > 500:
            errors.append(f"Question {question_num} ({topic}): Question text seems too long")
    
    return errors


def validate_subject_file(filepath: str, subject: str) -> Tuple[bool, int, List[str]]:
    """
    Validate an entire subject question file with new structure
    Returns: (is_valid, total_questions, errors)
    """
    print(f"\n{'='*60}")
    print(f"🔍 Validating: {subject.upper()}")
    print(f"{'='*60}")
    print(f"File: {filepath}")
    
    # Check if file exists
    if not os.path.exists(filepath):
        print(f"❌ File not found!")
        return False, 0, [f"File not found: {filepath}"]
    
    # Load JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False, 0, [f"Invalid JSON in {filepath}: {e}"]
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False, 0, [f"Error reading {filepath}: {e}"]
    
    all_errors = []
    
    # Validate root structure
    if 'subject' not in data:
        all_errors.append("Missing 'subject' key at root level")
    elif data['subject'] != subject:
        all_errors.append(f"Subject mismatch: expected '{subject}', got '{data['subject']}'")
    
    if 'metadata' not in data:
        all_errors.append("Missing 'metadata' key")
    else:
        # Validate metadata
        if 'topics' not in data['metadata']:
            all_errors.append("Missing 'topics' in metadata")
        else:
            print(f"\n📚 Topics defined: {len(data['metadata']['topics'])}")
            for topic_key, topic_name in data['metadata']['topics'].items():
                print(f"   • {topic_key}: {topic_name}")
    
    if 'questions' not in data:
        all_errors.append("Missing 'questions' key")
        print(f"\n❌ CRITICAL: No 'questions' array found!")
        return False, 0, all_errors
    
    # Validate questions
    if not isinstance(data['questions'], list):
        all_errors.append("'questions' must be a list/array")
        return False, 0, all_errors
    
    print(f"\n📝 Validating {len(data['questions'])} questions...")
    
    total_questions = len(data['questions'])
    topic_counts = {}
    question_ids = set()
    
    for i, question in enumerate(data['questions'], 1):
        # Count by topic
        topic = question.get('topic', 'unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Check for duplicate IDs
        q_id = question.get('id')
        if q_id in question_ids:
            all_errors.append(f"Question {i}: Duplicate ID {q_id}")
        question_ids.add(q_id)
        
        # Validate question
        errors = validate_question(question, i, subject, topic)
        all_errors.extend(errors)
    
    # Show topic distribution
    print(f"\n📊 Questions per topic:")
    for topic, count in sorted(topic_counts.items()):
        topic_name = data['metadata']['topics'].get(topic, topic)
        print(f"   • {topic_name}: {count} questions")
    
    # Report results
    print(f"\n{'='*60}")
    print(f"📈 VALIDATION RESULTS FOR {subject.upper()}")
    print(f"{'='*60}")
    print(f"Total questions: {total_questions}")
    print(f"Unique topics: {len(topic_counts)}")
    print(f"Errors found: {len(all_errors)}")
    
    if all_errors:
        print(f"\n❌ ERRORS FOUND:")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
        return False, total_questions, all_errors
    else:
        print(f"\n✅ ALL CHECKS PASSED!")
        return True, total_questions, []


def validate_all_subjects(subjects_config: Dict[str, str]) -> bool:
    """Validate all subject files and generate summary"""
    print("\n" + "="*60)
    print("🚀 UNT SILKWAY BOT - QUESTION VALIDATOR")
    print("="*60)
    
    results = {}
    total_questions_all = 0
    all_valid = True
    
    for subject, filepath in subjects_config.items():
        is_valid, question_count, errors = validate_subject_file(filepath, subject)
        results[subject] = {
            'valid': is_valid,
            'questions': question_count,
            'errors': errors
        }
        total_questions_all += question_count
        if not is_valid:
            all_valid = False
    
    # Generate final summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    for subject, result in results.items():
        status = "✅" if result['valid'] else "❌"
        print(f"{status} {subject.upper()}: {result['questions']} questions")
        if not result['valid']:
            print(f"   Errors: {len(result['errors'])}")
    
    print(f"\nTotal questions across all subjects: {total_questions_all}")
    
    if all_valid:
        print("\n" + "="*60)
        print("✅ ALL SUBJECTS VALIDATED SUCCESSFULLY!")
        print("="*60)
        print("✨ Your questions are ready to merge and deploy!")
        return True
    else:
        print("\n" + "="*60)
        print("❌ VALIDATION FAILED!")
        print("="*60)
        print("⚠️  Please fix the errors above before proceeding.")
        return False


if __name__ == "__main__":
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Updated subjects - NO 'reading', ADDED 'biology' and 'geography'
    subjects = {
        'mathematics': os.path.join(project_root, 'question_sources', 'mathematics_questions.json'),
        'physics': os.path.join(project_root, 'question_sources', 'physics_questions.json'),
        'chemistry': os.path.join(project_root, 'question_sources', 'chemistry_questions.json'),
        'biology': os.path.join(project_root, 'question_sources', 'biology_questions.json'),
        'history': os.path.join(project_root, 'question_sources', 'history_questions.json'),
        'geography': os.path.join(project_root, 'question_sources', 'geography_questions.json')
    }
    
    # Allow checking individual subjects via command line
    if len(sys.argv) > 1:
        subject_to_check = sys.argv[1].lower()
        if subject_to_check in subjects:
            print(f"\n🎯 Checking only: {subject_to_check}")
            is_valid, _, _ = validate_subject_file(subjects[subject_to_check], subject_to_check)
            sys.exit(0 if is_valid else 1)
        else:
            print(f"❌ Unknown subject: {subject_to_check}")
            print(f"Available subjects: {', '.join(subjects.keys())}")
            sys.exit(1)
    
    # Validate all subjects
    all_valid = validate_all_subjects(subjects)
    
    sys.exit(0 if all_valid else 1)