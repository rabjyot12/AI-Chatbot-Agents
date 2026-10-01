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


#education agent function

def education_agent(data):
    category = data["category"]
    location = data["location"]
    quantity = data["quantity"]

    if category is None:
        print("Are you looking for NEET UG or NEET PG leads?")

        category = input("You: ").lower()

        if "neet ug" in category:
            category = "NEET UG"
        elif "neet pg" in category:
            category = "NEET PG"
        else:
            print("Please specify NEET UG or NEET PG.")
            return

    if location is None:
        print("Which location are you looking for?")
        location = input("You: ")

    if quantity is None:
        print("How many leads do you need?")
        quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", "Education Data")
    print("Category:", category)
    print("Location:", location)
    print("Lead Quantity:", quantity)

    data["category"] = category
    data["location"] = location
    data["quantity"] = quantity

    return data




#loan agent function

def loan_agent():
    print("What type of loan leads are you looking for?")

    loan_type = input("You: ")

    print("Which location are you looking for?")
    location = input("You: ")

    print("How many leads do you need?")
    quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", "Loan Data")
    print("Loan Type:", loan_type)
    print("Location:", location)
    print("Lead Quantity:", quantity)



#real estate agent function

def real_estate_agent():
    print("Are you looking for residential or commercial real estate leads?")

    property_type = input("You: ")

    print("Which location are you interested in?")
    location = input("You: ")

    print("How many leads do you need?")
    quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", "Real Estate Data")
    print("Property Type:", property_type)
    print("Location:", location)
    print("Lead Quantity:", quantity)



#communication agent function

def communication_agent():
    print("Which communication service are you interested in?")
    print("Bulk SMS, RCS SMS, Voice, WhatsApp, IVR, or Toll-Free?")

    service = input("You: ").lower()

    if "bulk sms" in service:
        service = "Bulk SMS"
    elif "rcs" in service:
        service = "RCS SMS"
    elif "voice" in service:
        service = "Voice OBD/IBD"
    elif "whatsapp" in service:
        service = "WhatsApp"
    elif "ivr" in service:
        service = "IVR"
    elif "toll" in service:
        service = "Toll-Free"
    else:
        print("Sorry, I don't recognize that communication service.")
        return

    print("What is the approximate number of customers/recipients?")
    quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", service)
    print("Recipient Quantity:", quantity)



#intent detection function


def detect_intent(user_input):

    if "education" in user_input or "neet" in user_input:
        return "education"

    elif "loan" in user_input:
        return "loan"

    elif "real estate" in user_input or "realestate" in user_input:
        return "real_estate"

    elif (
        "bulk sms" in user_input
        or "rcs" in user_input
        or "voice" in user_input
        or "whatsapp" in user_input
        or "ivr" in user_input
        or "toll free" in user_input
        or "tollfree" in user_input
    ):
        return "communication"

    else:
        return "unknown"


def detect_intent_with_llm(user_input):
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

    return intent



def extract_information(user_input):

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

    result = result.replace("```json", "").replace("```", "").strip()

    data = json.loads(result)

    return data



print("Hello! I am your chatbot.")

while True:
    user_input = input("You: ").lower()

    if "bye" in user_input:
        print("Goodbye!")
        break

    data = extract_information(user_input)

    intent = data["intent"]

    if intent == "education":
        lead = education_agent(data)
        print(lead)

    elif intent == "loan":
        loan_agent()

    elif intent == "real_estate":
        real_estate_agent()

    elif intent == "communication":
        communication_agent()

    elif "hello" in user_input or "hi" in user_input:
        print("Hello! How can I help you today?")

    else:
        print("Sorry, I don't understand your request yet.") 
