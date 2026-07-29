# Bank Transaction Analytics (Kaggle Dataset)

Analytics project on a **real, publicly published Kaggle dataset** of bank transactions — built with **Python, SQL, and Power BI** — covering transaction behavior, occupation/channel patterns, and a rule-based risk-flagging layer.

## Data source & honest provenance

- Dataset: *Bank Transaction Dataset for Fraud Detection* by vala khorasani, published on Kaggle:
  https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection
- 2,512 transaction records, 16 columns, no missing values.
- **Important:** the dataset's own author describes it as generated to simulate realistic banking scenarios, not as real captured bank customer data. This is normal for public banking datasets — actual customer transaction data is confidential/regulated and isn't published. What makes this different from a fully self-generated dataset is that it's a real, independently-published, third-party dataset with its own Kaggle presence and community usage — I didn't write the generator or choose the values.
- The dataset has **no fraud label**. Any "risk" scoring in this project (see `sql/analysis.sql` Q6–Q9) is a rule-based heuristic built on observable signals (login attempts, transaction size relative to the account's own average) — described accurately as a heuristic screen, not a trained or validated fraud-detection model.
- **Data quality finding**: `PreviousTransactionDate` postdates `TransactionDate` for all 2,512 rows — the column name implies a chronological "prior transaction" but the values don't behave that way. This is documented and worked around in `scripts/eda_and_export.py` and `sql/analysis.sql` (Q7 derives true sequence order from `TransactionDate` itself instead of trusting that column).

## Project structure

```
bank-analytics-v2/
├── data/
│   ├── bank_transactions.csv    # the raw Kaggle dataset
│   └── powerbi_export.csv       # cleaned + risk-scored, ready for Power BI import
├── sql/
│   ├── schema.sql                # table definition
│   └── analysis.sql              # 10 business-question queries
├── scripts/
│   ├── build_database.py         # loads CSV into SQLite (bank.db)
│   ├── run_queries.py            # runs & sanity-checks analysis.sql
│   └── eda_and_export.py         # cleaning, data-quality checks, charts, Power BI export
├── charts/                       # EDA chart outputs (PNG)
└── requirements.txt
```

## Business questions answered (see `sql/analysis.sql`)

1. Transaction volume and value by channel (ATM / Branch / Online)
2. Average transaction amount and balance by customer occupation
3. Top 10 accounts by total transaction value (window function: `RANK()`)
4. Balance trend per account over time (window function: `LAG()`)
5. Monthly transaction volume and month-over-month growth
6. Suspicious login activity (3+ login attempts per transaction)
7. Unusually fast repeat transactions per account (true sequence via `LAG()` on `transaction_date`, not the unreliable `PreviousTransactionDate` column)
8. Statistical outliers — transactions >2 standard deviations above their channel's mean (z-score)
9. Combined rule-based risk score per account
10. Location-wise transaction concentration

## How to run

```bash
pip install -r requirements.txt

python scripts/build_database.py    # builds bank.db from the CSV
python scripts/run_queries.py       # runs all analysis.sql queries, prints results
python scripts/eda_and_export.py    # cleaning, data-quality checks, charts/, Power BI export
```

To run the SQL directly:
```bash
sqlite3 bank.db < sql/analysis.sql
```

## Power BI dashboard

Power BI Desktop isn't scriptable in this build environment, so the `.pbix` isn't auto-generated — `data/powerbi_export.csv` is a cleaned, risk-scored flat file ready to import directly. To build the dashboard:

1. Import `data/powerbi_export.csv` (Get Data → Text/CSV).
2. Suggested visuals:
   - **KPI cards**: total transactions, total value, average transaction size, count of risk_score > 0
   - **Bar chart**: transaction count/value by `channel`
   - **Line chart**: transaction volume by `year_month`
   - **Bar chart**: average transaction amount by `customer_occupation`
   - **Table**: top accounts by risk_score (matches SQL Q9)
   - **Histogram/bar**: `login_attempts` distribution
3. Add slicers for `channel` and `customer_occupation`.

## Tech stack

Python (Pandas, NumPy, Matplotlib) · SQL (SQLite — schema design, joins, CTEs, window functions, rule-based risk scoring) · Power BI (dashboarding on the exported dataset)

## License / attribution

Underlying dataset licensed per its Kaggle page (Apache 2.0 per the dataset's listing). Please retain attribution to the original author (vala khorasani) if you redistribute the raw data.

