"""
╔══════════════════════════════════════════════════════════════╗
║           SISTEMA DE LOGIN SEGURO - by Claude                ║
║          Arquitetura: Auth + Hash + Sessions + Logs          ║
╚══════════════════════════════════════════════════════════════╝
"""

import hashlib
import hmac
import os
import json
import time
import re
import getpass
import secrets
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ─────────────────────────── CONFIG ────────────────────────────

DB_FILE        = Path("usuarios.json")
LOG_FILE       = Path("auth.log")
MAX_ATTEMPTS   = 5
LOCKOUT_MIN    = 15
SESSION_HOURS  = 8
PEPPER         = b"C1@ud3-P3pp3r-S3cr3t!"   # em prod: env var


# ──────────────────────────── CORES ────────────────────────────

class Cor:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    VERDE   = "\033[92m"
    VERM    = "\033[91m"
    AMARELO = "\033[93m"
    CIANO   = "\033[96m"
    CINZA   = "\033[90m"
    AZUL    = "\033[94m"
    MAGENTA = "\033[95m"

def ok(msg):    print(f"{Cor.VERDE}  ✔  {msg}{Cor.RESET}")
def erro(msg):  print(f"{Cor.VERM}  ✘  {msg}{Cor.RESET}")
def info(msg):  print(f"{Cor.CIANO}  ℹ  {msg}{Cor.RESET}")
def warn(msg):  print(f"{Cor.AMARELO}  ⚠  {msg}{Cor.RESET}")


# ──────────────────────────── BANNER ───────────────────────────

def banner():
    print(f"""
{Cor.CIANO}{Cor.BOLD}
  ██╗      ██████╗  ██████╗ ██╗███╗   ██╗
  ██║     ██╔═══██╗██╔════╝ ██║████╗  ██║
  ██║     ██║   ██║██║  ███╗██║██╔██╗ ██║
  ██║     ██║   ██║██║   ██║██║██║╚██╗██║
  ███████╗╚██████╔╝╚██████╔╝██║██║ ╚████║
  ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚═╝  ╚═══╝
{Cor.RESET}{Cor.CINZA}  Sistema de Autenticação Segura v2.0{Cor.RESET}
""")


# ──────────────────────────── LOG ──────────────────────────────

def log(evento: str, usuario: str = "-", nivel: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{ts}] [{nivel:<8}] user={usuario:<20} evento={evento}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)


# ──────────────────────────── DB ───────────────────────────────

def carregar_db() -> dict:
    if not DB_FILE.exists():
        return {}
    try:
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        warn("Banco de dados corrompido. Recriando...")
        return {}

