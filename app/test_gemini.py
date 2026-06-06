from google import genai
import os
from core.config import settings

client = genai.Client(
    api_key="AIzaSyD5xhVFlzSODY6K4TAw0JICsJdlEbVcqvY"
)


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello"
)

print(response.text)