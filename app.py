import streamlit as st

from chatbot import process_message
from database import create_table, save_lead, get_all_leads


st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

create_table()

st.title("🤖 AI Chatbot")

st.divider()

st.subheader("📊 Lead Dashboard")

try:

    leads = get_all_leads()

    if leads:

        lead_data = []

        for lead in leads:

            lead_data.append({
                "ID": lead[0],
                "Intent": lead[1],
                "Category": lead[2],
                "Location": lead[3],
                "Quantity": lead[4],
                "Created At": lead[5]
            })

        st.dataframe(
            lead_data,
            use_container_width=True
        )

    else:

        st.info("No leads have been collected yet.")

except Exception as e:

    st.error("Unable to load leads from the database.")

    print("Dashboard database error:", e)

st.write(
    "Tell us what service you are looking for and "
    "I'll help collect the required information."
)


# Initialize session state

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_intent" not in st.session_state:
    st.session_state.current_intent = None

if "current_data" not in st.session_state:
    st.session_state.current_data = None

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input

user_input = st.chat_input("Type your message...")


if user_input:

    # Display user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)


    # Process message

    result = process_message(
        user_input,
        st.session_state.current_intent,
        st.session_state.current_data,
        st.session_state.conversation_history
    )


    # Update chatbot state

    st.session_state.current_intent = result["current_intent"]
    st.session_state.current_data = result["current_data"]
    st.session_state.conversation_history = result["conversation_history"]


    # Display chatbot response

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["reply"]
    })

    with st.chat_message("assistant"):
        st.write(result["reply"])


    # Show structured lead when complete

    if result["complete"]:

        st.success("Lead information collected successfully!")

        st.json(result["lead"])

        try:

            lead_id = save_lead(result["lead"])

            st.success(
                f"Lead saved successfully! Lead ID: {lead_id}"
            )

        except Exception as e:

            st.error(
                "The lead was collected, but it could not be saved to the database."
            )

            print("Database error:", e)