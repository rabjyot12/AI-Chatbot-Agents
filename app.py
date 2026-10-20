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


def icon_svg(name: str, size: int = 20, stroke_width: float = 1.8) -> str:
    """Return a small Lucide-style inline SVG icon."""
    paths = {
        "phone-call": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.1 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.96.36 1.9.7 2.8a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.84.58 2.8.7A2 2 0 0 1 22 16.92z"/>',
        "mic": '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/>',
        "volume": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/>',
        "stop": '<rect x="6" y="6" width="12" height="12" rx="2"/>',
        "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
        "moon": '<path d="M20.985 12.486A9 9 0 1 1 11.514 3.015a7 7 0 0 0 9.471 9.471z"/>',
        "send": '<path d="M12 19V5M5 12l7-7 7 7"/>',
        "close": '<path d="m18 6-12 12M6 6l12 12"/>',
    }
    path = paths.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{path}</svg>'
    )

# Theme state: the sun switches to light mode; the moon switches back to dark mode.
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"
if "show_live_voice" not in st.session_state:
    st.session_state.show_live_voice = False

is_light = st.session_state.theme_mode == "light"
if is_light:
    page_bg = "#f7f8fc"
    panel_bg = "#ffffff"
    text_color = "#172033"
    muted_color = "#475569"
    border_color = "#e2e8f0"
    input_bg = "#ffffff"
else:
    page_bg = "#0e1117"
    panel_bg = "#171b24"
    text_color = "#f3f4f6"
    muted_color = "#a1a1aa"
    border_color = "#30343d"
    input_bg = "#252832"

# Styling: light mode gets explicit readable surfaces; dark mode keeps its existing palette.
if is_light:
    button_bg = "#ffffff"
    button_hover = "#f1f5f9"
    button_border = "#d1d5db"
    field_border = "#cbd5e1"
    focus_border = "#64748b"
    sidebar_text = "#172033"
else:
    button_bg = "#171b24"
    button_hover = "#252b36"
    button_border = "#3b414d"
    field_border = "#30343d"
    focus_border = "#64748b"
    sidebar_text = "#f3f4f6"

