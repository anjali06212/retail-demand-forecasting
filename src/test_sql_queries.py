import os
import sqlite3
import re

def run_sql_tests():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database", "retail_demand.db")
    sql_path = os.path.join(base_dir, "sql", "demand_queries.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(sql_path, 'r') as f:
        sql_content = f.read()

    # Split queries by semicolon
    raw_statements = sql_content.split(';')

    print("=" * 60)
    print("TESTING SQL DEMAND QUERIES")
    print("=" * 60)

    q_idx = 1
    for raw in raw_statements:
        # Strip comments
        lines = [line for line in raw.splitlines() if not line.strip().startswith('--')]
        cleaned = "\n".join(lines).strip()
        if not cleaned:
            continue

        try:
            cursor.execute(cleaned)
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description] if cursor.description else []
            print(f"\n[QUERY {q_idx}] Execution SUCCESS! Returned {len(rows)} rows.")
            print(f"Columns: {cols}")
            for r in rows[:3]:
                print("  ", r)
            q_idx += 1
        except Exception as e:
            print(f"\n[QUERY {q_idx}] ERROR:", e)
            q_idx += 1

    conn.close()

if __name__ == '__main__':
    run_sql_tests()
