import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "rd_chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

def create_tables(cursor):
    """
    Creates the database tables if they don't already exist.
    
    What is a cursor?
    A cursor is like a pointer inside your database connection.
    You send SQL commands through the cursor, and it executes them.
    """
    
    # The programs table stores all USDA program information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programs (
            id          SERIAL PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT,
            description TEXT,
            eligibility TEXT,
            funding_info TEXT,
            how_to_apply TEXT,
            contact     TEXT,
            source_url  TEXT UNIQUE,
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)
    # SERIAL = auto-incrementing integer (1, 2, 3...)
    # PRIMARY KEY = unique identifier for each row
    # NOT NULL = this field must have a value
    # UNIQUE on source_url = prevents duplicate programs
    # DEFAULT NOW() = automatically records insertion time

    # The chat_history table stores every conversation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id              SERIAL PRIMARY KEY,
            session_id      TEXT,
            user_message    TEXT,
            bot_response    TEXT,
            programs_cited  TEXT[],
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)
    # TEXT[] = an array of text strings (list of program names cited)
    
    print("Tables created (or already existed).")

def seed_programs(cursor, programs):
    """
    Inserts program records into the programs table.
    Skips any program whose URL already exists (ON CONFLICT DO NOTHING).
    This means you can safely run this script multiple times.
    """
    inserted = 0
    skipped = 0
    
    for program in programs:
        cursor.execute("""
            INSERT INTO programs 
                (name, category, description, eligibility, 
                 funding_info, how_to_apply, contact, source_url)
            VALUES 
                (%(name)s, %(category)s, %(description)s, %(eligibility)s,
                 %(funding_info)s, %(how_to_apply)s, %(contact)s, %(source_url)s)
            ON CONFLICT (source_url) DO NOTHING;
        """, program)
        # %(name)s is a named placeholder — psycopg2 safely replaces it
        # with the value from the program dictionary.
        # This prevents SQL injection attacks.
        
        if cursor.rowcount == 1:
            inserted += 1
            print(f"  Inserted: {program['name']}")
        else:
            skipped += 1
            print(f"  Skipped (already exists): {program['name']}")
    
    return inserted, skipped

def main():
    print("=" * 60)
    print("USDA RD Chatbot — Database Seeder")
    print("=" * 60)
    
    # Step 1: Load programs from JSON file
    # os.path.dirname(__file__) = the folder this script is in
    # We go up one level (..) to reach the data/ folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'programs.json')
    
    with open(data_path, 'r', encoding='utf-8') as f:
        programs = json.load(f)
    
    print(f"\nLoaded {len(programs)} programs from programs.json")
    
    # Step 2: Connect to PostgreSQL
    print("\nConnecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        # conn is your database connection object
        # ** unpacks the dictionary as keyword arguments
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Check: Is PostgreSQL running? Is your password correct?")
        return
    
    # Step 3: Create tables and seed data
    try:
        with conn:                          # auto-commits on success
            with conn.cursor() as cursor:   # auto-closes cursor
                create_tables(cursor)
                print(f"\nInserting programs...")
                inserted, skipped = seed_programs(cursor, programs)
        
        print(f"\nDone!")
        print(f"  Inserted: {inserted} new programs")
        print(f"  Skipped:  {skipped} duplicates")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    # This block only runs when you execute the file directly
    # e.g. python seed_data.py
    # It does NOT run when this file is imported by another file
    main()