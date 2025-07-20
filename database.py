import sqlite3
import json
from datetime import datetime


def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()

    # Таблица пользователей (если нужна аутентификация)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Таблица чатов
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 session_id TEXT UNIQUE,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Таблица сообщений
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 chat_id INTEGER,
                 role TEXT CHECK(role IN ('user', 'bot')),
                 content TEXT,
                 sources TEXT,
                 response_time REAL,
                 feedback TEXT,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(chat_id) REFERENCES chats(id))''')

    conn.commit()
    conn.close()


def add_chat(session_id, user_id=None):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("INSERT INTO chats (session_id, user_id) VALUES (?, ?)",
              (session_id, user_id))
    chat_id = c.lastrowid
    conn.commit()
    conn.close()
    return chat_id


def add_message(chat_id, role, content, sources=None, response_time=None):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()

    sources_json = json.dumps(sources) if sources else None

    c.execute('''INSERT INTO messages 
                 (chat_id, role, content, sources, response_time) 
                 VALUES (?, ?, ?, ?, ?)''',
              (chat_id, role, content, sources_json, response_time))

    message_id = c.lastrowid
    conn.commit()
    conn.close()
    return message_id


def update_feedback(message_id, feedback):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("UPDATE messages SET feedback = ? WHERE id = ?",
              (feedback, message_id))
    conn.commit()
    conn.close()


def get_chat_history(chat_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT role, content, sources, response_time, id FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
              (chat_id,))
    rows = c.fetchall()

    history = []
    for row in rows:
        history.append({
            "role": row[0],
            "content": row[1],
            "sources": json.loads(row[2]) if row[2] else [],
            "response_time": row[3],
            "id": row[4]
        })

    conn.close()
    return history


def get_chat_id_by_session(session_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT id FROM chats WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
