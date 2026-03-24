#Login
max_tentativas = 3
credenciais_validas = {
    "gmail": "a@gmail.com",
    "senha": "12345"
}

for tentativa in range(1, max_tentativas + 1):
    senha = input("Digite sua senha: ")
    gmail = input("Digite seu gmail: ")

    if senha == credenciais_validas["senha"] and gmail == credenciais_validas["gmail"]:
        print("Login bem sucedido!")
        break

    restante = max_tentativas - tentativa
    if restante > 0:
        print(f"Login falhou! senha ou email errado. Você tem {restante} tentativa(s) restantes.")
    else:
        print("Login falhou! número máximo de tentativas atingido. Acesso bloqueado.")