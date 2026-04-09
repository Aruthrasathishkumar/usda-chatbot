"""
database.py — PostgreSQL helper functions for FastAPI

Why a separate file for database logic?
Your main.py handles HTTP requests. Your database.py handles
data. Keeping them separate means if you change your database
(e.g. switch to MySQL), you only change this file — not main.py.
This is called "separation of concerns."
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "rd_chatbot"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}


def get_connection():
    """
    Creates and returns a new PostgreSQL connection.
    
    Why create a new connection each time instead of keeping one open?
    For a small project like this, creating a connection per request
    is simple and reliable. A persistent connection can go stale or
    drop unexpectedly. For high-traffic production apps you would use
    a connection pool (e.g. asyncpg), but that adds complexity we
    do not need right now.
    """
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    # RealDictCursor makes each database row come back as a dictionary
    # instead of a plain tuple. So row["name"] works instead of row[0].


def get_all_programs():
    """
    Fetches all USDA programs from PostgreSQL.
    Returns a list of dictionaries.
    
    This is called by GET /api/programs in main.py.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id, name, category, description,
                    eligibility, funding_info, how_to_apply,
                    contact, source_url, created_at
                FROM programs
                ORDER BY category, name;
            """)
            # fetchall() returns a list of RealDictRow objects
            # list() converts them to plain dicts for JSON serialization
            programs = list(cursor.fetchall())
            
            # Convert datetime objects to strings for JSON
            # JSON does not understand Python datetime objects
            for program in programs:
                if program.get("created_at"):
                    program["created_at"] = str(program["created_at"])
            
            return programs
    finally:
        # always close the connection, even if an error occurred
        conn.close()


def get_program_by_id(program_id: int):
    """
    Fetches a single program by its ID.
    Returns a dictionary or None if not found.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM programs WHERE id = %s;",
                (program_id,)
                # Note the comma: (program_id,) is a tuple
                # psycopg2 requires parameters as a tuple, never
                # as a plain value — this prevents SQL injection
            )
            program = cursor.fetchone()
            if program:
                if program.get("created_at"):
                    program["created_at"] = str(program["created_at"])
                return dict(program)
            return None
    finally:
        conn.close()


def save_chat_history(session_id: str, user_message: str,
                      bot_response: str, programs_cited: list):
    """
    Saves a conversation turn to the chat_history table.
    
    Why save chat history?
    - Analytics: which programs are asked about most?
    - Debugging: what questions is the bot answering poorly?
    - Future feature: show users their conversation history
    
    Args:
        session_id:     unique ID for this chat session
        user_message:   what the user asked
        bot_response:   what Mistral answered
        programs_cited: list of program names used in the answer
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat_history 
                    (session_id, user_message, bot_response, programs_cited)
                VALUES 
                    (%s, %s, %s, %s);
            """, (
                session_id,
                user_message,
                bot_response,
                programs_cited  # psycopg2 converts Python list → PostgreSQL TEXT[]
            ))
        conn.commit()
    finally:
        conn.close()


def get_chat_stats():
    """
    Returns basic analytics about chatbot usage.
    Called by GET /api/stats in main.py.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total_conversations FROM chat_history;")
            total = cursor.fetchone()["total_conversations"]
            
            cursor.execute("SELECT COUNT(DISTINCT session_id) as unique_sessions FROM chat_history;")
            sessions = cursor.fetchone()["unique_sessions"]
            
            cursor.execute("SELECT COUNT(*) as total_programs FROM programs;")
            programs = cursor.fetchone()["total_programs"]
            
            return {
                "total_conversations": total,
                "unique_sessions": sessions,
                "total_programs": programs
            }
    finally:
        conn.close()