import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

from database import (
    create_table,
    get_all_sales_customers,
    save_sales_customer,
)
from product_catalog import PRODUCTS
from sales_agent import process_sales_message
from voice_service import transcribe_audio, synthesize_speech

load_dotenv()

st.set_page_config(
    page_title="Telecom AI Sales Agent",
    page_icon="💬",
    layout="wide",
)

# Styling
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 { margin-bottom: 0.3rem; }
    .hero p { margin-bottom: 0; color: #dbeafe; }

    </style>
    """,
    unsafe_allow_html=True,
)

# Database initialization
try:
    create_table()
    db_ready = True
except Exception as exc:
    db_ready = False
    print("Database initialization error:", exc)

# Session state initialization
WELCOME = (
    "Hi! 👋 I'm your telecom solutions sales assistant. "
    "Tell me what you're trying to achieve and I'll help you find "
    "the right communication solution."
)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "assistant", "content": WELCOME}
    ]

if "sales_state" not in st.session_state:
    st.session_state.sales_state = {
        "name": None,
        "company": None,
        "phone": None,
        "email": None,
        "requirement": None,
        "interested_product": None,
        "expected_scale": None,
        "sales_followup": False,
    }

if "customer_saved" not in st.session_state:
    st.session_state.customer_saved = False
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "message_audio" not in st.session_state:
    st.session_state.message_audio = {}

# Set the transcript before creating the input widget, so the user can review/edit it.
if "pending_transcript" in st.session_state:
    st.session_state.typed_message_input = st.session_state.pop("pending_transcript")


def handle_message(message: str):
    """Send typed or transcribed text through the existing sales-agent workflow."""
    message = (message or "").strip()
    if not message:
        return

    result = process_sales_message(
        message,
        st.session_state.conversation_history,
        st.session_state.sales_state,
    )
    st.session_state.sales_state = result["state"]


def submit_typed_message():
    """Send the text input only when the user presses the Send button."""
    message = st.session_state.get("typed_message_input", "").strip()
    if message:
        handle_message(message)
        st.session_state.typed_message_input = ""


# Sidebar: product information only; no Speak AI replies toggle.
with st.sidebar:
    st.title("Telecom AI Sales Agent")
    st.caption(
        "Prototype for website sales conversations. "
        "The same sales engine can later be connected to WhatsApp."
    )
    st.subheader("Solutions")

    for name, product in PRODUCTS.items():
        st.markdown(f"**{name}**")
        st.caption(product["description"])

    st.divider()
    if st.button("Start New Conversation", use_container_width=True):
        st.session_state.conversation_history = [
            {"role": "assistant", "content": WELCOME}
        ]
        st.session_state.sales_state = {
            "name": None,
            "company": None,
            "phone": None,
            "email": None,
            "requirement": None,
            "interested_product": None,
            "expected_scale": None,
            "sales_followup": False,
        }
        st.session_state.customer_saved = False
        st.session_state.last_audio_id = None
        st.session_state.message_audio = {}
        st.session_state.typed_message_input = ""
        st.rerun()

# Header
st.markdown(
    """
    <div class="hero">
        <h1>💬 Telecom AI Sales Agent</h1>
        <p>
            Conversational sales assistant for website visitors.
            Understand the requirement → recommend a solution → qualify the customer → hand off to sales.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Live conversational voice agent
with st.expander("🎙️ Start a live voice conversation", expanded=False):
    st.caption(
        "Talk naturally with our AI sales assistant. "
        "Your existing text chat remains available below."
    )

    # Replace with the exact Agent ID shown in ElevenLabs.
    ELEVENLABS_AGENT_ID = "agent_2901m5apm8drff0bxt5j5xg1xtzp"

    if ELEVENLABS_AGENT_ID != "agent_2901m5apm8drff0bxt5j5xg1xtzp":
        components.html(
            f"""
            <div style="min-height:180px;">
                <elevenlabs-convai
                    agent-id="{ELEVENLABS_AGENT_ID}">
                </elevenlabs-convai>
                <script
                    src="https://unpkg.com/@elevenlabs/convai-widget-embed"
                    async
                    type="text/javascript">
                </script>
            </div>
            """,
            height=220,
            scrolling=False,
        )
    else:
        st.info(
            "Add your ElevenLabs Agent ID here to enable live voice."
        )

chat_col, lead_col = st.columns([2.1, 1])

# Conversation panel
with chat_col:
    st.subheader("Conversation")

    for message_index, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                message_col, speaker_col = st.columns([12, 1], vertical_alignment="top")
                with message_col:
                    st.markdown(message["content"])
                with speaker_col:
                    audio_key = str(message_index)
                    audio_is_ready = audio_key in st.session_state.message_audio
                    if not audio_is_ready:
                        if st.button(
                            "🔊",
                            key=f"generate_ai_audio_{message_index}",
                            help="Play this AI response",
                        ):
                            try:
                                with st.spinner("Preparing spoken response..."):
                                    audio_bytes = synthesize_speech(message["content"])
                                if not audio_bytes:
                                    raise RuntimeError("Speech generation returned no audio.")
                                st.session_state.message_audio[audio_key] = audio_bytes
                                st.rerun()
                            except Exception as exc:
                                st.error("Could not generate audio for this response.")
                                print("Text-to-speech error:", exc)
                    else:
                        audio_b64 = base64.b64encode(
                            st.session_state.message_audio[audio_key]
                        ).decode("ascii")
                        # The speaker button itself toggles to Stop while the audio plays.
                        # Audio stays inside this component; no separate audio bar is shown.
                        components.html(
                            f"""
                            <div style="display:flex;justify-content:center;align-items:flex-start;">
                              <button id="voice-toggle-{message_index}"
                                title="Play AI voice" aria-label="Play AI voice"
                                style="width:42px;height:42px;border:1px solid #444;
                                background:#171923;color:white;border-radius:10px;
                                cursor:pointer;font-size:18px;">🔊</button>
                              <audio id="ai-audio-{message_index}" preload="auto" style="display:none">
                                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                              </audio>
                            </div>
                            <script>
                              const audio = document.getElementById('ai-audio-{message_index}');
                              const toggle = document.getElementById('voice-toggle-{message_index}');
                              const showSpeaker = () => {{
                                toggle.textContent = '🔊';
                                toggle.title = 'Play AI voice';
                                toggle.setAttribute('aria-label', 'Play AI voice');
                              }};
                              const showStop = () => {{
                                toggle.textContent = '⏹️';
                                toggle.title = 'Stop AI voice';
                                toggle.setAttribute('aria-label', 'Stop AI voice');
                              }};
                              toggle.onclick = async () => {{
                                if (!audio.paused && !audio.ended) {{
                                  audio.pause();
                                  audio.currentTime = 0;
                                  showSpeaker();
                                }} else {{
                                  try {{
                                    if (audio.ended) audio.currentTime = 0;
                                    await audio.play();
                                    showStop();
                                  }} catch (e) {{ showSpeaker(); }}
                                }}
                              }};
                              audio.onplay = showStop;
                              audio.onpause = showSpeaker;
                              audio.onended = showSpeaker;
                              // Try autoplay after generation; if blocked, click the speaker once more.
                              audio.play().then(showStop).catch(showSpeaker);
                            </script>
                            """,
                            height=48,
                            scrolling=False,
                        )
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])

    # Input row: recording puts text in the editable input; Send submits it.
    input_col, mic_col, send_col = st.columns([8, 1.15, 1], vertical_alignment="bottom")
    with input_col:
        st.text_input(
            "Message",
            placeholder="Or type what you need...",
            label_visibility="collapsed",
            key="typed_message_input",
        )
    with mic_col:
        audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            format="wav",
            key="sales_voice_recorder",
        )
    with send_col:
        st.button(
            "⬆️",
            key="send_chat_message",
            use_container_width=True,
            help="Send message",
            on_click=submit_typed_message,
        )

    if audio and audio.get("bytes") and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio.get("id")
        try:
            with st.spinner("Transcribing your voice..."):
                audio_format = audio.get("format", "wav")
                if not isinstance(audio_format, str):
                    audio_format = "wav"
                transcript = transcribe_audio(
                    audio["bytes"], audio_format=audio_format.lower()
                )
            if transcript:
                st.session_state.pending_transcript = transcript
                st.toast("Transcript added to the message box. Review it and press Send.")
                st.rerun()
            else:
                st.warning("I couldn't recognize speech. Please try recording again.")
        except Exception as exc:
            st.error("Speech recognition failed. Check the voice setup and try again.")
            print("Speech-to-text error:", exc)

