import sqlite3
import hashlib
import os
import getpass
import time
import logging
from datetime import datetime
from typing import Optional, Tuple

# Configuração de logging profissional
logging.basicConfig(
    filename='login_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LoginSystem:
    def __init__(self, db_name: str = "users.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        self.attempts = {}  # Rate limiting: {username: [timestamps]}

    def create_tables(self):
        """Cria as tabelas com schema seguro"""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    failed_attempts INTEGER DEFAULT 0
                )
            """)
            # Tabela de sessões (para simular autenticação persistente)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    created_at TEXT,
                    expires_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """PBKDF2 com 600.000 iterações (muito seguro em 2026)"""
        if not salt:
            salt = os.urandom(32).hex()
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            600000
        )
        return hash_obj.hex(), salt

    def register(self, username: str, email: str, password: str) -> bool:
        """Registro com validações robustas"""
        if len(password) < 12:
            print("❌ Senha deve ter no mínimo 12 caracteres.")
            return False
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            print("❌ Senha deve conter letra maiúscula e número.")
            return False

        try:
            password_hash, salt = self._hash_password(password)
            created_at = datetime.now().isoformat()
            
            with self.conn:
                self.conn.execute(
                    "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, email, password_hash, salt, created_at)
                )
            logging.info(f"Usuário registrado: {username}")
            print("✅ Cadastro realizado com sucesso!")
            return True
        except sqlite3.IntegrityError:
            print("❌ Usuário ou email já existe.")
            return False
        except Exception as e:
            logging.error(f"Erro no registro: {e}")
            print("❌ Erro interno no cadastro.")
            return False

    def _check_brute_force(self, username: str) -> bool:
        """Rate limiting simples mas eficaz"""
        now = time.time()
        if username not in self.attempts:
            self.attempts[username] = []
        
        # Remove tentativas antigas (> 5 minutos)
        self.attempts[username] = [t for t in self.attempts[username] if now - t < 300]
        
        if len(self.attempts[username]) >= 5:
            print("⛔ Muitas tentativas. Aguarde 5 minutos.")
            return False
        return True

    def login(self, username: str, password: str) -> Optional[str]:
        """Login seguro com rate limiting e lock por falhas"""
        if not self._check_brute_force(username):
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, password_hash, salt, failed_attempts FROM users WHERE username = ?", 
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                self.attempts[username].append(time.time())
                print("❌ Usuário ou senha inválidos.")
                logging.warning(f"Tentativa falha para usuário inexistente: {username}")
                return None

            user_id, stored_hash, salt, failed = user
            
            # Verifica lock por falhas
            if failed >= 5:
                print("🔒 Conta temporariamente bloqueada por muitas tentativas.")
                return None

            input_hash, _ = self._hash_password(password, salt)
            
            if input_hash == stored_hash:
                # Reset falhas e atualiza último login
                session_id = os.urandom(24).hex()
                expires = (datetime.now().timestamp() + 3600)  # 1 hora
                
                with self.conn:
                    self.conn.execute("UPDATE users SET failed_attempts = 0, last_login = ? WHERE id = ?", 
                                    (datetime.now().isoformat(), user_id))
                    self.conn.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
                                    (session_id, user_id, datetime.now().isoformat(), expires))
                
                self.attempts.pop(username, None)
                logging.info(f"Login bem-sucedido: {username}")
                print(f"✅ Login realizado! Session ID: {session_id}")
                return session_id
            else:
                # Incrementa falhas
                with self.conn:
                    self.conn.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = ?", (user_id,))
                self.attempts[username].append(time.time())
                print("❌ Usuário ou senha inválidos.")
                logging.warning(f"Tentativa falha para {username}")
                return None
                
        except Exception as e:
            logging.error(f"Erro no login: {e}")
            return None

    def check_session(self, session_id: str) -> bool:
        """Verifica se sessão é válida"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id FROM sessions WHERE session_id = ? AND expires_at > ?", 
            (session_id, datetime.now().timestamp())
        )
        return cursor.fetchone() is not None

    def logout(self, session_id: str):
        """Invalidar sessão"""
        with self.conn:
            self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        print("👋 Logout realizado.")

    def close(self):
        self.conn.close()


# Interface CLI bonita
def main():
    print("\n" + "="*60)
    print("🔐 SISTEMA DE LOGIN ULTRA SEGURANÇA v2.0".center(60))
    print(" " + "Feito para vencer competições".center(60))
    print("="*60)
    
    system = LoginSystem()
    
    while True:
        print("\n1. Registrar")
        print("2. Login")
        print("3. Sair")
        
        op = input("\nEscolha uma opção: ").strip()
        
        if op == "1":
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = getpass.getpass("Senha (mín 12 chars): ")
            system.register(username, email, password)
            
        elif op == "2":
            username = input("Username: ").strip()
            password = getpass.getpass("Senha: ")
            session = system.login(username, password)
            if session:
                print("🎉 Bem-vindo ao sistema!")
                # Aqui você poderia entrar num "dashboard"
                input("\nPressione ENTER para logout...")
                system.logout(session)
                
        elif op == "3":
            system.close()
            print("👋 Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()