import random

print("bem vindo a adivinhação!")
print("tente adivinhar o número que estou pensando.")
print("tenha até 5 tentativas.")
print("escolha a dificuldade.")

print("1 - fácil (1 a 10)")
print("2 - médio (1 a 50)")
print("3 - difícil (1 a 100)") 

opcao = input("digite sua escolha:")

if opcao == "1":
    numero_secreto = random.randint(1, 10) 
elif opcao == "2":
    numero_secreto = random.randint(1, 50)
elif opcao == "3":    
    numero_secreto = random.randint(1, 100)
else: 
    print("opção invalida!")
    exit()
#jogo começa aqui
tentativas = 5

while tentativas > 0:
    palpite = int(input("digite seu palpite:"))
    if palpite == numero_secreto:
        print("parabéns! você adivinhou o número!")
        break
    elif palpite < numero_secreto:
        print("tente um número maior.")
    else:
        print("tente um número menor.")
    tentativas -= 1
else:
    print("tentativas restantes:", tentativas)

if tentativas == 0:
    print("suas tentativas acabaram! o número era:", numero_secreto)

