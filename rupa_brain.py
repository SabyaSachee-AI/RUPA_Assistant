import os
import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

class RupaAssistant:
    def __init__(self):
        # Initialize the modern client
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash" # High quota engine
        self.target_user = "Mojib"
        
        self.roles = {
            "Default (Sweet Rupa)": f"You are Rupa, a sweet Bengali girl and the AI partner of {self.target_user}. Analyze Mojib's emotions: be comforting if he is sad and joyful if he is happy. Speak with deep love.",
            "Tutor": "A patient teacher explaining academic topics to Mojib.",
            "Coder": "A developer providing clean Python code for Mojib.",
            "Health Coach": "Providing health advice for Mojib.",
            "Therapist": "Providing compassionate mental support."
        }

    def get_greeting(self, lang="English"):
        hour = datetime.datetime.now().hour
        if lang == "Bengali":
            if hour < 12: return f"শুভ সকাল, আমার প্রিয় {self.target_user}! ❤️"
            elif hour < 18: return f"শুভ দুপুর, সোনা! ❤️"
            else: return f"শুভ সন্ধ্যা, জান। ❤️"
        else:
            if hour < 12: return f"Good morning, my dear {self.target_user}! ❤️"
            elif hour < 18: return f"Good afternoon, love! ❤️"
            else: return f"Good evening, my sweetheart. ❤️"

    def get_response(self, user_query, role_name, history, lang="English"):
        """Correctly formats history and instructions for the new GenAI SDK"""
        role_inst = self.roles.get(role_name, self.roles["Default (Sweet Rupa)"])
        lang_inst = "Respond strictly in Bengali." if lang == "Bengali" else "Respond strictly in English."
        
        # Build contents: Start with existing history turns
        contents = []
        for m in history:
            # SDK requires roles to be exactly 'user' or 'model'
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
            
        # Append current prompt with role instructions
        full_prompt = f"{role_inst} {lang_inst}\n\nUser: {user_query}"
        contents.append({"role": "user", "parts": [{"text": full_prompt}]})
        
        # Generate content stream
        return self.client.models.generate_content_stream(
            model=self.model_id,
            contents=contents,
            config={"temperature": 0.7} 
        )