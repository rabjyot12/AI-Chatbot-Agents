CREATE TABLE IF NOT EXISTS sales_customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150),
    company VARCHAR(200),
    phone VARCHAR(50),
    email VARCHAR(255),
    requirement TEXT,
    interested_product VARCHAR(100),
    expected_scale VARCHAR(100),
    conversation_summary TEXT,
    status VARCHAR(50) DEFAULT 'new',
    sales_followup BOOLEAN DEFAULT FALSE,
    channel VARCHAR(30) DEFAULT 'website',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);