import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('unt_master.db')
cursor = conn.cursor()

# Set your last practice to YESTERDAY
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

cursor.execute('''
    UPDATE users 
    SET last_practice_date = ?, current_streak = 1
    WHERE telegram_id = 7842634855
''', (yesterday,))

conn.commit()
conn.close()

print(f"✅ Set your last practice to {yesterday}")
print("🔥 Now answer a question in Telegram - you'll see 2-day streak!")