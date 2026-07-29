-- ============================================================
-- Bank Transaction Analytics — Business Questions
-- Run against bank.db (SQLite), built from the real Kaggle
-- "Bank Transaction Dataset for Fraud Detection" data.
--
-- NOTE: the raw dataset has NO fraud label. Q6–Q9 below build a
-- rule-based risk score from observable signals (large amount,
-- repeated login attempts, unusually fast repeat transactions).
-- This is a heuristic, not a trained/validated fraud model —
-- described accurately as such, not oversold as "fraud detection".
-- ============================================================

-- Q1: Transaction volume and total value by channel
SELECT
    channel,
    COUNT(*)                         AS txn_count,
    ROUND(SUM(transaction_amount),2) AS total_value,
    ROUND(AVG(transaction_amount),2) AS avg_value
FROM transactions
GROUP BY channel
ORDER BY total_value DESC;


-- Q2: Average transaction amount and balance by customer occupation
SELECT
    customer_occupation,
    COUNT(*)                          AS txn_count,
    ROUND(AVG(transaction_amount), 2) AS avg_txn_amount,
    ROUND(AVG(account_balance), 2)    AS avg_balance
FROM transactions
GROUP BY customer_occupation
ORDER BY avg_txn_amount DESC;


-- Q3: Top 10 accounts by total transaction value (window function: RANK)
WITH account_totals AS (
    SELECT
        account_id,
        COUNT(*)                          AS txn_count,
        ROUND(SUM(transaction_amount), 2) AS total_value
    FROM transactions
    GROUP BY account_id
)
SELECT
    account_id,
    txn_count,
    total_value,
    RANK() OVER (ORDER BY total_value DESC) AS value_rank
FROM account_totals
ORDER BY value_rank
LIMIT 10;


-- Q4: Balance trend per account over time (window function, ordered by date)
-- Shows how a given account's reported balance moved across its transactions.
SELECT
    account_id,
    transaction_date,
    transaction_amount,
    account_balance,
    LAG(account_balance) OVER (
        PARTITION BY account_id ORDER BY transaction_date
    ) AS prev_balance,
    account_balance - LAG(account_balance) OVER (
        PARTITION BY account_id ORDER BY transaction_date
    ) AS balance_change
FROM transactions
WHERE account_id = (SELECT account_id FROM transactions ORDER BY account_id LIMIT 1)
ORDER BY transaction_date;


-- Q5: Monthly transaction volume trend + month-over-month growth (CTE + LAG)
WITH monthly AS (
    SELECT
        strftime('%Y-%m', transaction_date) AS month,
        COUNT(*) AS txn_count,
        ROUND(SUM(transaction_amount), 2) AS total_value
    FROM transactions
    GROUP BY month
)
SELECT
    month,
    txn_count,
    total_value,
    ROUND(
        100.0 * (total_value - LAG(total_value) OVER (ORDER BY month))
        / NULLIF(LAG(total_value) OVER (ORDER BY month), 0), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- Q6: Suspicious login activity — transactions with 3+ login attempts
SELECT
    transaction_id,
    account_id,
    login_attempts,
    transaction_amount,
    channel,
    transaction_date
FROM transactions
WHERE login_attempts >= 3
ORDER BY login_attempts DESC, transaction_amount DESC;


-- Q7: Unusually fast repeat transactions on the same account (CTE)
-- NOTE: the raw column `previous_transaction_date` is unreliable for this —
-- in this dataset it postdates `transaction_date` for every single row
-- (likely a last-login/review timestamp, not a chronological prior
-- transaction, despite its name). Instead, we derive true sequence order
-- from transaction_date itself using LAG.
WITH ordered AS (
    SELECT
        transaction_id,
        account_id,
        transaction_date,
        LAG(transaction_date) OVER (
            PARTITION BY account_id ORDER BY transaction_date
        ) AS prev_txn_date
    FROM transactions
),
gaps AS (
    SELECT
        transaction_id,
        account_id,
        transaction_date,
        prev_txn_date,
        (julianday(transaction_date) - julianday(prev_txn_date)) * 24 AS hours_since_prev
    FROM ordered
    WHERE prev_txn_date IS NOT NULL
)
SELECT *
FROM gaps
ORDER BY hours_since_prev ASC
LIMIT 15;


-- Q8: Statistical outliers — transactions more than 2 std. deviations
-- above the mean amount for their channel (z-score style anomaly flag)
WITH channel_stats AS (
    SELECT
        channel,
        AVG(transaction_amount)                                   AS mean_amt,
        AVG(transaction_amount * transaction_amount)
            - AVG(transaction_amount) * AVG(transaction_amount)   AS variance_amt
    FROM transactions
    GROUP BY channel
)
SELECT
    t.transaction_id,
    t.account_id,
    t.channel,
    t.transaction_amount,
    ROUND(cs.mean_amt, 2) AS channel_avg,
    ROUND((t.transaction_amount - cs.mean_amt) / SQRT(cs.variance_amt), 2) AS z_score
FROM transactions t
JOIN channel_stats cs ON t.channel = cs.channel
WHERE t.transaction_amount > cs.mean_amt + 2 * SQRT(cs.variance_amt)
ORDER BY z_score DESC
LIMIT 15;


-- Q9: Combined rule-based risk score per account
-- Points: +1 per txn with login_attempts >= 3, +1 per txn > 3x that
-- account's own average amount. Accounts scoring high are worth review
-- — this is a heuristic screen, not a validated fraud model.
WITH account_avg AS (
    SELECT account_id, AVG(transaction_amount) AS avg_amt
    FROM transactions
    GROUP BY account_id
),
flags AS (
    SELECT
        t.account_id,
        SUM(CASE WHEN t.login_attempts >= 3 THEN 1 ELSE 0 END) AS login_flags,
        SUM(CASE WHEN t.transaction_amount > 3 * a.avg_amt THEN 1 ELSE 0 END) AS amount_flags
    FROM transactions t
    JOIN account_avg a ON t.account_id = a.account_id
    GROUP BY t.account_id
)
SELECT
    account_id,
    login_flags,
    amount_flags,
    (login_flags + amount_flags) AS risk_score
FROM flags
WHERE (login_flags + amount_flags) > 0
ORDER BY risk_score DESC
LIMIT 15;


-- Q10: Location-wise transaction concentration
SELECT
    location,
    COUNT(*) AS txn_count,
    ROUND(SUM(transaction_amount), 2) AS total_value,
    COUNT(DISTINCT account_id) AS unique_accounts
FROM transactions
GROUP BY location
ORDER BY txn_count DESC
LIMIT 15;
