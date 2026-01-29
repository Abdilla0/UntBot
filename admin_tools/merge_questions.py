# admin_tools/merge_questions.py
"""
Merge all subject question files into main questions_bank.json
Updated: 2026-01-29
Supports: Mathematics, Physics, Chemistry, Biology, History, Geography
"""

import json
import os
from datetime import datetime
from pathlib import Path

def merge_all_questions():
    """Merge all subject question files into main questions_bank.json"""
    
    # Updated subjects (removed 'reading', added biology & geography)
    subjects = {
        'mathematics': './question_sources/math_questions.json',
        'physics': './question_sources/physics_questions.json',
        'chemistry': './question_sources/chemistry_questions.json',
        'biology': './question_sources/biology_questions.json',
        'history': './question_sources/history_questions.json',
        'geography': './question_sources/geography_questions.json'
    }
    
    merged_data = {}
    total_questions = 0
    subject_summary = {}
    
    print("=" * 60)
    print("🔄 MERGING QUESTION FILES")
    print("=" * 60)
    print()
    
    for subject, filepath in subjects.items():
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                print(f"⚠️  {subject.upper()}: File not found at {filepath}")
                print(f"   Skipping...")
                continue
            
            # Load the JSON file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if 'questions' not in data:
                print(f"❌ {subject.upper()}: Invalid structure (missing 'questions' key)")
                continue
            
            # Store subject data
            merged_data[subject] = data
            
            # Count questions
            question_count = len(data['questions'])
            total_questions += question_count
            
            # Get topics info
            topics = data.get('metadata', {}).get('topics', {})
            topic_count = len(topics)
            
            # Store summary
            subject_summary[subject] = {
                'questions': question_count,
                'topics': topic_count,
                'topic_list': list(topics.keys()) if topics else []
            }
            
            print(f"✅ {subject.upper()}")
            print(f"   Questions: {question_count}")
            print(f"   Topics: {topic_count}")
            if topics:
                print(f"   Topic List: {', '.join(topics.keys())}")
            print()
                
        except FileNotFoundError:
            print(f"⚠️  {subject.upper()}: File not found, skipping")
            print()
        except json.JSONDecodeError as e:
            print(f"❌ {subject.upper()}: Invalid JSON - {e}")
            print()
        except Exception as e:
            print(f"❌ {subject.upper()}: Error - {e}")
            print()
    
    if not merged_data:
        print("❌ No questions were merged. Check your source files!")
        return
    
    # Save merged file
    output_path = '../questions_bank.json'
    
    # Create directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # Create detailed metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'total_questions': total_questions,
        'total_subjects': len(merged_data),
        'subjects': list(merged_data.keys()),
        'subject_details': subject_summary,
        'version': '2.0',
        'structure': 'topic-based',
        'languages': ['en', 'ru', 'kk']
    }
    
    metadata_path = '../questions_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("=" * 60)
    print("📊 MERGE SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully merged {total_questions} questions")
    print(f"📚 Subjects included: {len(merged_data)}")
    print()
    
    for subject, info in subject_summary.items():
        print(f"   • {subject.upper()}: {info['questions']} questions, {info['topics']} topics")
    
    print()
    print(f"💾 Output saved to: {output_path}")
    print(f"📋 Metadata saved to: {metadata_path}")
    print("=" * 60)


def validate_question_structure(filepath):
    """Validate that a question file has the correct structure"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required keys
        required_keys = ['subject', 'metadata', 'questions']
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"
        
        # Check metadata structure
        if 'topics' not in data['metadata']:
            return False, "Missing 'topics' in metadata"
        
        # Check questions structure
        if not isinstance(data['questions'], list):
            return False, "'questions' must be a list"
        
        # Check each question
        for i, q in enumerate(data['questions']):
            required_q_keys = ['id', 'topic', 'question_en', 'question_ru', 'question_kk', 
                             'options', 'correct', 'explanation_en', 'explanation_ru', 'explanation_kk']
            for key in required_q_keys:
                if key not in q:
                    return False, f"Question {i+1} missing key: {key}"
        
        return True, "Valid structure"
    
    except Exception as e:
        return False, str(e)


def generate_statistics():
    """Generate detailed statistics from questions_bank.json"""
    try:
        with open('../questions_bank.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n" + "=" * 60)
        print("📈 DETAILED STATISTICS")
        print("=" * 60)
        print()
        
        for subject, subject_data in data.items():
            questions = subject_data.get('questions', [])
            topics = subject_data.get('metadata', {}).get('topics', {})
            
            print(f"🎯 {subject.upper()}")
            print(f"   Total Questions: {len(questions)}")
            print(f"   Total Topics: {len(topics)}")
            print()
            
            # Count questions per topic
            topic_counts = {}
            for q in questions:
                topic = q.get('topic', 'unknown')
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            print("   Questions per topic:")
            for topic, count in sorted(topic_counts.items()):
                topic_name = topics.get(topic, topic)
                print(f"      • {topic_name}: {count} questions")
            
            print()
        
    except FileNotFoundError:
        print("❌ questions_bank.json not found. Run merge first!")
    except Exception as e:
        print(f"❌ Error generating statistics: {e}")


if __name__ == "__main__":
    print("\n🚀 UNT Silkway Bot - Question Merger\n")
    
    # Validate structure before merging (optional)
    print("🔍 Validating question files...")
    subjects_to_check = {
        'mathematics': './question_sources/mathematics_questions.json',
        'physics': './question_sources/physics_questions.json',
        'chemistry': './question_sources/chemistry_questions.json',
        'biology': './question_sources/biology_questions.json',
        'history': './question_sources/history_questions.json',
        'geography': './question_sources/geography_questions.json'
    }
    
    validation_passed = True
    for subject, filepath in subjects_to_check.items():
        if os.path.exists(filepath):
            valid, message = validate_question_structure(filepath)
            if valid:
                print(f"   ✅ {subject}: {message}")
            else:
                print(f"   ❌ {subject}: {message}")
                validation_passed = False
        else:
            print(f"   ⚠️  {subject}: File not found")
    
    print()
    
    if not validation_passed:
        print("⚠️  Some files have validation errors. Continue anyway? (y/n)")
        response = input().lower()
        if response != 'y':
            print("❌ Merge cancelled.")
            exit()
    
    # Run merge
    merge_all_questions()
    
    # Generate statistics
    generate_statistics()
    
    print("\n✨ Done!\n")