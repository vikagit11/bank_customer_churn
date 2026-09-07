CREATE TABLE clients (
    customer_id INTEGER PRIMARY KEY,
    row_number INTEGER,
    surname VARCHAR(100),
    credit_score INTEGER,
    geography VARCHAR(50),
    gender VARCHAR(20),
    age INTEGER,
    tenure INTEGER,
    balance DOUBLE PRECISION,
    num_of_products INTEGER,
    has_cr_card INTEGER,
    is_active_member INTEGER,
    estimated_salary DOUBLE PRECISION,
    exited INTEGER,
    complain INTEGER,
    satisfaction_score INTEGER,
    card_type VARCHAR(50),
    point_earned INTEGER
);
COPY  clients
FROM '/docker-entrypoint-initdb.d/clients.csv'
WITH (FORMAT csv, HEADER true);