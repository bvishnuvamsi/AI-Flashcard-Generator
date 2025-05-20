import sqlite3
from sqlite3 import Connection
import streamlit as st

DB_PATH = "flashcards.db"

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_flashcards(flashcards):
    create_table()

    if 'cleared_old_flashcards' not in st.session_state:
        # Delete old data only once per session
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM flashcards')
        conn.commit()
        conn.close()
        st.session_state.cleared_old_flashcards = True
        print("[DB] Cleared old flashcards")

    conn = get_connection()
    cursor = conn.cursor()
    saved_count = 0
    skipped_count = 0

    for i, card in enumerate(flashcards):
        # Safeguard: check for expected keys and non-empty values
        if isinstance(card, dict) and card.get('question') and card.get('answer'):
            cursor.execute('''
                INSERT INTO flashcards (question, answer)
                VALUES (?, ?)
            ''', (card['question'], card['answer']))
            saved_count += 1
        else:
            skipped_count += 1
            print(f"[DB] Skipped flashcard #{i+1} - Invalid format: {card}")

    conn.commit()
    conn.close()

    print(f"[DB] Saved {saved_count} flashcards")
    if skipped_count > 0:
        print(f"[DB] Skipped {skipped_count} invalid flashcards")

def save_flashcard_to_db(flashcard):
    """
    Save a single flashcard to the database without clearing old flashcards.
    """
    create_table()
    if not (isinstance(flashcard, dict) and flashcard.get('question') and flashcard.get('answer')):
        print(f"[DB] Invalid flashcard, not saved: {flashcard}")
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flashcards (question, answer)
        VALUES (?, ?)
    ''', (flashcard['question'], flashcard['answer']))
    conn.commit()
    conn.close()
    print("[DB] Saved 1 flashcard")
    return True

def get_saved_flashcards():
    create_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT question, answer FROM flashcards')
    rows = cursor.fetchall()
    conn.close()
    print(f"[DB] Retrieved {len(rows)} saved flashcards")
    return [{'question': r[0], 'answer': r[1]} for r in rows]
