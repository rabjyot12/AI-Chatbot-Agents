
services = {
    "bulk_sms": "Bulk SMS and RCS SMS",
    "voice": "Voice OBD/IBD",
    "whatsapp": "WhatsApp integration",
    "ivr": "IVR services",
    "toll_free": "Toll-Free numbers",
    "education": "Education leads such as NEET UG and NEET PG",
    "loan": "Loan leads",
    "real_estate": "Real estate leads"
}

def get_response(user_input):

    if "hello" in user_input or "hi" in user_input:
        return "Hello! How can I assist you today?"

    elif "bulk sms" in user_input:
        return f"Sure! We provide {services['bulk_sms']}. Are you interested in Bulk SMS or RCS SMS?"

    elif "education" in user_input:
        return f"Sure! We provide {services['education']}. Are you looking for NEET UG or NEET PG leads?"

    elif "voice" in user_input:
        return f"Sure! We provide {services['voice']}. Are you interested in voice calling services?"

    elif "whatsapp" in user_input:
        return f"Sure! We provide {services['whatsapp']}."

    elif "ivr" in user_input:
        return f"Sure! We provide {services['ivr']}."

    elif "toll free" in user_input or "tollfree" in user_input:
        return f"Sure! We provide {services['toll_free']}."

    elif "loan" in user_input:
        return f"Sure! We provide {services['loan']}."

    elif "real estate" in user_input or "realestate" in user_input:
        return f"Sure! We provide {services['real_estate']}."

    else:
        return "Sorry, I don't understand that yet."

print("Hello! I am your chatbot.")

while True:
    user_input = input("You: ").lower()

    if "bye" in user_input:
        print("Goodbye!")
        break

    response = get_response(user_input)
    print(response) 
