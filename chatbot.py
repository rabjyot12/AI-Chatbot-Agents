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
        return {
            "status": "incomplete",
            "missing": "category",
            "data": data
        }

    if location is None:
        return {
            "status": "incomplete",
            "missing": "location",
            "data": data
        }

    if quantity is None:
        return {
            "status": "incomplete",
            "missing": "quantity",
            "data": data
        }

    return {
        "status": "complete",
        "data": data
    }




#loan agent function

def loan_agent(data):

    category = data["category"]
    location = data["location"]
    quantity = data["quantity"]

    if category is not None and category.lower() == "loan":
        category = None
        data["category"] = None

    if category is None:
        return {
            "status": "incomplete",
            "missing": "category",
            "data": data
        }

    if location is None:
        return {
            "status": "incomplete",
            "missing": "location",
            "data": data
        }

    if quantity is None:
        return {
            "status": "incomplete",
            "missing": "quantity",
            "data": data
        }

    return {
        "status": "complete",
        "data": data
    }



#real estate agent function

def real_estate_agent(data):

    category = data["category"]
    location = data["location"]
    quantity = data["quantity"]

    if category is not None and category.lower() == "real estate":
        category = None
        data["category"] = None

    if category is None:
        return {
            "status": "incomplete",
            "missing": "category",
            "data": data
        }

    if location is None:
        return {
            "status": "incomplete",
            "missing": "location",
            "data": data
        }

    if quantity is None:
        return {
            "status": "incomplete",
            "missing": "quantity",
            "data": data
        }

    return {
        "status": "complete",
        "data": data
    }



#communication agent function

def communication_agent(data):

    category = data["category"]
    quantity = data["quantity"]

    if category is None:
        return {
            "status": "incomplete",
            "missing": "category",
            "data": data
        }

    if quantity is None:
        return {
            "status": "incomplete",
            "missing": "quantity",
            "data": data
        }

    return {
        "status": "complete",
        "data": data
    }



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



def extract_information(user_input, conversation_history, current_data=None):

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
                    If the latest message is a new request, do not copy missing values from an older completed request.
                    Only use previous information when it belongs to the current unfinished request.

                    For example:

                    Previous message:
                    "I need loan leads."

                    Latest message:
                    "Personal Loan"

                    The result should be:

                    {
                        "intent": "loan",
                        "category": "Personal Loan",
                        "location": null,
                        "quantity": null
                    }
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
                "content": f"""
                    Current request information:
                    {current_data}

                    Latest user message:
                    {user_input}

                    Extract information from the latest user message.

                    If Current request information contains already collected fields, keep those fields.

                    Do NOT copy values from older completed requests in the conversation history.

                    If a field has not been provided for the current request, return null.
                    """
            }
        ]
    )

    result = response.choices[0].message.content

    if not result:
        print("The AI returned an empty response.")
        return {
            "intent": "unknown",
            "category": None,
            "location": None,
            "quantity": None
        }

    result = result.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        print("The AI returned invalid JSON:")
        print(result)

        return {
            "intent": "unknown",
            "category": None,
            "location": None,
            "quantity": None
        }

    return data


#main chatbot loop
print("Hello! I am your chatbot.")

conversation_history = []
current_intent = None
current_data = None
while True:

    user_input = input("You: ")

    if "bye" in user_input.lower():
        print("Goodbye!")
        break

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    data = extract_information(
        user_input,
        conversation_history,
        current_data
    )

    detected_intent = data["intent"]

    if current_intent is None:

        if detected_intent == "unknown":
            print("Sorry, I don't understand your request yet.")
            continue

        current_intent = detected_intent
        current_data = data

    else:

        if detected_intent != current_intent and detected_intent != "unknown":

            current_intent = detected_intent
            current_data = data

        else:

            current_data.update({
                key: value
                for key, value in data.items()
                if value is not None
            })

    intent = current_intent
    data = current_data

    if intent == "education":
        result = education_agent(data)

    elif intent == "loan":
        result = loan_agent(data)

    elif intent == "real_estate":
        result = real_estate_agent(data)

    elif intent == "communication":
        result = communication_agent(data)

    else:
        print("Sorry, I don't understand your request yet.")
        continue

    if result["status"] == "incomplete":

        missing = result["missing"]

        if intent == "education":

            if missing == "category":
                print("Are you looking for NEET UG or NEET PG leads?")

            elif missing == "location":
                print("Which location are you looking for?")

            elif missing == "quantity":
                print("How many leads do you need?")

        elif intent == "loan":

            if missing == "category":
                print("What type of loan leads are you looking for?")

            elif missing == "location":
                print("Which location are you looking for?")

            elif missing == "quantity":
                print("How many leads do you need?")

        elif intent == "real_estate":

            if missing == "category":
                print("Are you looking for residential or commercial real estate leads?")

            elif missing == "location":
                print("Which location are you interested in?")

            elif missing == "quantity":
                print("How many leads do you need?")

        elif intent == "communication":

            if missing == "category":
                print("Which communication service are you interested in?")
                print("Bulk SMS, RCS SMS, Voice, WhatsApp, IVR, or Toll-Free?")

            elif missing == "quantity":
                print("What is the approximate number of customers/recipients?")

    else:

        lead = result["data"]

        print("\nHere is the information I collected:")

        if intent == "education":
            print("Service:", "Education Data")
            print("Category:", lead["category"])
            print("Location:", lead["location"])
            print("Lead Quantity:", lead["quantity"])

        elif intent == "loan":
            print("Service:", "Loan Data")
            print("Loan Type:", lead["category"])
            print("Location:", lead["location"])
            print("Lead Quantity:", lead["quantity"])

        elif intent == "real_estate":
            print("Service:", "Real Estate Data")
            print("Property Type:", lead["category"])
            print("Location:", lead["location"])
            print("Lead Quantity:", lead["quantity"])

        elif intent == "communication":
            print("Service:", lead["category"])
            print("Recipient Quantity:", lead["quantity"])

        print("\nStructured Lead Data:")
        print(lead) 

        current_intent = None
        current_data = None