def salvar_db(db: dict):
    DB_FILE.write_text(
        json.dumps(db, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ─────────────────────────── CRYPTO ────────────────────────────

def gerar_salt() -> str:
    return secrets.token_hex(32)

def hash_senha(senha: str, salt: str) -> str:
    """PBKDF2-HMAC-SHA256 com pepper — resistente a rainbow tables."""
    chave = hashlib.pbkdf2_hmac(
        hash_name  = "sha256",
        password   = (senha.encode() + PEPPER),
        salt       = salt.encode(),
        iterations = 260_000,          # OWASP 2024 recommendation
        dklen      = 32
    )
    return base64.b64encode(chave).decode()

def verificar_senha(senha: str, salt: str, hash_armazenado: str) -> bool:
    """Comparação em tempo constante — previne timing attacks."""
    hash_tentativa = hash_senha(senha, salt)
    return hmac.compare_digest(hash_tentativa, hash_armazenado)

def gerar_token_sessao() -> str:
    return secrets.token_urlsafe(48)


# ─────────────────────────── VALIDAÇÃO ─────────────────────────

def validar_usuario(nome: str) -> tuple[bool, str]:
    if len(nome) < 3:
        return False, "Mínimo 3 caracteres."
    if len(nome) > 32:
        return False, "Máximo 32 caracteres."
    if not re.fullmatch(r"[a-zA-Z0-9_.\-]+", nome):
        return False, "Apenas letras, números, _, . e - são permitidos."
    return True, ""

def validar_senha(senha: str) -> tuple[bool, str]:
    regras = [
        (len(senha) >= 8,                    "Mínimo 8 caracteres"),
        (len(senha) <= 128,                  "Máximo 128 caracteres"),
        (bool(re.search(r"[A-Z]", senha)),   "Pelo menos 1 letra maiúscula"),
        (bool(re.search(r"[a-z]", senha)),   "Pelo menos 1 letra minúscula"),
        (bool(re.search(r"\d",    senha)),   "Pelo menos 1 número"),
        (bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:',.<>?/]", senha)),
                                             "Pelo menos 1 caractere especial"),
    ]
    falhas = [msg for ok_flag, msg in regras if not ok_flag]
    if falhas:
        return False, " | ".join(falhas)
    return True, ""

def forca_senha(senha: str) -> str:
    """Retorna indicador visual de força."""
    score = 0
    if len(senha) >= 12: score += 1
    if len(senha) >= 16: score += 1
    if re.search(r"[A-Z]", senha): score += 1
    if re.search(r"[a-z]", senha): score += 1
    if re.search(r"\d",    senha): score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:',.<>?/]", senha): score += 1
    niveis = {
        (0, 2): f"{Cor.VERM}▓░░░░ Fraca{Cor.RESET}",
        (2, 4): f"{Cor.AMARELO}▓▓▓░░ Média{Cor.RESET}",
        (4, 6): f"{Cor.VERDE}▓▓▓▓▓ Forte{Cor.RESET}",
    }
    for (mn, mx), rotulo in niveis.items():
        if mn <= score < mx:
            return rotulo
    return f"{Cor.VERDE}▓▓▓▓▓ Forte{Cor.RESET}"


# ─────────────────────────── BLOQUEIO ──────────────────────────

def esta_bloqueado(registro: dict) -> tuple[bool, int]:
    """Retorna (bloqueado, segundos_restantes)."""
    bloqueado_ate = registro.get("bloqueado_ate")
    if not bloqueado_ate:
        return False, 0
    restante = bloqueado_ate - time.time()
    if restante > 0:
        return True, int(restante)
    # Expirou: limpa o bloqueio
    registro["tentativas"]    = 0
    registro["bloqueado_ate"] = None
    return False, 0

def registrar_tentativa(registro: dict) -> bool:
    """Incrementa falhas; bloqueia se necessário. Retorna True se bloqueou."""
    registro["tentativas"] = registro.get("tentativas", 0) + 1
    if registro["tentativas"] >= MAX_ATTEMPTS:
        registro["bloqueado_ate"] = time.time() + LOCKOUT_MIN * 60
        return True
    return False


# ─────────────────────────── CADASTRO ──────────────────────────

def cadastrar():
    print(f"\n{Cor.BOLD}{Cor.AZUL}  ── NOVO CADASTRO ──{Cor.RESET}\n")
    db = carregar_db()

    # Usuário
    while True:
        nome = input(f"{Cor.BOLD}  Usuário: {Cor.RESET}").strip()
        valido, msg = validar_usuario(nome)
        if not valido:
            erro(msg)
            continue
        if nome in db:
            erro("Usuário já existe.")
            continue
        break

    # Senha
    while True:
        senha = getpass.getpass(f"{Cor.BOLD}  Senha  : {Cor.RESET}")
        valido, msg = validar_senha(senha)
        if not valido:
            erro(msg)
            info(f"Força → {forca_senha(senha)}")
            continue
        confirmacao = getpass.getpass(f"{Cor.BOLD}  Confirme: {Cor.RESET}")
        if senha != confirmacao:
            erro("As senhas não coincidem.")
            continue
        info(f"Força da senha → {forca_senha(senha)}")
        break

    # Persiste
    salt = gerar_salt()
    db[nome] = {
        "hash"         : hash_senha(senha, salt),
        "salt"         : salt,
        "criado_em"    : datetime.now().isoformat(),
        "ultimo_login" : None,
        "tentativas"   : 0,
        "bloqueado_ate": None,
        "ativo"        : True,
    }
    salvar_db(db)
    log("CADASTRO", nome)
    ok(f"Conta '{nome}' criada com sucesso!")


# ─────────────────────────── LOGIN ─────────────────────────────

def login() -> Optional[dict]:
    print(f"\n{Cor.BOLD}{Cor.AZUL}  ── ENTRAR ──{Cor.RESET}\n")
    db = carregar_db()

    nome = input(f"{Cor.BOLD}  Usuário: {Cor.RESET}").strip()

    # Usuário não encontrado — mesmo delay para evitar user enumeration
    if nome not in db:
        time.sleep(0.6)
        erro("Usuário ou senha incorretos.")
        log("LOGIN_FALHA_USER_INEXISTENTE", nome, "WARN")
        return None

    registro = db[nome]

    # Conta desativada
    if not registro.get("ativo", True):
        erro("Conta desativada. Contate o administrador.")
        log("LOGIN_CONTA_INATIVA", nome, "WARN")
        return None

    # Bloqueio por tentativas
    bloqueado, restante = esta_bloqueado(registro)
    if bloqueado:
        min_rest = restante // 60
        sec_rest = restante % 60
        erro(f"Conta bloqueada. Tente em {min_rest}m {sec_rest}s.")
        log("LOGIN_CONTA_BLOQUEADA", nome, "WARN")
        salvar_db(db)
        return None

    senha = getpass.getpass(f"{Cor.BOLD}  Senha  : {Cor.RESET}")

    if not verificar_senha(senha, registro["salt"], registro["hash"]):
        bloqueou = registrar_tentativa(registro)
        salvar_db(db)
        tentativas_restantes = MAX_ATTEMPTS - registro["tentativas"]
        if bloqueou:
            erro(f"Muitas tentativas. Conta bloqueada por {LOCKOUT_MIN} minutos.")
            log("CONTA_BLOQUEADA", nome, "ERROR")
        else:
            erro(f"Usuário ou senha incorretos. ({tentativas_restantes} tentativa(s) restante(s))")
            log("LOGIN_SENHA_ERRADA", nome, "WARN")
        return None

    # Sucesso
    registro["tentativas"]    = 0
    registro["bloqueado_ate"] = None
    registro["ultimo_login"]  = datetime.now().isoformat()

    token = gerar_token_sessao()
    sessao = {
        "usuario"    : nome,
        "token"      : token,
        "expira_em"  : (datetime.now() + timedelta(hours=SESSION_HOURS)).isoformat(),
        "ip_simulado": "127.0.0.1",
    }
    registro["sessao_atual"] = sessao
    salvar_db(db)
    log("LOGIN_OK", nome)

    ultimo = registro.get("ultimo_login", "Primeiro acesso")
    print(f"\n{Cor.VERDE}{Cor.BOLD}  ╔══════════════════════════════════╗")
    print(f"  ║   Bem-vindo, {nome:<20}║")
    print(f"  ║   Último login: {str(ultimo)[:16]:<17}║")
    print(f"  ║   Token: {token[:16]}...  ║")
    print(f"  ╚══════════════════════════════════╝{Cor.RESET}\n")
    return sessao


# ─────────────────────────── DASHBOARD ─────────────────────────

def painel_admin():
    print(f"\n{Cor.BOLD}{Cor.MAGENTA}  ── PAINEL (admin) ──{Cor.RESET}\n")
    db = carregar_db()
    if not db:
        info("Nenhum usuário cadastrado.")
        return

    print(f"  {'Usuário':<20} {'Ativo':<6} {'Último Login':<20} {'Tentativas'}")
    print(f"  {'-'*20} {'-'*6} {'-'*20} {'-'*10}")
    for nome, reg in db.items():
        ativo    = f"{Cor.VERDE}Sim{Cor.RESET}" if reg.get("ativo") else f"{Cor.VERM}Não{Cor.RESET}"
        ultimo   = (reg.get("ultimo_login") or "Nunca")[:19]
        tent     = reg.get("tentativas", 0)
        bloq, _  = esta_bloqueado(reg)
        bloq_str = f" {Cor.VERM}🔒{Cor.RESET}" if bloq else ""
        print(f"  {nome:<20} {ativo:<15} {ultimo:<20} {tent}{bloq_str}")
    print()


# ─────────────────────────── LOGOUT ────────────────────────────

def logout(sessao: dict):
    if not sessao:
        return
    db = carregar_db()
    nome = sessao.get("usuario")
    if nome in db:
        db[nome]["sessao_atual"] = None
        salvar_db(db)
    log("LOGOUT", nome)
    ok("Sessão encerrada com segurança.")


# ─────────────────────────── MAIN ──────────────────────────────

def menu_principal():
    banner()
    opcoes = {
        "1": ("Entrar",           login),
        "2": ("Criar conta",      cadastrar),
        "3": ("Painel de usuários", painel_admin),
        "4": ("Ver logs",         lambda: print(LOG_FILE.read_text() if LOG_FILE.exists() else "Sem logs.")),
        "0": ("Sair",             None),
    }

    sessao_atual = None

    while True:
        print(f"{Cor.BOLD}  ┌─────────────────────────┐")
        for k, (label, _) in opcoes.items():
            print(f"  │  [{k}] {label:<22}│")
        print(f"  └─────────────────────────┘{Cor.RESET}")

        if sessao_atual:
            info(f"Sessão ativa: {sessao_atual['usuario']} — [5] Logout")
            escolha = input(f"\n{Cor.BOLD}  Opção: {Cor.RESET}").strip()
            if escolha == "5":
                logout(sessao_atual)
                sessao_atual = None
                continue
        else:
            escolha = input(f"\n{Cor.BOLD}  Opção: {Cor.RESET}").strip()

        if escolha == "0":
            info("Até logo!")
            break

        if escolha not in opcoes:
            warn("Opção inválida.")
            continue

        _, acao = opcoes[escolha]
        resultado = acao()

        if escolha == "1" and resultado:
            sessao_atual = resultado


if __name__ == "__main__":
    menu_principal()