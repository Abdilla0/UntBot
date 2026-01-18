import sqlite3
from datetime import datetime

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'en',
            registration_date TEXT,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            last_active TEXT
        )
    ''')
    
    # User answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            question_id INTEGER,
            user_answer TEXT,
            correct_answer TEXT,
            is_correct BOOLEAN,
            answered_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def add_user(telegram_id, username, first_name):
    """Add new user to database"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users 
        (telegram_id, username, first_name, registration_date, last_active)
        VALUES (?, ?, ?, ?, ?)
    ''', (telegram_id, username, first_name, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def update_user_activity(telegram_id):
    """Update last active time"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET last_active = ? WHERE telegram_id = ?
    ''', (datetime.now().isoformat(), telegram_id))
    
    conn.commit()
    conn.close()

def save_answer(user_id, subject, question_id, user_answer, correct_answer, is_correct):
    """Save user's answer"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_answers 
        (user_id, subject, question_id, user_answer, correct_answer, is_correct, answered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, subject, question_id, user_answer, correct_answer, is_correct, datetime.now().isoformat()))
    
    # Update user stats
    cursor.execute('''
        UPDATE users 
        SET total_questions = total_questions + 1,
            correct_answers = correct_answers + ?
        WHERE telegram_id = ?
    ''', (1 if is_correct else 0, user_id))
    
    conn.commit()
    conn.close()

def get_user_stats(telegram_id):
    """Get user statistics"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_questions, correct_answers FROM users WHERE telegram_id = ?
    ''', (telegram_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        total, correct = result
        percentage = (correct / total * 100) if total > 0 else 0
        return {
            'total': total,
            'correct': correct,
            'percentage': round(percentage, 1)
        }
    return None

def set_user_language(telegram_id, language):
    """Set user's preferred language"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET language = ? WHERE telegram_id = ?
    ''', (language, telegram_id))
    
    conn.commit()
    conn.close()

def get_user_language(telegram_id):
    """Get user's preferred language"""
    conn = sqlite3.connect('unt_master.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT language FROM users WHERE telegram_id = ?
    ''', (telegram_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 'en'