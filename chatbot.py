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

def loan_agent(data):

    category = data["category"]
    location = data["location"]
    quantity = data["quantity"]

    if category is not None and category.lower() == "loan":
        category = None

    if category is None:
        print("What type of loan leads are you looking for?")
        category = input("You: ")

    if location is None:
        print("Which location are you looking for?")
        location = input("You: ")

    if quantity is None:
        print("How many leads do you need?")
        quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", "Loan Data")
    print("Loan Type:", category)
    print("Location:", location)
    print("Lead Quantity:", quantity)

    data["category"] = category
    data["location"] = location
    data["quantity"] = quantity

    return data



#real estate agent function

def real_estate_agent(data):

    category = data["category"]
    location = data["location"]
    quantity = data["quantity"]

    if category is not None and category.lower() == "real estate":
        category = None

    if category is None:
        print("Are you looking for residential or commercial real estate leads?")
        category = input("You: ")

    if location is None:
        print("Which location are you interested in?")
        location = input("You: ")

    if quantity is None:
        print("How many leads do you need?")
        quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", "Real Estate Data")
    print("Property Type:", category)
    print("Location:", location)
    print("Lead Quantity:", quantity)

    data["category"] = category
    data["location"] = location
    data["quantity"] = quantity

    return data



#communication agent function

def communication_agent(data):

    category = data["category"]
    quantity = data["quantity"]

    if category is None:
        print("Which communication service are you interested in?")
        print("Bulk SMS, RCS SMS, Voice, WhatsApp, IVR, or Toll-Free?")

        category = input("You: ").lower()

        if "bulk sms" in category:
            category = "Bulk SMS"
        elif "rcs" in category:
            category = "RCS SMS"
        elif "voice" in category:
            category = "Voice OBD/IBD"
        elif "whatsapp" in category:
            category = "WhatsApp"
        elif "ivr" in category:
            category = "IVR"
        elif "toll" in category:
            category = "Toll-Free"
        else:
            print("Sorry, I don't recognize that communication service.")
            return

    if quantity is None:
        print("What is the approximate number of customers/recipients?")
        quantity = input("You: ")

    print("\nHere is the information I collected:")
    print("Service:", category)
    print("Recipient Quantity:", quantity)

    data["category"] = category
    data["quantity"] = quantity

    return data



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

                    Extract exactly these fields from the user's message:

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

                    CATEGORY RULES:

                    For education:
                    - NEET UG -> category = "NEET UG"
                    - NEET PG -> category = "NEET PG"

                    For loan:
                    - Extract only the loan type.
                    - Example: "I need personal loan leads" -> category = "Personal Loan"
                    - Example: "I need home loan leads" -> category = "Home Loan"
                    - Example: "I need business loan leads" -> category = "Business Loan"
                    - Do not put the full user message in category.

                    For real_estate:
                    - Residential property -> category = "Residential"
                    - Commercial property -> category = "Commercial"

                    For communication:
                    - If the user mentions "Bulk SMS", category MUST be "Bulk SMS".
                    - If the user mentions "RCS" or "RCS SMS", category MUST be "RCS SMS".
                    - If the user mentions "Voice", "Voice OBD", or "Voice OBD/IBD", category MUST be "Voice OBD/IBD".
                    - If the user mentions "WhatsApp", category MUST be "WhatsApp".
                    - If the user mentions "IVR", category MUST be "IVR".
                    - If the user mentions "Toll-Free" or "Toll Free", category MUST be "Toll-Free".

                    LOCATION RULE:
                    - Extract only the location name.
                    - If no location is given, use null.

                    QUANTITY RULE:
                    - Extract the requested number of leads or recipients.
                    - If no quantity is given, use null.

                    If any information is not provided, use null.
                    Do not invent missing information.
                    Do not copy the entire user message into a field.

                    Return ONLY valid JSON.
                    Do not use Markdown.
                    Do not use ```json code blocks.
                    Do not explain anything.

                    Example:

                    User: I need personal loan leads in Delhi for 5000 people.

                    Output:
                    {
                    "intent": "loan",
                    "category": "Personal Loan",
                    "location": "Delhi",
                    "quantity": 5000
                    }

                    User: I want to send Bulk SMS to 50000 customers.

                    Output:
                    {
                    "intent": "communication",
                    "category": "Bulk SMS",
                    "location": null,
                    "quantity": 50000
                    }
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


#main chatbot loop
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
        lead = loan_agent(data)
        print(lead)
    elif intent == "real_estate":
        lead = real_estate_agent(data)
        print(lead)
    elif intent == "communication":
        lead = communication_agent(data)
        print(lead)
    elif "hello" in user_input or "hi" in user_input:
        print("Hello! How can I help you today?")
    else:
        print("Sorry, I don't understand your request yet.") 
