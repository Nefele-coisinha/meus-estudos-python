# perguntar dois numeros 
num1 = float(input("digite o primeiro numero: "))
num2 = float(input("digite o segundo numero: "))

# pergunta a operação
operacao = input("escolha a operacão (+, -, *, /): ")

# faz o cálculo
if operacao == "+":
    resultado = num1 + num2
elif operacao == "-":
    resultado = num1 - num2 
elif operacao == "*":
    resultado = num1 * num2
elif operacao == "/":
    resultado = num1 / num2
else:
    resultado = "operação invalida!"

# mostra resultado
print("resultado:", resultado)