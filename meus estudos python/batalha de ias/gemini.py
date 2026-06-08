import sqlite3
import hashlib
import os
import re

class SistemaLoginFoda:
    def __init__(self, db_name="sistema_seguro.db"):
        self.db_name = db_name
        self._inicializar_banco()

    def _inicializar_banco(self):
        """Cria o banco de dados e a tabela de usuários se não existirem."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE NOT NULL,
                        senha_hash BLOB NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"[ERRO DO SISTEMA] Falha ao conectar ao banco: {e}")

    def _criptografar_senha(self, senha, salt=None):
        """Gera um hash ultra-seguro usando PBKDF2."""
        if salt is None:
            salt = os.urandom(32) # Gera 32 bytes de dados aleatórios
        
        # 100.000 iterações tornam a quebra por força bruta inviável
        chave = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)
        return salt + chave

    def validar_senha(self, senha):
        """Exige no mínimo 8 caracteres, uma letra e um número."""
        if len(senha) < 8 or not re.search(r"\d", senha) or not re.search(r"[a-zA-Z]", senha):
            return False
        return True

    def registrar(self, usuario, senha):
        """Registra um novo usuário com tratamento anti-duplicidade."""
        if not usuario or not senha:
            print("[AVISO] Usuário e senha não podem ficar em branco.")
            return False

        if not self.validar_senha(senha):
            print("[AVISO] A senha deve ter pelo menos 8 caracteres, incluindo letras e números.")
            return False

        senha_segura = self._criptografar_senha(senha)

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)', (usuario, senha_segura))
                conn.commit()
                print(f"[SUCESSO] Usuário '{usuario}' registrado com perfeição!")
                return True
        except sqlite3.IntegrityError:
            print(f"[ERRO] O usuário '{usuario}' já existe. Tente outro nome.")
            return False
        except sqlite3.Error as e:
            print(f"[ERRO CRÍTICO] Erro no banco de dados: {e}")
            return False

    def login(self, usuario, senha):
        """Valida o login comparando os hashes."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT senha_hash FROM usuarios WHERE usuario = ?', (usuario,))
                resultado = cursor.fetchone()

                if resultado is None:
                    print("[FALHA] Usuário não encontrado.")
                    return False

                senha_armazenada = resultado[0]
                salt = senha_armazenada[:32]
                chave_armazenada = senha_armazenada[32:]

                # Recalcula o hash com a senha fornecida e o salt original
                chave_tentativa = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)

                if chave_tentativa == chave_armazenada:
                    print(f"[SUCESSO] Bem-vindo(a) de volta, {usuario}! Acesso concedido.")
                    return True
                else:
                    print("[FALHA] Senha incorreta. Acesso negado.")
                    return False
        except sqlite3.Error as e:
            print(f"[ERRO CRÍTICO] Erro no banco de dados: {e}")
            return False

# ==========================================
# INTERFACE DE USUÁRIO (MENU IMPENETRÁVEL)
# ==========================================
def main():
    sistema = SistemaLoginFoda()
    
    while True:
        print("\n--- 🛡️ SISTEMA DE LOGIN DE ALTA SEGURANÇA ---")
        print("1. Registrar novo usuário")
        print("2. Fazer Login")
        print("3. Sair")
        
        escolha = input("Escolha sua ação (1/2/3): ").strip()

        if escolha == '1':
            print("\n-- REGISTRO --")
            user = input("Digite um nome de usuário: ").strip()
            senha = input("Digite uma senha forte: ").strip()
            sistema.registrar(user, senha)

        elif escolha == '2':
            print("\n-- LOGIN --")
            user = input("Usuário: ").strip()
            senha = input("Senha: ").strip()
            sistema.login(user, senha)

        elif escolha == '3':
            print("Encerrando sistema. Até logo!")
            break

        else:
            print("[ERRO DE ENTRADA] Opção inválida. Por favor, digite 1, 2 ou 3.")

if __name__ == "__main__":
    # Garante que o programa não quebre nem se o usuário apertar Ctrl+C bruscamente
    try:
        main()
    except KeyboardInterrupt:
        print("\n[AVISO] Sistema encerrado forçadamente pelo usuário. Saindo com segurança...")
    except Exception as e:
        print(f"\n[ERRO FATAL EVITADO] Ocorreu um erro inesperado: {e}")