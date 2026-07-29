-- ============================================================
-- Bank Transaction Fraud Analytics — Schema
-- Data source: "Bank Transaction Dataset for Fraud Detection"
-- by vala khorasani, Kaggle (see README for link/attribution).
-- ============================================================

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id            TEXT PRIMARY KEY,
    account_id                TEXT NOT NULL,
    transaction_amount        REAL NOT NULL,
    transaction_date          DATETIME NOT NULL,
    transaction_type          TEXT NOT NULL CHECK (transaction_type IN ('Debit','Credit')),
    location                  TEXT NOT NULL,
    device_id                 TEXT NOT NULL,
    ip_address                TEXT NOT NULL,
    merchant_id               TEXT NOT NULL,
    channel                   TEXT NOT NULL CHECK (channel IN ('ATM','Branch','Online')),
    customer_age              INTEGER NOT NULL,
    customer_occupation       TEXT NOT NULL,
    transaction_duration_sec  INTEGER NOT NULL,
    login_attempts            INTEGER NOT NULL,
    account_balance           REAL NOT NULL,
    previous_transaction_date DATETIME
);

CREATE INDEX idx_txn_account   ON transactions(account_id);
CREATE INDEX idx_txn_date      ON transactions(transaction_date);
CREATE INDEX idx_txn_channel   ON transactions(channel);