# Customer panel: preserve the existing customer capture and database workflow.
with lead_col:
    st.subheader("Customer")
    state = st.session_state.sales_state

    with st.form("customer_form"):
        name = st.text_input("Name", value=state.get("name") or "")
        company = st.text_input("Company", value=state.get("company") or "")
        phone = st.text_input("Phone", value=state.get("phone") or "")
        email = st.text_input("Email", value=state.get("email") or "")
        requirement = st.text_area(
            "Requirement", value=state.get("requirement") or ""
        )
        interested_product = st.text_input(
            "Interested product", value=state.get("interested_product") or ""
        )
        expected_scale = st.text_input(
            "Expected scale", value=state.get("expected_scale") or ""
        )

        save_button = st.form_submit_button(
            "Send to Sales Team", use_container_width=True
        )

    if save_button:
        customer = {
            "name": name.strip() or None,
            "company": company.strip() or None,
            "phone": phone.strip() or None,
            "email": email.strip() or None,
            "requirement": requirement.strip() or None,
            "interested_product": interested_product.strip() or None,
            "expected_scale": expected_scale.strip() or None,
            "sales_followup": True,
        }

        if not any(
            [
                customer["name"],
                customer["company"],
                customer["phone"],
                customer["email"],
                customer["requirement"],
            ]
        ):
            st.warning("Please provide at least one useful customer detail.")
        elif not db_ready:
            st.error("Database is not connected. Check the database settings.")
        else:
            try:
                customer_id = save_sales_customer(customer, channel="website")
                st.session_state.sales_state.update(customer)
                st.session_state.customer_saved = True
                st.success(
                    f"Customer sent to sales successfully. ID: {customer_id}"
                )
            except Exception as exc:
                st.error("The customer was collected but could not be saved.")
                print("Customer database error:", exc)

    if st.session_state.customer_saved:
        st.info("This customer has already been saved in the database.")

