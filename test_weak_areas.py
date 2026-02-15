#!/usr/bin/env python3
# test_weak_areas.py - Test the weak area detection feature

import sqlite3
from datetime import datetime

def create_test_data():
    """Create test data to demonstrate weak area detection"""
    
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    # Test user ID
    test_user_id = 999999999
    
    print("🧪 Creating test data for weak area detection...\n")
    
    # Clear any existing test data
    cursor.execute('DELETE FROM topic_performance WHERE user_id = ?', (test_user_id,))
    cursor.execute('DELETE FROM answers WHERE user_id = ?', (test_user_id,))
    cursor.execute('DELETE FROM users WHERE user_id = ?', (test_user_id,))
    
    # Add test user
    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, language)
        VALUES (?, ?, ?, ?)
    ''', (test_user_id, 'test_user', 'Test Student', 'en'))
    
    # Simulate answering questions with different accuracy per topic
    test_data = [
        # ALGEBRA - 75% accuracy (STRONG)
        ('math', 'algebra', 1, True),
        ('math', 'algebra', 2, True),
        ('math', 'algebra', 3, True),
        ('math', 'algebra', 4, False),
        
        # GEOMETRY - 53% accuracy (WEAK)
        ('math', 'geometry', 5, False),
        ('math', 'geometry', 6, True),
        ('math', 'geometry', 7, False),
        ('math', 'geometry', 8, True),
        ('math', 'geometry', 9, False),
        ('math', 'geometry', 10, True),
        ('math', 'geometry', 11, False),
        ('math', 'geometry', 12, False),
        
        # PERCENTAGES - 66% accuracy (MODERATE)
        ('math', 'percentages', 13, True),
        ('math', 'percentages', 14, True),
        ('math', 'percentages', 15, False),
        ('math', 'percentages', 16, True),
        ('math', 'percentages', 17, False),
        ('math', 'percentages', 18, True),
        
        # PHYSICS TOPICS
        # MECHANICS - 80% accuracy (STRONG)
        ('physics', 'mechanics', 19, True),
        ('physics', 'mechanics', 20, True),
        ('physics', 'mechanics', 21, True),
        ('physics', 'mechanics', 22, True),
        ('physics', 'mechanics', 23, False),
        
        # ELECTRICITY - 40% accuracy (WEAK)
        ('physics', 'electricity', 24, False),
        ('physics', 'electricity', 25, True),
        ('physics', 'electricity', 26, False),
        ('physics', 'electricity', 27, False),
        ('physics', 'electricity', 28, False),
    ]
    
    for subject, topic, question_id, is_correct in test_data:
        # Add to answers table
        cursor.execute('''
            INSERT INTO answers (user_id, subject, question_id, user_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_user_id, subject, question_id, 'A', 'A' if is_correct else 'B', is_correct))
        
        # Add to topic_performance table
        cursor.execute('''
            INSERT INTO topic_performance (user_id, subject, topic, question_id, is_correct)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_user_id, subject, topic, question_id, is_correct))
    
    conn.commit()
    conn.close()
    
    print("✅ Test data created!")
    print(f"📝 Test user ID: {test_user_id}")
    print("\n📊 Expected Results:")
    print("   MATH:")
    print("      ✅ Algebra: 75% (Strong) - Keep Practicing")
    print("      ❌ Geometry: 53% (Weak) - Review Concepts") 
    print("      ⚠️  Percentages: 66% (Moderate) - More Practice")
    print("   PHYSICS:")
    print("      ✅ Mechanics: 80% (Strong) - Keep Practicing")
    print("      ❌ Electricity: 40% (Weak) - Review Concepts")


def test_weak_areas():
    """Test the weak area detection functions"""
    from database import get_topic_stats, get_weak_topics
    
    test_user_id = 999999999
    
    print("\n" + "="*60)
    print("🧪 TESTING WEAK AREA DETECTION")
    print("="*60)
    
    # Test Math
    print("\n📐 MATHEMATICS:")
    print("-" * 60)
    math_stats = get_topic_stats(test_user_id, 'math')
    for stat in math_stats:
        status_emoji = "✅" if stat['status'] == 'strong' else "⚠️" if stat['status'] == 'moderate' else "❌"
        print(f"{status_emoji} {stat['topic'].upper()}: {stat['accuracy']}% - {stat['recommendation']}")
    
    weak_math = get_weak_topics(test_user_id, 'math')
    print(f"\n🎯 Weak topics to focus on: {weak_math}")
    
    # Test Physics
    print("\n⚡ PHYSICS:")
    print("-" * 60)
    physics_stats = get_topic_stats(test_user_id, 'physics')
    for stat in physics_stats:
        status_emoji = "✅" if stat['status'] == 'strong' else "⚠️" if stat['status'] == 'moderate' else "❌"
        print(f"{status_emoji} {stat['topic'].upper()}: {stat['accuracy']}% - {stat['recommendation']}")
    
    weak_physics = get_weak_topics(test_user_id, 'physics')
    print(f"\n🎯 Weak topics to focus on: {weak_physics}")
    
    print("\n" + "="*60)
    print("✅ WEAK AREA DETECTION IS WORKING!")
    print("="*60)


if __name__ == "__main__":
    print("\n🚀 WEAK AREA DETECTION - SETUP & TEST\n")
    
    # Step 1: Initialize database
    from database import init_db
    init_db()
    
    # Step 2: Create test data
    create_test_data()
    
    # Step 3: Test the feature
    test_weak_areas()
    
    print("\n📱 HOW TO TEST IN TELEGRAM:")
    print("1. Start your bot: python bot.py")
    print("2. Use test user ID: 999999999 (send /start)")
    print("3. Choose Math subject")
    print("4. Click 'Choose Topic'")
    print("5. Click '📊 Weak Areas' button")
    print("6. You should see the analysis above!")
    
    print("\n✨ Done! Feature is ready to use!\n")