print ("bem vindo ao RPG! Um mundo vasto e incrivel (ainda em desenvolvimento)")
vida_jogador = 100
vida_inimigo = 50

while vida_jogador > 0 and vida_inimigo > 0:
    print("\nSua vida:", vida_jogador)
    print("Vida do inimigo:", vida_inimigo)

    print("escolha uma ação:")
    print("1. Atacar")
    print("2. Defender")
    escolha = input("> ")

    if escolha == "1":
        dano = 10
        vida_inimigo -= dano
        print("Você atacou o inimigo e causou", dano, "de dano!")

    elif escolha == "2":
        defesa = 5
        vida_jogador += defesa
        print("Você se defendeu, e recebeu pouco dano, recuperando", defesa, "de vida!")
    else:
        print("Escolha inválida! Tente novamente.")
        
    #turno do inimigo
    dano_inimigo = 8
    vida_jogador -= dano_inimigo
    print("O inimigo atacou você e causou", dano_inimigo, "de dano!")

#resultado final
if vida_jogador <= 0:
    print("Você foi derrotado!")
elif vida_inimigo <= 0:
    print("Você derrotou o inimigo!")