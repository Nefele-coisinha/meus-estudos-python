usuarios = {}
max_tentativas = 3

while True:
    print("\n=== Menu ===")
    print("1. Cadastrar usuário")
    print("2. Fazer login")
    print("3. Sair")

    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1":
        email = input("Digite seu email: ").strip().lower()
        senha = input("Digite sua senha: ").strip()
        if not email or not senha:
            print("Email e senha são obrigatórios.")
            continue
        usuarios[email] = senha
        print("Usuário cadastrado com sucesso!")

    elif opcao == "2":
        if not usuarios:
            print("Nenhum usuário cadastrado. Cadastre-se primeiro.")
            continue

        email = input("Digite seu email: ").strip().lower()
        senha = input("Digite sua senha: ").strip()

        if email not in usuarios or usuarios[email] != senha:
            print("Login falhou! Email ou senha incorretos.")
            continue

        print("Login bem sucedido!")
        break

    elif opcao == "3":
        print("Saindo...")
        break

    else:
        print("Opção inválida!")
