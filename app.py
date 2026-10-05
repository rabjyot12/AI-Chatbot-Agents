import os

import streamlit as st
from dotenv import load_dotenv

from database import (
    create_table,
    get_all_sales_customers,
    save_sales_customer,
)
from product_catalog import PRODUCTS
from sales_agent import process_sales_message

load_dotenv()

st.set_page_config(
    page_title="Telecom AI Sales Agent",
    page_icon="💬",
    layout="wide",
)

#styling

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

    .hero h1 {
        margin-bottom: 0.3rem;
    }

    .hero p {
        margin-bottom: 0;
        color: #dbeafe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#database initialization

try:
    create_table()
    db_ready = True
except Exception as exc:
    db_ready = False
    print("Database initialization error:", exc)

#session state initialization

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {
            "role": "assistant",
            "content": (
                "Hi! 👋 I'm your telecom solutions sales assistant. "
                "Tell me what you're trying to achieve and I'll help you find "
                "the right communication solution."
            ),
        }
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

#the sidebar contains the title, description, and product information

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
            {
                "role": "assistant",
                "content": (
                    "Hi! 👋 I'm your telecom solutions sales assistant. "
                    "What are you looking to achieve?"
                ),
            }
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
        st.rerun()

#header section with title and description

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

chat_col, lead_col = st.columns([2.1, 1])

#chat panel for conversation with the AI sales agent

with chat_col:
    st.subheader("Conversation")

    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Tell me what you need...")

    if user_input:
        result = process_sales_message(
            user_input,
            st.session_state.conversation_history,
            st.session_state.sales_state,
        )

        st.session_state.sales_state = result["state"]

        st.rerun()

#lead panel for capturing customer information and sending it to the sales team

with lead_col:
    st.subheader("Customer")

    state = st.session_state.sales_state

    with st.form("customer_form"):
        name = st.text_input("Name", value=state.get("name") or "")
        company = st.text_input("Company", value=state.get("company") or "")
        phone = st.text_input("Phone", value=state.get("phone") or "")
        email = st.text_input("Email", value=state.get("email") or "")
        requirement = st.text_area(
            "Requirement",
            value=state.get("requirement") or "",
        )
        interested_product = st.text_input(
            "Interested product",
            value=state.get("interested_product") or "",
        )
        expected_scale = st.text_input(
            "Expected scale",
            value=state.get("expected_scale") or "",
        )

        save_button = st.form_submit_button(
            "Send to Sales Team",
            use_container_width=True,
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
                st.error(
                    "The customer was collected but could not be saved."
                )
                print("Customer database error:", exc)

    if st.session_state.customer_saved:
        st.info("This customer has already been saved in the database.")

#brochure section for product information and download links

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

#admin/demo view

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
