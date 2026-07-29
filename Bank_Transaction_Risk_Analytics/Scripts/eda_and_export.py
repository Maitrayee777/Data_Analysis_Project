"""
EDA on the real bank transactions dataset:
 - validates/cleans data
 - documents the PreviousTransactionDate data-quality issue
 - produces charts (saved to charts/)
 - exports a Power BI-ready flat CSV with a derived risk_score column

Run: python scripts/eda_and_export.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)

def load():
    df = pd.read_csv(DATA / "bank_transactions.csv",
                      parse_dates=["TransactionDate", "PreviousTransactionDate"])
    return df

def validate_and_clean(df):
    before = len(df)
    dupes = df.duplicated(subset="TransactionID").sum()
    nulls = df.isnull().sum().sum()
    df = df.drop_duplicates(subset="TransactionID").dropna()

    # Document the PreviousTransactionDate quirk rather than silently using it
    bad_order = (df["TransactionDate"] < df["PreviousTransactionDate"]).sum()
    print(f"Cleaning report:")
    print(f"  Rows before: {before}, duplicates removed: {dupes}, null rows removed: {before - len(df) - dupes}")
    print(f"  Rows where PreviousTransactionDate > TransactionDate: {bad_order}/{len(df)} "
          f"({'ALL rows — treat this column as unreliable for sequencing' if bad_order == len(df) else 'partial'})")
    return df

def add_risk_score(df):
    avg_by_account = df.groupby("AccountID")["TransactionAmount"].transform("mean")
    login_flag = (df["LoginAttempts"] >= 3).astype(int)
    amount_flag = (df["TransactionAmount"] > 3 * avg_by_account).astype(int)
    df["risk_score"] = login_flag + amount_flag
    return df

def eda_charts(df):
    # Transaction amount distribution by channel
    plt.figure(figsize=(8, 4.5))
    df.boxplot(column="TransactionAmount", by="Channel", grid=False)
    plt.title("Transaction Amount by Channel")
    plt.suptitle("")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.savefig(CHARTS / "amount_by_channel.png", dpi=130)
    plt.close()

    # Monthly transaction volume
    monthly = df.set_index("TransactionDate").resample("ME").size()
    plt.figure(figsize=(9, 4.5))
    monthly.plot(kind="bar", color="#1F3864")
    plt.title("Monthly Transaction Count")
    plt.ylabel("Transactions")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(CHARTS / "monthly_volume.png", dpi=130)
    plt.close()

    # Occupation vs avg transaction amount
    plt.figure(figsize=(7, 4.5))
    df.groupby("CustomerOccupation")["TransactionAmount"].mean().sort_values().plot(
        kind="barh", color="#2E6F40")
    plt.title("Average Transaction Amount by Occupation")
    plt.xlabel("Average Amount")
    plt.tight_layout()
    plt.savefig(CHARTS / "avg_amount_by_occupation.png", dpi=130)
    plt.close()

    # Login attempts distribution
    plt.figure(figsize=(7, 4.5))
    df["LoginAttempts"].value_counts().sort_index().plot(kind="bar", color="#B22222")
    plt.title("Login Attempts Distribution")
    plt.xlabel("Login Attempts")
    plt.ylabel("Transaction Count")
    plt.tight_layout()
    plt.savefig(CHARTS / "login_attempts_distribution.png", dpi=130)
    plt.close()

    # Risk score distribution
    plt.figure(figsize=(6, 4.5))
    df["risk_score"].value_counts().sort_index().plot(kind="bar", color="#8B4513")
    plt.title("Rule-Based Risk Score Distribution")
    plt.xlabel("Risk Score (0-2)")
    plt.ylabel("Transaction Count")
    plt.tight_layout()
    plt.savefig(CHARTS / "risk_score_distribution.png", dpi=130)
    plt.close()

    print(f"Saved 5 charts to {CHARTS}")

def export_for_powerbi(df):
    out = df.rename(columns={
        "TransactionID": "transaction_id", "AccountID": "account_id",
        "TransactionAmount": "transaction_amount", "TransactionDate": "transaction_date",
        "TransactionType": "transaction_type", "Location": "location",
        "Channel": "channel", "CustomerAge": "customer_age",
        "CustomerOccupation": "customer_occupation", "LoginAttempts": "login_attempts",
        "AccountBalance": "account_balance",
    })
    out["year_month"] = out["transaction_date"].dt.to_period("M").astype(str)
    out_path = DATA / "powerbi_export.csv"
    out.to_csv(out_path, index=False)
    print(f"Power BI-ready export saved to {out_path} ({len(out)} rows)")

def main():
    df = load()
    df = validate_and_clean(df)
    df = add_risk_score(df)
    eda_charts(df)
    export_for_powerbi(df)

if __name__ == "__main__":
    main()
