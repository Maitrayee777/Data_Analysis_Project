"""
Loads data/bank_transactions.csv (real Kaggle dataset) into
SQLite (bank.db) using the schema in sql/schema.sql.

Run: python scripts/build_database.py
"""
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "bank.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
CSV_PATH = ROOT / "data" / "bank_transactions.csv"

COLUMN_MAP = {
    "TransactionID": "transaction_id",
    "AccountID": "account_id",
    "TransactionAmount": "transaction_amount",
    "TransactionDate": "transaction_date",
    "TransactionType": "transaction_type",
    "Location": "location",
    "DeviceID": "device_id",
    "IP Address": "ip_address",
    "MerchantID": "merchant_id",
    "Channel": "channel",
    "CustomerAge": "customer_age",
    "CustomerOccupation": "customer_occupation",
    "TransactionDuration": "transaction_duration_sec",
    "LoginAttempts": "login_attempts",
    "AccountBalance": "account_balance",
    "PreviousTransactionDate": "previous_transaction_date",
}

def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    df = pd.read_csv(CSV_PATH)
    df = df.rename(columns=COLUMN_MAP)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"Loaded {count} rows into 'transactions' at {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
