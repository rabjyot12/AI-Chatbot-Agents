import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st

    if hasattr(st, "secrets") and st.secrets:
        secrets = st.secrets
    else:
        secrets = {}
except Exception:
    secrets = {}

DB_CONFIG = {
    "host": secrets.get("DB_HOST", os.getenv("DB_HOST", "localhost")),
    "database": secrets.get("DB_NAME", os.getenv("DB_NAME", "ai_chatbot")),
    "user": secrets.get("DB_USER", os.getenv("DB_USER", "postgres")),
    "password": secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD")),
    "port": secrets.get("DB_PORT", os.getenv("DB_PORT", "5432")),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS onboarding (
            id SERIAL PRIMARY KEY,
            company_email VARCHAR(255),
            gst_status VARCHAR(30) DEFAULT 'pending',
            pan_status VARCHAR(30) DEFAULT 'pending',
            aadhaar_status VARCHAR(30) DEFAULT 'pending',
            msme_required BOOLEAN DEFAULT FALSE,
            msme_status VARCHAR(30) DEFAULT 'not_required',
            onboarding_status VARCHAR(30) DEFAULT 'incomplete',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150),
            company VARCHAR(200),
            phone VARCHAR(50),
            email VARCHAR(255),
            requirement TEXT,
            interested_product VARCHAR(100),
            expected_scale VARCHAR(100),
            sales_followup BOOLEAN DEFAULT FALSE,
            channel VARCHAR(30) DEFAULT 'website',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()




def save_onboarding(onboarding):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO onboarding (
            company_email,
            gst_status,
            pan_status,
            aadhaar_status,
            msme_required,
            msme_status,
            onboarding_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        onboarding["company_email"],
        onboarding["gst_status"],
        onboarding["pan_status"],
        onboarding["aadhaar_status"],
        onboarding["msme_required"],
        onboarding["msme_status"],
        onboarding["onboarding_status"],
    ))

    onboarding_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()
    return onboarding_id


def get_all_onboarding():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            company_email,
            gst_status,
            pan_status,
            aadhaar_status,
            msme_required,
            msme_status,
            onboarding_status,
            created_at
        FROM onboarding
        ORDER BY created_at DESC;
    """)

    onboarding_records = cursor.fetchall()
    cursor.close()
    connection.close()
    return onboarding_records


def save_sales_customer(customer, channel="website"):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sales_customers (
            name,
            company,
            phone,
            email,
            requirement,
            interested_product,
            expected_scale,
            sales_followup,
            channel
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        customer.get("name"),
        customer.get("company"),
        customer.get("phone"),
        customer.get("email"),
        customer.get("requirement"),
        customer.get("interested_product"),
        customer.get("expected_scale"),
        customer.get("sales_followup", False),
        channel,
    ))

    customer_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return customer_id


def get_all_sales_customers():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            phone,
            email,
            requirement,
            interested_product,
            expected_scale,
            sales_followup,
            channel,
            created_at
        FROM sales_customers
        ORDER BY created_at DESC;
    """)

    customers = cursor.fetchall()
    cursor.close()
    connection.close()

    return customers
