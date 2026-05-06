anime = input("qual seu anime favorito? ")
genero = input("qual o genero do anime? ")

#verificação do genero
Naruto = ["shounen", "ação", "aventura", "comédia"]
onePiece = ["shounen", "ação", "aventura", "comédia"]
deathNote = ["Seinen", "ação", "sobrenatural", "mistério"]
if genero in Naruto:
    print(f"{anime} é um anime do gênero {genero}!")
elif genero in onePiece:
    print(f"{anime} é um anime do gênero {genero}!")
elif genero in deathNote:
    print(f"{anime} é um anime do gênero {genero}!")
else:
    print(f"{anime} não é um anime do gênero {genero}!")

