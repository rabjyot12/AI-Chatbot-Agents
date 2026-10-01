import os
import json
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
You are a data extraction system for a business chatbot.

Extract the following information from the user's message:

1. intent
2. category
3. location
4. quantity

The intent must be exactly one of:

education
loan
real_estate
communication
unknown

For education:
- category can be NEET UG or NEET PG.

For real estate:
- category can be residential or commercial.

If a piece of information is not provided, use null.

Return ONLY valid JSON.
Do not explain anything.
"""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]
)

result = response.choices[0].message.content

print("RAW RESPONSE:")
print(result)

data = json.loads(result)

print("Intent:", data["intent"])
print("Category:", data["category"])
print("Location:", data["location"])
print("Quantity:", data["quantity"])