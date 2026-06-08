anime = input("qual seu anime favorito? ").strip()
genero = input("qual o genero do anime? ").strip().lower()

# verificação do gênero
categorias = {
    "shounen": "shounen",
    "ação": "ação",
    "acao": "ação",
    "aventura": "aventura",
    "comédia": "comédia",
    "comedia": "comédia",
    "seinen": "seinen",
    "sobrenatural": "sobrenatural",
    "mistério": "mistério",
    "misterio": "mistério"
}

if genero in categorias:
    print(f"{anime} é um anime do gênero {categorias[genero]}!")
else:
    print(f"{anime} não é um anime do gênero {genero}! Ainda assim, é uma ótima escolha.")