st.markdown(
    f"""
    <style>
    .stApp {{ background: {page_bg}; color: {text_color}; }}
    /* Match Streamlit's top chrome to the active theme instead of leaving a black bar. */
    header[data-testid="stHeader"] {{ background: {page_bg} !important; }}
    [data-testid="stToolbar"] {{ background: transparent !important; }}
    [data-testid="stDecoration"] {{ background: transparent !important; }}
    .block-container {{ max-width: 1380px; padding-top: 1.4rem; padding-bottom: 3rem; }}
    [data-testid="stSidebar"] {{ background: {panel_bg}; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {{ color: {sidebar_text}; }}
    h1, h2, h3, p, label, .stMarkdown {{ color: {text_color}; }}
    [data-testid="stCaptionContainer"] p {{ color: {muted_color} !important; }}
    .hero {{
        padding: 1.55rem 1.8rem; border-radius: 22px;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white; margin-bottom: 1.25rem;
    }}
    .hero h1 {{ margin-bottom: .3rem; color: white !important; }}
    .hero p {{ margin-bottom: 0; color: #dbeafe !important; }}
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: {input_bg} !important; color: {text_color} !important;
        border: 1px solid {field_border} !important; border-radius: 12px !important;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {{ color: {muted_color} !important; opacity: 1; }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {{
        border-color: {focus_border} !important; box-shadow: 0 0 0 1px {focus_border} !important;
    }}
    div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
        color: {text_color} !important; background: {button_bg} !important;
        border: 1px solid {button_border} !important; border-radius: 12px !important;
        min-height: 2.5rem; min-width: 2.65rem;
        padding: 0.45rem 0.65rem; transition: background .15s ease;
        display: inline-flex; align-items: center; justify-content: center;
        overflow: visible; line-height: 1; box-shadow: none !important;
    }}
    div[data-testid="stButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover {{ background: {button_hover} !important; }}
    div[data-testid="stDownloadButton"] button {{
        color: {text_color} !important; background: {button_bg} !important;
        border: 1px solid {button_border} !important; border-radius: 12px !important;
        min-height: 2.5rem; padding: 0.55rem 0.9rem; box-shadow: none !important;
    }}
    div[data-testid="stDownloadButton"] button, div[data-testid="stDownloadButton"] button * {{
        color: {text_color} !important;
    }}
    div[data-testid="stButton"] button p {{
        color: {text_color} !important; display: flex; align-items: center; justify-content: center;
        margin: 0; line-height: 1;
    }}
    div[data-testid="stButton"] button svg {{
        color: {text_color} !important; flex-shrink: 0; width: 1.25rem; height: 1.25rem;
        overflow: visible;
    }}
    /* Keep the recorder control aligned with the neighboring icon buttons. */
    iframe[title*="mic_recorder"] {{
        transform: translateY(5px);
        background: transparent !important;
        border: 0 !important;
        color-scheme: {"light" if is_light else "dark"};
    }}
    /* Recorder widget is an iframe; style its frame consistently with the composer. */
    div[data-testid="stHorizontalBlock"] iframe[title*="mic_recorder"] {{
        border-radius: 12px !important;
        background: transparent !important;
        color-scheme: {"light" if is_light else "dark"} !important;
        overflow: hidden !important;
    }}
    /* Streamlit help/tooltips should follow the selected theme instead of staying dark. */
    [role="tooltip"], [data-testid="stTooltipContent"] {{
        background: {"#ffffff" if is_light else "#252832"} !important;
        color: {"#172033" if is_light else "#f3f4f6"} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(0,0,0,.12) !important;
    }}
    [role="tooltip"] *, [data-testid="stTooltipContent"] * {{
        color: {"#172033" if is_light else "#f3f4f6"} !important;
    }}
    [data-testid="stChatMessage"] {{ border: none; background: transparent; }}
    div[data-testid="stExpander"] {{
        border: 1px solid {border_color} !important; border-radius: 14px !important;
        background: {panel_bg} !important; overflow: hidden;
    }}
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        background: {panel_bg} !important; color: {text_color} !important;
    }}
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary svg {{ color: {text_color} !important; }}
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        border-top: 1px solid {border_color} !important; padding-top: .8rem;
    }}
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] {{ color: {text_color} !important; }}
    [data-testid="stDataFrame"] {{ border: 1px solid {border_color}; border-radius: 12px; overflow: hidden; }}
    hr {{ border-color: {border_color}; }}
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
    if st.button(":material/dark_mode:" if is_light else ":material/light_mode:", key="toggle_theme", use_container_width=False):
        st.session_state.theme_mode = "light" if not is_light else "dark"
        st.rerun()
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


# Agent ID and compact voice panel (opened from the composer microphone icon).
ELEVENLABS_AGENT_ID = "agent_2901m5apm8drff0bxt5j5xg1xtzp"

if st.session_state.show_live_voice:
    voice_header_col, voice_close_col = st.columns([10, 1])
    with voice_header_col:
        st.caption("LIVE VOICE · Speak naturally with the telecom sales assistant")
    with voice_close_col:
        if st.button("✕", key="close_live_voice", help="Close voice panel"):
            st.session_state.show_live_voice = False
            st.rerun()
    components.html(
        f"""
        <html>
          <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
          <body style="margin:0; padding:8px 4px 18px; background:transparent; overflow:visible;">
            <div style="width:100%; min-height:250px; display:flex; justify-content:center; align-items:center; overflow:visible;">
              <elevenlabs-convai agent-id="{ELEVENLABS_AGENT_ID}"></elevenlabs-convai>
            </div>
            <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
          </body>
        </html>
        """,
        height=300,
        scrolling=False,
    )

chat_col, lead_col = st.columns([1.8, 1], gap="large")

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
                            ":material/volume_up:",
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
                                style="width:34px;height:34px;border:0;background:transparent;
                                color:inherit;border-radius:999px;cursor:pointer;
                                display:flex;align-items:center;justify-content:center;opacity:.78;">{icon_svg("volume", 19)}</button>
                              <audio id="ai-audio-{message_index}" preload="auto" style="display:none">
                                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                              </audio>
                            </div>
                            <script>
                              const audio = document.getElementById('ai-audio-{message_index}');
                              const toggle = document.getElementById('voice-toggle-{message_index}');
                              const showSpeaker = () => {{
                                toggle.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
                                toggle.title = 'Play AI voice';
                                toggle.setAttribute('aria-label', 'Play AI voice');
                              }};
                              const showStop = () => {{
                                toggle.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';
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

    # Compact composer: text, borderless live-call icon, recorder, and send.
    input_col, call_col, mic_col, send_col = st.columns([8, 0.82, 0.82, 0.82], vertical_alignment="center")
    with input_col:
        st.text_input(
            "Message",
            placeholder="Message Telecom AI...",
            label_visibility="collapsed",
            key="typed_message_input",
        )
    with call_col:
        if st.button(":material/call:", key="open_live_voice", help="Start a live AI voice conversation", use_container_width=True):
            st.session_state.show_live_voice = not st.session_state.show_live_voice
            st.rerun()
    with mic_col:
        audio = mic_recorder(
            start_prompt="🎙",
            stop_prompt="■",
            just_once=True,
            use_container_width=True,
            format="wav",
            key="sales_voice_recorder",
        )
    with send_col:
        st.button(
            ":material/arrow_upward:",
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

            if is_light:
                # Use a styled static table in light mode so it cannot inherit a dark
                # grid theme from the browser/Streamlit settings.
                import pandas as pd
                dashboard_df = pd.DataFrame(rows)
                styled_dashboard = dashboard_df.style.set_table_styles([
                    {"selector": "table", "props": [
                        ("background-color", "#ffffff"),
                        ("color", "#172033"),
                        ("border-collapse", "collapse"),
                        ("width", "100%"),
                        ("border", "1px solid #e2e8f0"),
                    ]},
                    {"selector": "th", "props": [
                        ("background-color", "#f1f5f9"),
                        ("color", "#172033"),
                        ("font-weight", "600"),
                        ("text-align", "left"),
                        ("padding", "10px 12px"),
                        ("border", "1px solid #e2e8f0"),
                    ]},
                    {"selector": "td", "props": [
                        ("background-color", "#ffffff"),
                        ("color", "#172033"),
                        ("padding", "9px 12px"),
                        ("border", "1px solid #e2e8f0"),
                    ]},
                ]).set_properties(**{"background-color": "#ffffff", "color": "#172033"})
                st.table(styled_dashboard)
            else:
                st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No sales customers have been captured yet.")

    except Exception as exc:
        st.error("Could not load the sales dashboard.")
        st.caption(f"Dashboard detail: {type(exc).__name__}: {exc}")
        print("Dashboard error:", repr(exc))
else:
    st.warning("Sales dashboard is unavailable until the database connection works.")
