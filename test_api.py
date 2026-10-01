import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

messages = [
    {
        "role": "system",
        "content":"""
You are a business chatbot for a company that provides:
- Bulk SMS and RCS SMS
- Voice OBD/IBD
- IVR and Toll-Free numbers
- WhatsApp integration
- Education leads such as NEET UG and NEET PG
- Loan leads
- Real Estate leads

Your job is to understand what service the user is interested in and
ask short, relevant questions to collect the information needed for
that service.

Do not give long marketing strategies or unrelated advice.
Keep responses concise and focused on collecting the user's requirements.

For education leads, ask whether they need NEET UG or NEET PG,
their target location, and the number of leads required.

For loan leads, ask the loan type, location, and number of leads.

For real estate leads, ask whether they need residential or
commercial leads, the location, and number of leads.

For communication services, identify whether they need Bulk SMS,
RCS SMS, Voice, WhatsApp, IVR, or Toll-Free services and ask
appropriate basic requirements.

If the user's request is unclear, ask what service they are
interested in.
"""
    }
]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        print("Bot: Goodbye!")
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages
    )

    assistant_message = response.choices[0].message.content

    messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    print("Bot:", assistant_message)

print("Model:", response.model)
print(response.choices[0].message.content)