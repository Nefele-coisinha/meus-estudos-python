import sqlite3
import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta
import hmac
import re

# ================= CONFIG =================
DB_NAME = "auth.db"
PEPPER = b"super_secret_pepper_123"
MAX_ATTEMPTS = 5
LOCK_TIME = 15  # minutos
TOKEN_EXPIRY = 10  # minutos

# ================= DATABASE =================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash BLOB,
            salt BLOB,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TEXT,
            created_at TEXT
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            expires_at TEXT
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            expires_at TEXT
        )
        """)
        self.conn.commit()

db = Database()

# ================= SECURITY =================
def hash_password(password: str, salt: bytes) -> bytes:
    pwd = password.encode() + PEPPER
    return hashlib.pbkdf2_hmac("sha256", pwd, salt, 200000)

def verify_password(stored, provided, salt):
    new_hash = hash_password(provided, salt)
    return hmac.compare_digest(stored, new_hash)

def strong_password(password):
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
    return re.match(pattern, password)

# ================= AUTH SYSTEM =================
class Auth:

    def register(self, username, email, password):
        username = username.lower().strip()
        email = email.lower().strip()

        if not strong_password(password):
            return "Senha fraca!"

        salt = os.urandom(16)
        hashed = hash_password(password, salt)

        try:
            db.conn.execute("""
            INSERT INTO users (username, email, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (username, email, hashed, salt, datetime.now().isoformat()))
            db.conn.commit()
            return "Usuário criado!"
        except:
            return "Usuário/email já existe!"

    def is_locked(self, user):
        if user["locked_until"]:
            if datetime.now() < datetime.fromisoformat(user["locked_until"]):
                return True
        return False

    def login(self, username, password):
        cursor = db.conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()

        # Anti-enumeração
        fake_salt = os.urandom(16)
        fake_hash = hash_password(password, fake_salt)

        if not user:
            hmac.compare_digest(fake_hash, fake_hash)
            return "Credenciais inválidas"

        user_dict = {
            "id": user[0],
            "password": user[3],
            "salt": user[4],
            "failed": user[5],
            "locked_until": user[6]
        }

        if self.is_locked(user_dict):
            return "Conta bloqueada"

        if verify_password(user_dict["password"], password, user_dict["salt"]):
            db.conn.execute("""
            UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?
            """, (user_dict["id"],))
            db.conn.commit()

            return self.create_session(user_dict["id"])

        else:
            attempts = user_dict["failed"] + 1
            lock_time = None

            if attempts >= MAX_ATTEMPTS:
                lock_time = (datetime.now() + timedelta(minutes=LOCK_TIME)).isoformat()

            db.conn.execute("""
            UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?
            """, (attempts, lock_time, user_dict["id"]))
            db.conn.commit()

            return "Credenciais inválidas"

    def create_session(self, user_id):
        token = secrets.token_hex(32)
        expiry = datetime.now() + timedelta(hours=1)

        db.conn.execute("""
        INSERT INTO sessions VALUES (?, ?, ?)
        """, (token, user_id, expiry.isoformat()))
        db.conn.commit()

        return f"Login feito! Token: {token}"

    def request_reset(self, email):
        cursor = db.conn.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return "Se existir, enviamos o reset"

        token = secrets.token_hex(32)
        expiry = datetime.now() + timedelta(minutes=TOKEN_EXPIRY)

        db.conn.execute("""
        INSERT INTO reset_tokens VALUES (?, ?, ?)
        """, (token, user[0], expiry.isoformat()))
        db.conn.commit()

        return f"Token de reset: {token}"

    def reset_password(self, token, new_password):
        cursor = db.conn.execute(
            "SELECT user_id, expires_at FROM reset_tokens WHERE token=?",
            (token,)
        )
        data = cursor.fetchone()

        if not data:
            return "Token inválido"

        if datetime.now() > datetime.fromisoformat(data[1]):
            return "Token expirado"

        salt = os.urandom(16)
        hashed = hash_password(new_password, salt)

        db.conn.execute("""
        UPDATE users SET password_hash=?, salt=? WHERE id=?
        """, (hashed, salt, data[0]))

        db.conn.execute("DELETE FROM reset_tokens WHERE token=?", (token,))
        db.conn.commit()

        return "Senha redefinida!"

# ================= TESTE =================
auth = Auth()

print(auth.register("teste", "teste@email.com", "Senha@123"))
print(auth.login("teste", "Senha@123"))