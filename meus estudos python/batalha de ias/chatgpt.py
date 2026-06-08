import getpass
import time
import sys

# "Banco de dados" fake
usuarios = {}

def limpar():
    print("\n" * 50)

def pausa():
    input("\nPressione ENTER para continuar...")

def titulo(txt):
    print("=" * 40)
    print(txt.center(40))
    print("=" * 40)

def cadastrar():
    limpar()
    titulo("CADASTRO")

    user = input("Crie um usuário: ").strip()

    if user in usuarios:
        print("⚠️ Usuário já existe!")
        pausa()
        return

    senha = getpass.getpass("Crie uma senha: ")

    usuarios[user] = senha
    print("✅ Usuário cadastrado com sucesso!")
    pausa()

def login():
    limpar()
    titulo("LOGIN")

    tentativas = 3

    while tentativas > 0:
        user = input("Usuário: ").strip()
        senha = getpass.getpass("Senha: ")

        if user in usuarios and usuarios[user] == senha:
            print("\n💖 Login realizado com sucesso!")
            time.sleep(1)
            sistema_logado(user)
            return
        else:
            tentativas -= 1
            print(f"❌ Dados incorretos! Tentativas restantes: {tentativas}")

    print("\n🚫 Muitas tentativas! Acesso bloqueado.")
    pausa()

def sistema_logado(user):
    while True:
        limpar()
        titulo(f"BEM-VINDO, {user}")

        print("1 - Ver mensagem secreta 💌")
        print("2 - Logout")

        escolha = input("\nEscolha: ")

        if escolha == "1":
            mensagem_secreta()
        elif escolha == "2":
            print("\nSaindo...")
            time.sleep(1)
            break
        else:
            print("Opção inválida!")
            pausa()

def mensagem_secreta():
    limpar()
    titulo("💖 MENSAGEM 💖")

    texto = "Eu fiz esse sistema só pra você...\nVocê é muito especial 💕"

    for letra in texto:
        print(letra, end="", flush=True)
        time.sleep(0.05)

    pausa()

def sair():
    print("\nEncerrando sistema...")
    time.sleep(1)
    sys.exit()

def menu():
    while True:
        limpar()
        titulo("SISTEMA DE LOGIN")

        print("1 - Cadastrar")
        print("2 - Login")
        print("3 - Sair")

        escolha = input("\nEscolha: ")

        if escolha == "1":
            cadastrar()
        elif escolha == "2":
            login()
        elif escolha == "3":
            sair()
        else:
            print("❌ Opção inválida!")
            pausa()

# INÍCIO
menu()