import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "ai_chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            intent VARCHAR(50) NOT NULL,
            category VARCHAR(100),
            location VARCHAR(100),
            quantity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()

    cursor.close()
    connection.close()


def save_lead(lead):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO leads (
            intent,
            category,
            location,
            quantity
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (
        lead["intent"],
        lead["category"],
        lead["location"],
        lead["quantity"]
    ))

    lead_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return lead_id


def get_all_leads():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            intent,
            category,
            location,
            quantity,
            created_at
        FROM leads
        ORDER BY created_at DESC;
    """)

    leads = cursor.fetchall()

    cursor.close()
    connection.close()

    return leads