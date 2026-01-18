import google.generativeai as genai

API_KEY = "AIzaSyDasqgRbBOgRRajnH2Rcp9B_Q0rF-WD2dk"

genai.configure(api_key=API_KEY)

print("🔍 Listing all available Gemini models...\n")

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Description: {model.description}")
            print(f"   Methods: {model.supported_generation_methods}")
            print()
except Exception as e:
    print(f"❌ Error: {e}")