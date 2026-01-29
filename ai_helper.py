import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

print("🔮 Using Gemini AI")

# ✅ Your working Gemini API key
GEMINI_API_KEY = ""

print(f"🔑 API Key: {GEMINI_API_KEY[:20]}...")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # ✅ Working model name
    model = genai.GenerativeModel('models/gemini-flash-latest')
    print("✅ Gemini AI configured successfully")
except Exception as e:
    print(f"❌ Error: {e}")
    model = None

def clean_response(text: str) -> str:
    """Remove unwanted symbols like $ from AI response"""
    if not text:
        return text
    
    # Remove single $ symbols
    text = text.replace('$', '')
    
    # Remove ** markdown bold (optional - if you want plain text)
    # text = text.replace('**', '')
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def call_ai(prompt: str) -> str:
    """Call Gemini AI"""
    if model is None:
        return "⚠️ AI temporarily unavailable"
    
    try:
        response = model.generate_content(prompt)
        # ✅ Clean the response before returning
        cleaned_text = clean_response(response.text)
        return cleaned_text
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)[:150]}...")
        return "⚠️ AI temporarily unavailable. Please try again."

def explain_topic(topic, subject, language="en"):
    """AI explains a topic"""
    
    lang_map = {
        'en': 'English',
        'ru': 'Russian',
        'kk': 'Kazakh'
    }
    
    prompt = f"""You are a helpful UNT (Unified National Testing) exam tutor for Kazakhstan students.

Explain the topic: "{topic}" in {subject}

Requirements:
- Use {lang_map.get(language, 'English')} language
- Make it simple and clear for high school students
- Include practical examples
- Keep under 300 words
- Be encouraging and supportive
- DO NOT use $ symbols or LaTeX formatting
- Use plain text only

Start your explanation:"""
    
    return call_ai(prompt)

def answer_question(question, subject, language="en"):
    """AI answers student's question"""
    
    lang_map = {
        'en': 'English',
        'ru': 'Russian',
        'kk': 'Kazakh'
    }
    
    prompt = f"""You are a UNT (Unified National Testing) exam preparation assistant for Kazakhstan.

Student's question: {question}
Subject: {subject}

Requirements:
- Answer in {lang_map.get(language, 'English')}
- Be clear, accurate, and helpful
- Include examples if needed
- Keep under 300 words
- Be encouraging
- DO NOT use $ symbols or LaTeX formatting
- Use plain text only

Your answer:"""
    
    return call_ai(prompt)

def explain_answer(question_text, correct_answer, user_answer, language="en"):
    """Explain why an answer is correct"""
    
    lang_map = {
        'en': 'English',
        'ru': 'Russian',
        'kk': 'Kazakh'
    }
    
    is_correct = (str(user_answer).upper().strip() == str(correct_answer).upper().strip())
    
    if is_correct:
        prompt = f"""A student answered correctly on their UNT practice!

Question: {question_text}
Correct answer: {correct_answer}

In {lang_map.get(language, 'English')}, write 2-3 encouraging sentences praising them.

Requirements:
- DO NOT use $ symbols or LaTeX formatting
- Use plain text only
- Keep it simple and encouraging

Your response:"""
    else:
        prompt = f"""Help a UNT student understand their mistake.

Question: {question_text}
Correct answer: {correct_answer}
Student's answer: {user_answer}

In {lang_map.get(language, 'English')}:
- Explain why the correct answer is right
- Be kind and encouraging
- Keep under 150 words
- DO NOT use $ symbols or LaTeX formatting
- Use plain text only

Your explanation:"""
    
    return call_ai(prompt)

if __name__ == "__main__":
    print("\n🧪 Testing Gemini AI for UNT Silkway Bot...\n")
    
    print("1️⃣ Testing explain_topic...")
    result = explain_topic("quadratic equations", "math", "en")
    print(f"✅ Result:\n{result}\n")
    print("=" * 60)
    
    print("\n2️⃣ Testing answer_question...")
    result = answer_question("What is 15% of 200?", "math", "en")
    print(f"✅ Result:\n{result}\n")
    print("=" * 60)
    
    print("\n3️⃣ Testing explain_answer...")
    result = explain_answer("Solve: x² - 5x + 6 = 0", "x = 2, x = 3", "x = 1, x = 6", "en")
    print(f"✅ Result:\n{result}\n")
    
    print("\n✅ All tests complete!")