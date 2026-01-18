import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

print("🔮 Using Gemini AI")

# ✅ Your working Gemini API key
GEMINI_API_KEY = "AIzaSyDasqgRbBOgRRajnH2Rcp9B_Q0rF-WD2dk"

print(f"🔑 API Key: {GEMINI_API_KEY[:20]}...")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # ✅ Working model name
    model = genai.GenerativeModel('models/gemini-flash-latest')
    print("✅ Gemini AI configured successfully")
except Exception as e:
    print(f"❌ Error: {e}")
    model = None

def call_ai(prompt: str) -> str:
    """Call Gemini AI"""
    if model is None:
        return "⚠️ AI temporarily unavailable"
    
    try:
        response = model.generate_content(prompt)
        return response.text
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

Start your explanation:"""
    
    return call_ai(prompt)

def answer_question(question, subject, language="en"):
    """AI answers student's question"""
    
    lang_map = {
        'en': 'English',
        'ru': 'Russian',
        'kk': 'Kazakh'
    }
    
    prompt = f"""You are a UNT exam preparation assistant.

Student's question: {question}
Subject: {subject}

Requirements:
- Answer in {lang_map.get(language, 'English')}
- Be clear, accurate, and helpful
- Include examples if needed
- Keep under 300 words
- Be encouraging

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
        prompt = f"""A student answered correctly!

Question: {question_text}
Correct answer: {correct_answer}

In {lang_map.get(language, 'English')}, write 2-3 encouraging sentences praising them.

Your response:"""
    else:
        prompt = f"""Help a student understand their mistake.

Question: {question_text}
Correct answer: {correct_answer}
Student's answer: {user_answer}

In {lang_map.get(language, 'English')}:
- Explain why the correct answer is right
- Be kind and encouraging
- Keep under 150 words

Your explanation:"""
    
    return call_ai(prompt)

if __name__ == "__main__":
    print("\n🧪 Testing Gemini AI...\n")
    
    print("1️⃣ Testing explain_topic...")
    result = explain_topic("photosynthesis", "biology", "en")
    print(f"✅ Result:\n{result}\n")
    print("=" * 60)
    
    print("\n2️⃣ Testing answer_question...")
    result = answer_question("What is photosynthesis?", "biology", "en")
    print(f"✅ Result:\n{result}\n")
    print("=" * 60)
    
    print("\n3️⃣ Testing explain_answer...")
    result = explain_answer("What is 2+2?", "4", "5", "en")
    print(f"✅ Result:\n{result}\n")
    
    print("\n✅ All tests complete!")