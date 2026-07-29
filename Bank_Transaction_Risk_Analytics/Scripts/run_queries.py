"""
Runs every query in sql/analysis.sql against bank.db and prints
a preview of results — used to sanity-check the SQL, and can be
reused to export results for Power BI.
"""
import sqlite3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "bank.db"
ANALYSIS_SQL = ROOT / "sql" / "analysis.sql"

def split_queries(sql_text):
    # split on blank-line-separated blocks starting with a comment header
    blocks = re.split(r"\n\n(?=--)", sql_text.strip())
    # drop the file's leading title/comment block (no actual SQL statement in it)
    return [b.strip() for b in blocks if b.strip() and re.search(r"-- Q\d+", b)]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    sql_text = ANALYSIS_SQL.read_text()
    blocks = split_queries(sql_text)

    for i, block in enumerate(blocks, 1):
        title_match = re.search(r"-- (Q\d+.*)", block)
        title = title_match.group(1) if title_match else f"Query {i}"
        try:
            cur.execute(block)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            print(f"\n=== {title} ===")
            print(cols)
            for r in rows[:5]:
                print(r)
            print(f"... ({len(rows)} rows total)")
        except Exception as e:
            print(f"\n=== {title} ===")
            print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    main()
