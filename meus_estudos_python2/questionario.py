# pergunta qual é o seu nome
nome = input("qual é o seu nome? ")

# pergunta qual é a sua idade
idade = int(input('quantos anos você tem? '))

# pergunta qual é a sua cidade
cidade = (input("qual a sua cidade? "))

#pergunta qual é o pais
pais = input("qual é seu pais? ").lower()

#verificação do pais 

americano = ["estados unidos", "canadá", "alaska", ""]

latinos = ["brasil", "argentina", "chile", "peru"]

europa = ["frança", "alemanha", "italia", "espanha"]

asia = ["japão", "china", "coreia", "russia"]

if pais in latinos:
    origem = "latino"
elif pais in americano:
    origem = "norte americano"
elif pais in europa:
    origem = "europeu"
elif pais in asia:
    origem = "asiatico"
else:
    origem = "origem desconhecida"

# verifica se é maior/menor de idade, cidade e pais
if idade >= 18:
    trabalho = input("qual é o seu trabalho? ")
    print(f"{nome}, você é maior de idade, seu trabalho é {trabalho}, você é {origem} e mora em {cidade}! ")
else:
    print(f"{nome}, você ainda é menor de idade, você é {origem} e mora em {cidade}! ")
