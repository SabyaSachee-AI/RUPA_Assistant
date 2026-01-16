import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Using the 'latest' alias which typically points to 1.5 Flash for stability
model = genai.GenerativeModel('gemini-flash-latest')

try:
    response = model.generate_content("Rupa, confirm you are using the Flash 2.5 engine.")
    print("API Status: SUCCESS ✅")
    print("Rupa's Response:", response.text)
except Exception as e:
    print("API Status: FAILED ❌")
    print(f"Error: {e}")