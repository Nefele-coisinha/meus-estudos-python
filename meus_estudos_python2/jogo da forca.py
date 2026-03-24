import random

# Lista de palavras
palavras = ["python", "programa", "jogo", "forca", "computador"]

# Escolhe uma palavra aleatória
palavra = random.choice(palavras)
letras_descobertas = ["_"] * len(palavra)
tentativas = 6
erros = 0

print("Bem-vindo ao jogo da forca!")

while erros < tentativas and "_" in letras_descobertas:
    print("\nPalavra:", " ".join(letras_descobertas))
    letra = input("Digite uma letra: ").lower()

    if letra in palavra:
        for i, l in enumerate(palavra):
            if l == letra:
                letras_descobertas[i] = letra
        print("Boa! Você acertou uma letra.")
    else:
        erros += 1
        print(f"Errou! Você ainda tem {tentativas - erros} tentativas.")

# Resultado final
if "_" not in letras_descobertas:
    print("\nParabéns! Você venceu! 🎉")
else:
    print(f"\nVocê perdeu! A palavra era: {palavra}")
