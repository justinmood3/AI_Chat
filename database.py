import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Migration: add thread_id, media_type, and media_url to chats if not exists
try:
    cursor.execute("PRAGMA table_info(chats)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'thread_id' not in columns:
        cursor.execute("ALTER TABLE chats ADD COLUMN thread_id INTEGER")
    if 'media_type' not in columns:
        cursor.execute("ALTER TABLE chats ADD COLUMN media_type TEXT")
    if 'media_url' not in columns:
        cursor.execute("ALTER TABLE chats ADD COLUMN media_url TEXT")
    # For existing chats, create default threads if needed
    if 'thread_id' not in columns:
        cursor.execute("SELECT DISTINCT user_id FROM chats WHERE thread_id IS NULL")
        users = cursor.fetchall()
        for (user_id,) in users:
            cursor.execute("INSERT INTO threads (user_id, title) VALUES (?, ?)", (user_id, "Old Chats"))
            thread_id = cursor.lastrowid
            cursor.execute("UPDATE chats SET thread_id = ? WHERE user_id = ? AND thread_id IS NULL", (thread_id, user_id))
except:
    pass  # Table might not exist yet

# Add user_id to uploads if not exists
try:
    cursor.execute("PRAGMA table_info(uploads)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE uploads ADD COLUMN user_id INTEGER")
except:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE,
    name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER,
    user_message TEXT,
    ai_reply TEXT,
    media_type TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    key TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

conn.commit()

def save_user_google(google_id, name, email):
    cursor.execute(
        "INSERT OR IGNORE INTO users (google_id, name, email) VALUES (?, ?, ?)",
        (google_id, name, email)
    )
    conn.commit()
    cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
    return cursor.fetchone()[0]

def save_user_email(name, email, password):
    import sqlite3 as sqlite3_module
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
    except sqlite3_module.IntegrityError:
        cursor.execute(
            "UPDATE users SET name = ?, password_hash = ? WHERE email = ?",
            (name, password_hash, email)
        )
        conn.commit()
    user_data = get_user_by_email(email)
    return user_data[0]

def get_user_by_email(email):
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

def get_user_by_id(user_id):
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def check_password(user_id, password):
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    hash = cursor.fetchone()
    if hash:
        return check_password_hash(hash[0], password)
    return False

def save_chat(thread_id, user_message, ai_reply, media_type=None, media_url=None):
    cursor.execute(
        "INSERT INTO chats (thread_id, user_message, ai_reply, media_type, media_url) VALUES (?, ?, ?, ?, ?)",
        (thread_id, user_message, ai_reply, media_type, media_url)
    )
    conn.commit()

def get_chats(thread_id):
    cursor.execute("SELECT user_message, ai_reply, media_type, media_url FROM chats WHERE thread_id = ? ORDER BY id DESC", (thread_id,))
    return cursor.fetchall()

def create_thread(user_id, title="New Chat"):
    cursor.execute(
        "INSERT INTO threads (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conn.commit()
    return cursor.lastrowid

def get_threads(user_id):
    cursor.execute("SELECT id, title, created_at FROM threads WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    return cursor.fetchall()

def get_thread(thread_id):
    cursor.execute("SELECT id, title FROM threads WHERE id = ?", (thread_id,))
    return cursor.fetchone()

def save_user_data(user_id, key, value):
    cursor.execute(
        "INSERT OR REPLACE INTO user_data (user_id, key, value) VALUES (?, ?, ?)",
        (user_id, key, value)
    )
    conn.commit()

def get_user_data(user_id, key=None):
    if key:
        cursor.execute("SELECT value FROM user_data WHERE user_id = ? AND key = ?", (user_id, key))
        result = cursor.fetchone()
        return result[0] if result else None
    else:
        cursor.execute("SELECT key, value FROM user_data WHERE user_id = ?", (user_id,))
        return cursor.fetchall()