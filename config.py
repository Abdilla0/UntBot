import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Subjects available
SUBJECTS = {
    'math': '📐 Mathematics',
    'reading': '📖 Reading Literacy',
    'history': '🏛️ History of Kazakhstan',
    'physics': '⚡ Physics',
    'chemistry': '⚗️ Chemistry',
}

# Languages
LANGUAGES = {
    'kk': '🇰🇿 Қазақша',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}