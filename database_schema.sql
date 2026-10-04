CREATE TABLE IF NOT EXISTS sales_prospects (
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
