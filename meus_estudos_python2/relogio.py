from datetime import datetime


def saudacao():
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        return "Bom dia"
    elif 12 <= hora_atual < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def mostrar_horas():
    agora = datetime.now()
    hora = agora.strftime("%H:%M")  # Formata só hora e minutos
    print(f"{saudacao()}! Agora são: {hora}")


# Exemplo de uso:
while True:
    pergunta = input("Quer saber as horas? (s/n): ").lower()
    if pergunta == "s":
        mostrar_horas()
    elif pergunta == "n":
        print("Ok, até mais!")
        break
    else:
        print("Não entendi, digite 's' ou 'n'.")
