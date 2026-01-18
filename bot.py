import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from config import TELEGRAM_BOT_TOKEN, SUBJECTS, LANGUAGES
from database import (init_db, add_user, update_user_activity, save_answer, 
                      get_user_stats, set_user_language, get_user_language)
from ai_helper import explain_topic, answer_question, explain_answer
from questions import get_question, format_question, QUESTIONS
from translations import t, TRANSLATIONS

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_LANGUAGE, CHOOSING_SUBJECT, WAITING_ANSWER, ASKING_QUESTION = range(4)

# User session data
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    
    # Add user to database
    add_user(user.id, user.username, user.first_name)
    
    # Language selection keyboard
    keyboard = [
        [KeyboardButton("🇰🇿 Қазақша"), KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇬🇧 English")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        t('welcome', 'en'),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return CHOOSING_LANGUAGE

async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose language"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Map choice to language code
    lang_map = {
        "🇰🇿 Қазақша": 'kk',
        "🇷🇺 Русский": 'ru',
        "🇬🇧 English": 'en'
    }
    
    language = lang_map.get(text, 'en')
    
    # Store in session AND database
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['language'] = language
    
    # Save to database
    set_user_language(user_id, language)
    
    # Subject selection keyboard with translated subjects
    keyboard = [
        [KeyboardButton(t('subject_math', language)), KeyboardButton(t('subject_reading', language))],
        [KeyboardButton(t('subject_history', language)), KeyboardButton(t('subject_physics', language))],
        [KeyboardButton(t('subject_chemistry', language))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        t('choose_subject', language),
        reply_markup=reply_markup
    )
    
    return CHOOSING_SUBJECT

async def subject_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose subject"""
    text = update.message.text
    user_id = update.effective_user.id
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Map translated subjects back to subject codes
    subject_map = {}
    for lang in ['en', 'ru', 'kk']:
        subject_map[t('subject_math', lang)] = 'math'
        subject_map[t('subject_reading', lang)] = 'reading'
        subject_map[t('subject_history', lang)] = 'history'
        subject_map[t('subject_physics', lang)] = 'physics'
        subject_map[t('subject_chemistry', lang)] = 'chemistry'
    
    subject = subject_map.get(text)
    
    if not subject:
        await update.message.reply_text(t('choose_subject', language))
        return CHOOSING_SUBJECT
    
    # Store in session
    user_sessions[user_id]['subject'] = subject
    
    # Menu keyboard with translations
    keyboard = [
        [KeyboardButton(t('btn_practice', language)), KeyboardButton(t('btn_explain', language))],
        [KeyboardButton(t('btn_ask', language)), KeyboardButton(t('btn_progress', language))],
        [KeyboardButton(t('btn_change_subject', language))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        t('subject_chosen', language, subject=text),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return WAITING_ANSWER

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu selections"""
    text = update.message.text
    user_id = update.effective_user.id
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Check against all language versions of buttons
    button_actions = {
        'practice': [t('btn_practice', 'en'), t('btn_practice', 'ru'), t('btn_practice', 'kk')],
        'explain': [t('btn_explain', 'en'), t('btn_explain', 'ru'), t('btn_explain', 'kk')],
        'ask': [t('btn_ask', 'en'), t('btn_ask', 'ru'), t('btn_ask', 'kk')],
        'progress': [t('btn_progress', 'en'), t('btn_progress', 'ru'), t('btn_progress', 'kk')],
        'change': [t('btn_change_subject', 'en'), t('btn_change_subject', 'ru'), t('btn_change_subject', 'kk')],
        'next': [t('btn_next', 'en'), t('btn_next', 'ru'), t('btn_next', 'kk')],
        'menu': [t('btn_menu', 'en'), t('btn_menu', 'ru'), t('btn_menu', 'kk')]
    }
    
    if text in button_actions['practice']:
        return await start_practice(update, context)
    elif text in button_actions['explain']:
        return await ask_for_topic(update, context)
    elif text in button_actions['ask']:
        return await ask_for_question(update, context)
    elif text in button_actions['progress']:
        return await show_progress(update, context)
    elif text in button_actions['change'] or text in button_actions['menu']:
        return await start(update, context)
    elif text in button_actions['next']:
        return await start_practice(update, context)
    else:
        # Might be an answer to a question
        return await check_answer(update, context)

async def start_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start practice questions"""
    user_id = update.effective_user.id
    subject = user_sessions.get(user_id, {}).get('subject', 'math')
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Get question in user's language
    question = get_question(subject, language=language)
    
    if not question:
        await update.message.reply_text(t('no_questions', language))
        return WAITING_ANSWER
    
    # Store current question
    user_sessions[user_id]['current_question'] = question
    
    # Send question
    await update.message.reply_text(
        format_question(question),
        parse_mode='Markdown'
    )
    
    return WAITING_ANSWER

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user's answer"""
    user_id = update.effective_user.id
    user_answer = update.message.text.upper().strip()
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    if user_answer not in ['A', 'B', 'C', 'D', 'E']:
        return await handle_free_text(update, context)
    
    question = user_sessions.get(user_id, {}).get('current_question')
    
    if not question:
        await update.message.reply_text(t('start_practice_first', language))
        return WAITING_ANSWER
    
    correct_answer = question['correct']
    is_correct = (user_answer == correct_answer)
    
    # Save to database
    subject = user_sessions[user_id].get('subject', 'math')
    save_answer(user_id, subject, question['id'], user_answer, correct_answer, is_correct)
    
    # Get AI explanation
    ai_explanation = explain_answer(
        question['text'],
        question['options'][correct_answer],
        question['options'].get(user_answer, user_answer),
        language
    )
    
    # Build response
    emoji = "🎉" if is_correct else "❌"
    result_text = t('correct' if is_correct else 'incorrect', language)
    
    response = f"{emoji} **{result_text}**\n\n"
    response += f"✅ {question['explanation']}\n\n"
    response += f"📖 **AI:**\n{ai_explanation}"
    
    # Get stats
    stats = get_user_stats(user_id)
    if stats:
        response += f"\n\n{t('your_stats', language, **stats)}"
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Offer next question
    keyboard = [[KeyboardButton(t('btn_next', language)), KeyboardButton(t('btn_menu', language))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(t('ready_more', language), reply_markup=reply_markup)
    
    return WAITING_ANSWER

async def ask_for_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user what topic to explain"""
    language = user_sessions.get(update.effective_user.id, {}).get('language', 'en')
    await update.message.reply_text(t('ask_topic', language))
    return ASKING_QUESTION

async def ask_for_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user their question"""
    language = user_sessions.get(update.effective_user.id, {}).get('language', 'en')
    await update.message.reply_text(t('ask_question', language))
    return ASKING_QUESTION

async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle topic explanation or question"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    subject = user_sessions.get(user_id, {}).get('subject', 'general')
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Try to explain or answer
    if len(user_text) > 100:
        # Longer text = question
        response = answer_question(user_text, subject, language)
    else:
        # Short text = topic to explain
        response = explain_topic(user_text, subject, language)
    
    await update.message.reply_text(response)
    
    return WAITING_ANSWER

async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    language = user_sessions.get(user_id, {}).get('language', 'en')
    stats = get_user_stats(user_id)
    
    if not stats or stats['total'] == 0:
        await update.message.reply_text(t('no_stats', language))
        return WAITING_ANSWER
    
    # Calculate performance emoji
    if stats['percentage'] >= 80:
        emoji = "⭐⭐⭐⭐⭐"
    elif stats['percentage'] >= 60:
        emoji = "⭐⭐⭐⭐"
    elif stats['percentage'] >= 40:
        emoji = "⭐⭐⭐"
    else:
        emoji = "⭐⭐"
    
    response = f"{t('progress_title', language)}\n\n"
    response += f"{t('overall_stats', language)}\n"
    response += f"{t('total_questions', language, total=stats['total'])}\n"
    response += f"{t('correct_answers', language, correct=stats['correct'])}\n"
    response += f"{t('accuracy', language, percentage=stats['percentage'])} {emoji}\n\n"
    response += f"{t('keep_practicing', language)}"
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    return WAITING_ANSWER

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    user_id = update.effective_user.id
    language = user_sessions.get(user_id, {}).get('language', 'en')
    
    help_text = t('welcome', language)
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Start the bot"""
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_chosen)],
            CHOOSING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, subject_chosen)],
            WAITING_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)],
            ASKING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    
    # Start bot
    print("🚀 Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()