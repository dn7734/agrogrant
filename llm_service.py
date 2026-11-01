import os
import httpx
from pydantic import BaseModel

class LLMService:
    def __init__(self):
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.api_key = os.getenv("AQ.Ab8RN6KqUmTdQdN7AWUMwgRt_arRWgTR_tEyxFbo9LcMQVdkEQ")

    async def generate_response(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            return "Вибачте, наразі сервіс генерації відповідей тимчасово недоступний."

