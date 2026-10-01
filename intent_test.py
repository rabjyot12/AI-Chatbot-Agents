import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

user_input = input("You: ")

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "system",
            "content": """
You are an intent classification system.

Classify the user's message into exactly ONE of these categories:

education
loan
real_estate
communication
unknown

Return ONLY the category name.
Do not explain your answer.
"""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]
)

intent = response.choices[0].message.content.strip().lower()

print("Detected intent:", intent)