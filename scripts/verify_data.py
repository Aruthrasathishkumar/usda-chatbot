import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "rd_chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Count total programs
cursor.execute("SELECT COUNT(*) FROM programs;")
count = cursor.fetchone()[0]
print(f"Total programs in database: {count}")

# Show name and category of each
cursor.execute("SELECT id, name, category FROM programs ORDER BY category, name;")
rows = cursor.fetchall()

print("\n--- All programs ---")
for row in rows:
    print(f"[{row[0]}] ({row[2]}) {row[1]}")

# Show the full text of one program to verify content
cursor.execute("SELECT * FROM programs WHERE id = 1;")
cols = [desc[0] for desc in cursor.description]
program = cursor.fetchone()
print(f"\n--- Full record for program ID 1 ---")
for col, val in zip(cols, program):
    print(f"{col}: {str(val)[:120]}")

cursor.close()
conn.close()