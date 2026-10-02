import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
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



#uses keywords to identify the request


def detect_intent(user_input):

    user_input = user_input.lower()

    if (
        "onboard" in user_input
        or "onboarding" in user_input
        or "registration" in user_input
        or "register" in user_input
        or "setup" in user_input
        or "set up" in user_input
    ):
        return "onboarding"

    elif "education" in user_input or "neet" in user_input:
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


#uses the LLM to identify the request
def detect_intent_with_llm(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
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


#stores the user's answer in the correct field
def update_followup_data(user_input, current_data, missing):

    value = user_input.strip()

    if missing == "quantity":
        try:
            quantity = int(value.replace(",", ""))
            current_data["quantity"] = quantity
        except ValueError:
            return False

    elif missing == "location":
        current_data["location"] = value.title()

    elif missing == "category":

        intent = current_data["intent"]

        if intent == "loan":
            current_data["category"] = value.title()

        elif intent == "education":
            value_lower = value.lower()

            if "neet ug" in value_lower:
                current_data["category"] = "NEET UG"

            elif "neet pg" in value_lower:
                current_data["category"] = "NEET PG"

            else:
                return False

        elif intent == "real_estate":
            value_lower = value.lower()

            if "residential" in value_lower:
                current_data["category"] = "Residential"

            elif "commercial" in value_lower:
                current_data["category"] = "Commercial"

            else:
                return False

        elif intent == "communication":

            value_lower = value.lower()

            if "bulk sms" in value_lower:
                current_data["category"] = "Bulk SMS"

            elif "rcs" in value_lower:
                current_data["category"] = "RCS SMS"

            elif "voice" in value_lower:
                current_data["category"] = "Voice OBD/IBD"

            elif "whatsapp" in value_lower:
                current_data["category"] = "WhatsApp"

            elif "ivr" in value_lower:
                current_data["category"] = "IVR"

            elif "toll" in value_lower:
                current_data["category"] = "Toll-Free"

            else:
                return False

    return True


# onboarding agent
def onboarding_agent(data):

    if data.get("company_email") is None:
        return {
            "status": "incomplete",
            "missing": "company_email",
            "data": data
        }

    if data.get("gst_status") != "received":
        return {
            "status": "incomplete",
            "missing": "gst_status",
            "data": data
        }

    if data.get("pan_status") != "received":
        return {
            "status": "incomplete",
            "missing": "pan_status",
            "data": data
        }

    if data.get("aadhaar_status") != "received":
        return {
            "status": "incomplete",
            "missing": "aadhaar_status",
            "data": data
        }

    if data.get("msme_required") is None:
        return {
            "status": "incomplete",
            "missing": "msme_decision",
            "data": data
        }

    if (
        data.get("msme_required") is True
        and data.get("msme_status") != "received"
    ):
        return {
            "status": "incomplete",
            "missing": "msme",
            "data": data
        }

    return {
        "status": "complete",
        "data": data
    }

#this converts user's language to structured data using the LLM
def extract_information(user_input, conversation_history, current_data=None):

    try:
        response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
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
                            onboarding
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

                            For onboarding:
                            - If the user says they want to onboard, register, activate, or set up the services, use intent = "onboarding".

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

    except Exception as e:
        print("LLM API error:", e)

        return {
            "intent": "unknown",
            "category": None,
            "location": None,
            "quantity": None
        }

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



#Controls the whole conversation
def process_message(user_input, current_intent, current_data, conversation_history):

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    #new request

    if current_intent is None:

        detected_intent = detect_intent(user_input)

        if detected_intent == "onboarding":

            current_intent = "onboarding"

            current_data = {
                "intent": "onboarding",
                "company_email": None,
                "gst_status": "pending",
                "pan_status": "pending",
                "aadhaar_status": "pending",
                "msme_required": None,
                "msme_status": "not_required",
                "onboarding_status": "incomplete"
            }

        else:

            data = extract_information(
                user_input,
                conversation_history,
                None
            )

            intent = data["intent"]

            if intent == "unknown":
                return {
                    "reply": "Sorry, I don't understand your request yet.",
                    "current_intent": None,
                    "current_data": None,
                    "conversation_history": conversation_history,
                    "complete": False,
                    "lead": None
                }

            current_intent = intent
            current_data = data

        

    #follow-up message for an existing request
   

    else:

        # check which field is currently missing

        if current_intent == "education":
            result = education_agent(current_data)

        elif current_intent == "loan":
            result = loan_agent(current_data)

        elif current_intent == "real_estate":
            result = real_estate_agent(current_data)

        elif current_intent == "communication":
            result = communication_agent(current_data)

        elif current_intent == "onboarding":
            result = onboarding_agent(current_data)

        else:
            result = {
                "status": "incomplete",
                "missing": None,
                "data": current_data
            }

        missing = result["missing"]

        # try to understand whether the user started
        #a completely new request.

        detected_intent = detect_intent(user_input)

        if (
            detected_intent != "unknown"
            and detected_intent != current_intent
        ):

            data = extract_information(
                user_input,
                conversation_history,
                None
            )

            if data["intent"] != "unknown":
                current_intent = data["intent"]
                current_data = data

        else:

            if current_intent == "onboarding":

                if missing == "company_email":

                    email = user_input.strip()

                    if "@" in email and "." in email.split("@")[-1]:

                        current_data["company_email"] = email
                        updated = True

                    else:

                        return {
                            "reply": (
                                "Please provide a valid company email address "
                                "linked to your website domain."
                            ),
                            "current_intent": current_intent,
                            "current_data": current_data,
                            "conversation_history": conversation_history,
                            "complete": False,
                            "lead": None,
                            "onboarding": True
                        }

                elif missing == "msme_decision":

                    answer = user_input.strip().lower()

                    if answer in ["yes", "y"]:

                        current_data["msme_required"] = True
                        current_data["msme_status"] = "pending"

                        updated = True

                    elif answer in ["no", "n"]:

                        current_data["msme_required"] = False
                        current_data["msme_status"] = "not_required"

                        updated = True

                    else:

                        return {
                            "reply": (
                                "Please answer Yes or No.\n\n"
                                "Will you be using your company name as the sender ID?"
                            ),
                            "current_intent": current_intent,
                            "current_data": current_data,
                            "conversation_history": conversation_history,
                            "complete": False,
                            "lead": None,
                            "onboarding": True
                        }

                elif missing == "msme":

                    # MSME is already required.
                    # The user cannot answer this step with Yes/No.
                    return {
                        "reply": (
                            "Please upload your MSME Registration certificate "
                            "using the upload option below."
                        ),
                        "current_intent": current_intent,
                        "current_data": current_data,
                        "conversation_history": conversation_history,
                        "complete": False,
                        "lead": None,
                        "onboarding": True
                    }

                else:

                    updated = True

            else:

                updated = update_followup_data(
                    user_input,
                    current_data,
                    missing
                )

            if not updated:
                return {
                    "reply": f"I couldn't understand that. Please provide the {missing}.",
                    "current_intent": current_intent,
                    "current_data": current_data,
                    "conversation_history": conversation_history,
                    "complete": False,
                    "lead": None
                }

    #run the appropriate agent function based on the current intent


    if current_intent == "education":

        result = education_agent(current_data)

    elif current_intent == "loan":

        result = loan_agent(current_data)

    elif current_intent == "real_estate":

        result = real_estate_agent(current_data)

    elif current_intent == "communication":

        result = communication_agent(current_data)

    elif current_intent == "onboarding":
        result = onboarding_agent(current_data)

    else:

        return {
            "reply": "Sorry, I don't understand your request yet.",
            "current_intent": None,
            "current_data": None,
            "conversation_history": conversation_history,
            "complete": False,
            "lead": None
        }


    # request is still incomplete, ask for the missing information


    if result["status"] == "incomplete":

        missing = result["missing"]

        if current_intent == "onboarding":

            if missing == "company_email":
                reply = (
                    "Please provide a valid email address linked "
                    "to your company's website domain."
                )

            elif missing == "gst_status":
                reply = (
                    "Please upload your GST Certificate "
                    "using the upload option below."
                )

            elif missing == "pan_status":
                reply = (
                    "Please upload your PAN Card "
                    "using the upload option below."
                )

            elif missing == "aadhaar_status":
                reply = (
                    "Please upload your Aadhaar Card "
                    "using the upload option below."
                )

            elif missing == "msme_decision":
                reply = (
                    "Will you be using your company name as the sender ID?\n\n"
                    "Please answer Yes or No."
                )

            elif missing == "msme":
                reply = (
                    "Please upload your MSME Registration certificate "
                    "using the upload option below."
                )

            return {
                "reply": reply,
                "current_intent": current_intent,
                "current_data": current_data,
                "conversation_history": conversation_history,
                "complete": False,
                "lead": None,
                "onboarding": True
            }

        if current_intent == "education":

            if missing == "category":
                reply = "Are you looking for NEET UG or NEET PG leads?"

            elif missing == "location":
                reply = "Which location are you looking for?"

            elif missing == "quantity":
                reply = "How many leads do you need?"

        elif current_intent == "loan":

            if missing == "category":
                reply = "What type of loan leads are you looking for?"

            elif missing == "location":
                reply = "Which location are you looking for?"

            elif missing == "quantity":
                reply = "How many leads do you need?"

        elif current_intent == "real_estate":

            if missing == "category":
                reply = (
                    "Are you looking for residential or "
                    "commercial real estate leads?"
                )

            elif missing == "location":
                reply = "Which location are you interested in?"

            elif missing == "quantity":
                reply = "How many leads do you need?"

        elif current_intent == "communication":

            if missing == "category":
                reply = (
                    "Which communication service are you interested in?\n\n"
                    "Bulk SMS, RCS SMS, Voice, WhatsApp, IVR, or Toll-Free?"
                )

            elif missing == "quantity":
                reply = (
                    "What is the approximate number of "
                    "customers/recipients?"
                )

        return {
            "reply": reply,
            "current_intent": current_intent,
            "current_data": current_data,
            "conversation_history": conversation_history,
            "complete": False,
            "lead": None
        }


    if current_intent == "onboarding":

        current_data["onboarding_status"] = "complete"

        return {
            "reply": (
                "Great! Your onboarding information has been collected successfully.\n\n"
                "Company Email: "
                f"{current_data['company_email']}\n"
                "GST Certificate: Received\n"
                "PAN Card: Received\n"
                "Aadhaar Card: Received\n"
                f"MSME Registration: {current_data['msme_status']}"
            ),
            "current_intent": None,
            "current_data": None,
            "conversation_history": conversation_history,
            "complete": True,
            "lead": None,
            "onboarding": True,
            "onboarding_data": current_data
        }


    #request is complete, save the lead and return a summary


    lead = result["data"]

    if current_intent == "education":

        reply = (
            "Great! I have collected your requirements.\n\n"
            f"Service: Education Data\n"
            f"Category: {lead['category']}\n"
            f"Location: {lead['location']}\n"
            f"Lead Quantity: {lead['quantity']}"
        )

    elif current_intent == "loan":

        reply = (
            "Great! I have collected your requirements.\n\n"
            f"Service: Loan Data\n"
            f"Loan Type: {lead['category']}\n"
            f"Location: {lead['location']}\n"
            f"Lead Quantity: {lead['quantity']}"
        )

    elif current_intent == "real_estate":

        reply = (
            "Great! I have collected your requirements.\n\n"
            f"Service: Real Estate Data\n"
            f"Property Type: {lead['category']}\n"
            f"Location: {lead['location']}\n"
            f"Lead Quantity: {lead['quantity']}"
        )

    elif current_intent == "communication":

        reply = (
            "Great! I have collected your requirements.\n\n"
            f"Service: {lead['category']}\n"
            f"Recipient Quantity: {lead['quantity']}"
        )

    return {
        "reply": reply,
        "current_intent": None,
        "current_data": None,
        "conversation_history": conversation_history,
        "complete": True,
        "lead": lead
    }
