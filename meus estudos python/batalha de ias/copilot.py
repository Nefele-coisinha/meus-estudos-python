#!/usr/bin/env python3
"""
Sistema de login simples e seguro em Python (SQLite, PBKDF2, tokens, lockout).
Sem dependências externas.
"""

import sqlite3
import hashlib
import secrets
import hmac
import time
import datetime
import re

DB = "auth.db"
PBKDF2_ITER = 200_000
SALT_BYTES = 16
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24 horas
RESET_TOKEN_TTL = 60 * 30  # 30 minutos
MAX_FAILED = 5
LOCKOUT_BASE_SECONDS = 60  # 1 minuto base

_username_re = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

def _now_ts():
    return int(time.time())

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            salt BLOB NOT NULL,
            pw_hash BLOB NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            lock_until INTEGER DEFAULT 0,
            reset_token TEXT,
            reset_expiry INTEGER
        )
        """)
        conn.commit()

def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITER, dklen=32)

def create_user(username: str, password: str) -> bool:
    if not _username_re.match(username):
        raise ValueError("Nome de usuário inválido. Use 3-32 chars alfanuméricos e _.-")
    if len(password) < 8:
        raise ValueError("Senha muito curta. Mínimo 8 caracteres.")
    salt = secrets.token_bytes(SALT_BYTES)
    key = _derive_key(password, salt)
    try:
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, salt, pw_hash) VALUES (?, ?, ?)", (username, salt, key))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def _get_user(username: str):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT id, salt, pw_hash, failed_attempts, lock_until FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        return row

def _update_failed(username: str, failed: int, lock_until: int):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET failed_attempts = ?, lock_until = ? WHERE username = ?", (failed, lock_until, username))
        conn.commit()

def verify_login(username: str, password: str):
    row = _get_user(username)
    if not row:
        # avoid user enumeration timing differences
        dummy_salt = b"\x00" * SALT_BYTES
        dummy_hash = _derive_key(password, dummy_salt)
        hmac.compare_digest(dummy_hash, dummy_hash)
        return False, "Credenciais inválidas."

    user_id, salt, pw_hash, failed_attempts, lock_until = row
    now = _now_ts()
    if lock_until and now < lock_until:
        wait = lock_until - now
        return False, f"Conta bloqueada. Tente novamente em {wait} segundos."

    candidate = _derive_key(password, salt)
    if hmac.compare_digest(candidate, pw_hash):
        # reset failed attempts
        _update_failed(username, 0, 0)
        session = _create_session_token(user_id)
        return True, session
    else:
        failed_attempts = (failed_attempts or 0) + 1
        lock_until = 0
        if failed_attempts >= MAX_FAILED:
            # exponential backoff
            extra = 2 ** (failed_attempts - MAX_FAILED)
            lock_until = now + LOCKOUT_BASE_SECONDS * extra
        _update_failed(username, failed_attempts, lock_until)
        return False, "Credenciais inválidas."

# In-memory session store (for demo). In produção, persist sessions.
_sessions = {}

def _create_session_token(user_id: int):
    token = secrets.token_urlsafe(32)
    expiry = _now_ts() + SESSION_TTL_SECONDS
    _sessions[token] = {"user_id": user_id, "expiry": expiry}
    return {"token": token, "expiry": expiry}

def validate_session(token: str):
    info = _sessions.get(token)
    if not info:
        return False
    if _now_ts() > info["expiry"]:
        del _sessions[token]
        return False
    return True

def logout(token: str):
    _sessions.pop(token, None)

def request_password_reset(username: str):
    row = _get_user(username)
    if not row:
        # do not reveal existence
        return True
    token = secrets.token_urlsafe(24)
    expiry = _now_ts() + RESET_TOKEN_TTL
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET reset_token = ?, reset_expiry = ? WHERE username = ?", (token, expiry, username))
        conn.commit()
    # In real app: send token by email. Here we return it for demo.
    return token

def reset_password(username: str, token: str, new_password: str):
    if len(new_password) < 8:
        raise ValueError("Senha muito curta.")
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT reset_token, reset_expiry FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if not row:
            return False
        stored_token, expiry = row
        if not stored_token or _now_ts() > (expiry or 0):
            return False
        if not hmac.compare_digest(stored_token, token):
            return False
        salt = secrets.token_bytes(SALT_BYTES)
        key = _derive_key(new_password, salt)
        c.execute("UPDATE users SET salt = ?, pw_hash = ?, reset_token = NULL, reset_expiry = NULL, failed_attempts = 0, lock_until = 0 WHERE username = ?", (salt, key, username))
        conn.commit()
        return True

def change_password(username: str, old_password: str, new_password: str):
    ok, result = verify_login(username, old_password)
    if not ok:
        return False
    if len(new_password) < 8:
        raise ValueError("Senha muito curta.")
    salt = secrets.token_bytes(SALT_BYTES)
    key = _derive_key(new_password, salt)
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET salt = ?, pw_hash = ? WHERE username = ?", (salt, key, username))
        conn.commit()
    return True

# Simple CLI demo
def _print_menu():
    print("\n1) Criar usuário\n2) Login\n3) Solicitar reset de senha\n4) Resetar senha com token\n5) Sair")

def main():
    init_db()
    print("Sistema de autenticação demo")
    while True:
        _print_menu()
        choice = input("Escolha: ").strip()
        if choice == "1":
            u = input("Usuário: ").strip()
            p = input("Senha: ").strip()
            try:
                ok = create_user(u, p)
                print("Criado." if ok else "Usuário já existe.")
            except ValueError as e:
                print("Erro:", e)
        elif choice == "2":
            u = input("Usuário: ").strip()
            p = input("Senha: ").strip()
            ok, res = verify_login(u, p)
            if ok:
                print("Login OK. Token:", res["token"])
            else:
                print("Falha:", res)
        elif choice == "3":
            u = input("Usuário: ").strip()
            token = request_password_reset(u)
            print("Token de reset (demo):", token)
        elif choice == "4":
            u = input("Usuário: ").strip()
            t = input("Token: ").strip()
            np = input("Nova senha: ").strip()
            try:
                ok = reset_password(u, t, np)
                print("Senha resetada." if ok else "Token inválido ou expirado.")
            except ValueError as e:
                print("Erro:", e)
        elif choice == "5":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
