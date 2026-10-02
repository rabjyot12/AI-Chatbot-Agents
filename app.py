import streamlit as st

from chatbot import process_message
from database import (
    create_table,
    save_lead,
    get_all_leads,
    save_onboarding,
    get_all_onboarding
)


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


st.divider()

st.subheader("📋 Onboarding Dashboard")

try:

    onboarding_records = get_all_onboarding()

    if onboarding_records:

        onboarding_data = []

        for record in onboarding_records:

            onboarding_data.append({
                "ID": record[0],
                "Company Email": record[1],
                "GST": record[2],
                "PAN": record[3],
                "Aadhaar": record[4],
                "MSME Required": record[5],
                "MSME": record[6],
                "Status": record[7],
                "Created At": record[8]
            })

        st.dataframe(
            onboarding_data,
            use_container_width=True
        )

    else:

        st.info("No onboarding records yet.")

except Exception as e:

    st.error("Unable to load onboarding records.")

    print("Onboarding dashboard error:", e)


st.write(
    "Tell us what service you are looking for and "
    "I'll help collect the required information."
)


#initialize session state variables

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_intent" not in st.session_state:
    st.session_state.current_intent = None

if "current_data" not in st.session_state:
    st.session_state.current_data = None

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "onboarding_data" not in st.session_state:
    st.session_state.onboarding_data = None


#this displays previous messages in the chat interface

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])



#onboarding document upload section


if st.session_state.current_intent == "onboarding":

    st.divider()

    st.subheader("📄 Onboarding Documents")

    current_data = st.session_state.current_data

    if current_data:

        # GST
        if current_data.get("gst_status") == "pending":

            gst_file = st.file_uploader(
                "Upload GST Certificate",
                type=["pdf", "png", "jpg", "jpeg"],
                key="gst_upload"
            )

            if gst_file is not None:

                st.success("GST Certificate received.")

                current_data["gst_status"] = "received"

        # PAN
        if current_data.get("pan_status") == "pending":

            pan_file = st.file_uploader(
                "Upload PAN Card",
                type=["pdf", "png", "jpg", "jpeg"],
                key="pan_upload"
            )

            if pan_file is not None:

                st.success("PAN Card received.")

                current_data["pan_status"] = "received"

        # Aadhaar
        if current_data.get("aadhaar_status") == "pending":

            aadhaar_file = st.file_uploader(
                "Upload Aadhaar Card",
                type=["pdf", "png", "jpg", "jpeg"],
                key="aadhaar_upload"
            )

            if aadhaar_file is not None:

                st.success("Aadhaar Card received.")

                current_data["aadhaar_status"] = "received"

        # MSME
        if current_data.get("msme_required") is True:

            if current_data.get("msme_status") == "pending":

                msme_file = st.file_uploader(
                    "Upload MSME Registration",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="msme_upload"
                )

                if msme_file is not None:

                    st.success("MSME Registration received.")

                    current_data["msme_status"] = "received"



if st.session_state.current_intent == "onboarding":

    onboarding_data = st.session_state.current_data

    if onboarding_data:

        required_complete = (
            onboarding_data.get("company_email") is not None
            and onboarding_data.get("gst_status") == "received"
            and onboarding_data.get("pan_status") == "received"
            and onboarding_data.get("aadhaar_status") == "received"
        )

        st.write("DEBUG msme_required:", onboarding_data.get("msme_required"))
        st.write("DEBUG type:", type(onboarding_data.get("msme_required")))

        msme_complete = (
            onboarding_data.get("msme_required") is False
            or onboarding_data.get("msme_status") == "received"
        )

        st.write("DEBUG required_complete:", required_complete)
        st.write("DEBUG msme_complete:", msme_complete)
        st.write("DEBUG onboarding_data:", onboarding_data)

        if required_complete and msme_complete:

            onboarding_data["onboarding_status"] = "complete"

            try:
                st.write("DEBUG: Saving onboarding:", onboarding_data)

                onboarding_id = save_onboarding(onboarding_data)

                st.success(
                    f"Onboarding completed successfully! "
                    f"Onboarding ID: {onboarding_id}"
                )

                st.json(onboarding_data)

                st.session_state.current_intent = None
                st.session_state.current_data = None

            except Exception as e:

                st.error(
                    "Onboarding was completed, but the information "
                    "could not be saved to the database."
                )

                print("Onboarding database error:", e)


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

    if result["complete"] and result["lead"] is not None:

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

            print(f"Database error: {e}")