# Product information and downloadable brochure-style text files.
st.divider()
st.subheader("Product Information")
st.caption(
    "These are prototype product descriptions. Replace them with the company's "
    "approved brochures and product specifications before the production demo."
)

for name, product in PRODUCTS.items():
    with st.expander(name):
        st.write(product["description"])
        st.write(f"**Best for:** {product['best_for']}")
        st.markdown("**Known information**")
        for fact in product["facts"]:
            st.write(f"- {fact}")

        st.download_button(
            label=f"Download {name} information",
            data=(
                f"{name}\n\n"
                f"{product['description']}\n\n"
                f"Best for: {product['best_for']}\n\n"
                "Known information:\n"
                + "\n".join(f"- {fact}" for fact in product["facts"])
            ),
            file_name=f"{product['key']}_product_information.txt",
            mime="text/plain",
            key=f"download_{product['key']}",
        )

# Admin/demo sales dashboard.
st.divider()
st.subheader("Sales Dashboard")

if db_ready:
    try:
        customers = get_all_sales_customers()
        st.metric("Customers captured", len(customers))

        if customers:
            rows = []
            for row in customers:
                (
                    customer_id,
                    name,
                    company,
                    phone,
                    email,
                    requirement,
                    interested_product,
                    expected_scale,
                    conversation_summary,
                    status,
                    sales_followup,
                    channel,
                    created_at,
                ) = row

                rows.append(
                    {
                        "ID": customer_id,
                        "Name": name,
                        "Company": company,
                        "Phone": phone,
                        "Email": email,
                        "Requirement": requirement,
                        "Product": interested_product,
                        "Scale": expected_scale,
                        "Summary": conversation_summary,
                        "Status": status,
                        "Follow-up": sales_followup,
                        "Channel": channel,
                        "Created": created_at,
                    }
                )

            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No sales customers have been captured yet.")

    except Exception as exc:
        st.error("Could not load the sales dashboard.")
        print("Dashboard error:", exc)
else:
    st.warning("Sales dashboard is unavailable until the database connection works.")


with st.expander("Speech engine diagnostics"):
    from voice_service import check_speech_engine
    st.json(check_speech_engine())