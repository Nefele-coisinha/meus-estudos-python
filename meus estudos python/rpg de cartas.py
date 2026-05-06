import random

#=======================
# ESCOLHA DE CLASSE
#=======================

print("Escolha sua classe:")
print("1. Guerreiro (mais vida)")
print("2. Mago (efeitos melhores)")
print("3. Assassino (crítico alto)")
print("4. Samurai (precisão alta)")
classe = input("> ")

vida_jogador = 500
critico_bonus = 0
precisao_bonus = 0

if classe == "1":
    vida_jogador = 600
elif classe == "2":
    critico_bonus = 0.1
elif classe == "3":
    critico_bonus = 0.2
elif classe == "4":
    precisao_bonus = 0.15

#=======================
# DECK FANTASIOSO (CARTAS PASSIVAS)
#=======================

print("\n" + "="*50)
print("Escolha seu Deck Fantasioso:")
print("="*50)

deck_fantasioso = [
    {
        "nome": "A Lenda do Dragão",
        "historia": "Um antigo dragão deixou seu legado...",
        "buff": {"tipo": "dano", "valor": 0.3}
    },
    {
        "nome": "A Maldição da Sombra",
        "historia": "As sombras sussurram poder e perdição...",
        "buff": {"tipo": "critico", "valor": 0.15}
    },
    {
        "nome": "O Pacto do Anjo",
        "historia": "Um anjo celestial selou um pacto contigo...",
        "buff": {"tipo": "vida", "valor": 100}
    },
    {
        "nome": "A Bênção do Tempo",
        "historia": "O tempo flui a seu favor...",
        "buff": {"tipo": "energia", "valor": 10}
    },
    {
        "nome": "O Sussurro da Floresta",
        "historia": "A natureza te protege com sua sabedoria...",
        "buff": {"tipo": "defesa", "valor": 0.25}
    },
    {
        "nome": "O Chamado do Abismo",
        "historia": "Poderes antigos despertam em você...",
        "buff": {"tipo": "efeito_dano", "valor": 10}
    },
    {
        "nome": "A Cicatriz do Guerreiro",
        "historia": "Cada ferida te faz mais forte...",
        "buff": {"tipo": "cura", "valor": 0.5}
    },
    {
        "nome": "O Olho do Predador",
        "historia": "Você vê tudo que se move...",
        "buff": {"tipo": "precisao", "valor": 0.2}
    }
]

for i, d in enumerate(deck_fantasioso):
    print(f"{i+1}. {d['nome']}")
    print(f"   📖 {d['historia']}")

escolha_deck = int(input("\nEscolha (1-8): ")) - 1
deck_escolhido = deck_fantasioso[escolha_deck]

print(f"\n✨ Você escolheu: {deck_escolhido['nome']}!\n")

buff_deck = deck_escolhido["buff"]
dano_bonus_deck = 0
energia_extra = 0
defesa_bonus_deck = 0
efeito_dano_bonus = 0
cura_bonus_deck = 0

if buff_deck["tipo"] == "dano":
    dano_bonus_deck = buff_deck["valor"]
elif buff_deck["tipo"] == "critico":
    critico_bonus += buff_deck["valor"]
elif buff_deck["tipo"] == "vida":
    vida_jogador += buff_deck["valor"]
elif buff_deck["tipo"] == "energia":
    energia_extra = buff_deck["valor"]
elif buff_deck["tipo"] == "defesa":
    defesa_bonus_deck = buff_deck["valor"]
elif buff_deck["tipo"] == "efeito_dano":
    efeito_dano_bonus = buff_deck["valor"]
elif buff_deck["tipo"] == "cura":
    cura_bonus_deck = buff_deck["valor"]
elif buff_deck["tipo"] == "precisao":
    precisao_bonus += buff_deck["valor"]

#=======================
# CONFIG
#=======================

vida_inimigo = 500
energia_jogador = 50 + energia_extra
energia_inimigo = 50

efeitos_jogador = []
efeitos_inimigo = []

defesa_jogador = 0
defesa_inimigo = 0

pular_turno_jogador = False
pular_turno_inimigo = False

extra_turno_jogador = False
extra_turno_inimigo = False

#=======================
# CARTAS
#=======================

cartas = [
    {"nome": "bola de fogo", "dano": 25, "custo": 10, "precisao": 0.9,
     "efeito": {"tipo": "queimadura", "dano": 5, "turnos": 3}},

    {"nome": "veneno", "custo": 8, "precisao": 0.85,
     "efeito": {"tipo": "veneno", "dano": 7, "turnos": 3}},

    {"nome": "gelo", "dano": 15, "custo": 8, "precisao": 0.8,
     "efeito": {"tipo": "stun", "turnos": 1}},

    {"nome": "cura", "cura": 20, "custo": 10, "precisao": 1.0},

    {"nome": "escudo", "custo": 6, "precisao": 1.0,
     "efeito": {"tipo": "escudo", "defesa": 15, "turnos": 2}},

    {"nome": "ataque forte", "dano": 30, "custo": 15, "precisao": 0.75},
    
    {"nome": "sangramento", "dano": 12, "custo": 9, "precisao": 0.85,
     "efeito": {"tipo": "sangramento", "dano": 6, "turnos": 4}},
    
    {"nome": "mordida vampira", "dano": 20, "custo": 12, "precisao": 0.8,
     "lifesteal": 0.5},
    
    {"nome": "rajada dupla", "dano": 18, "custo": 11, "precisao": 0.7,
     "efeito": {"tipo": "extra_turno", "turnos": 1}}
]

#=======================
# EFEITOS
#=======================

def aplicar_efeitos(efeitos, alvo):
    global vida_jogador, vida_inimigo
    global defesa_jogador, defesa_inimigo
    global pular_turno_jogador, pular_turno_inimigo
    global extra_turno_jogador, extra_turno_inimigo

    for e in efeitos[:]:

        if e["tipo"] in ["queimadura", "veneno", "sangramento"]:
            if alvo == "jogador":
                vida_jogador -= e["dano"]
            else:
                vida_inimigo -= e["dano"]
            print(f"🔥 {e['tipo']} -{e['dano']} vida")

        elif e["tipo"] == "stun":
            if alvo == "jogador":
                pular_turno_jogador = True
            else:
                pular_turno_inimigo = True
            print(f"🔵 {alvo} perdeu o turno")

        elif e["tipo"] == "escudo":
            if alvo == "jogador":
                defesa_valor = int(e["defesa"] * (1 + defesa_bonus_deck))
                defesa_jogador = max(defesa_jogador, defesa_valor)
            else:
                defesa_inimigo = max(defesa_inimigo, e["defesa"])
            print(f"🛡️ +{e['defesa']} defesa")

        elif e["tipo"] == "extra_turno":
            if alvo == "jogador":
                extra_turno_jogador = True
            else:
                extra_turno_inimigo = True
            print("⚡ Extra turno ativado!")

        e["turnos"] -= 1
        if e["turnos"] <= 0:
            efeitos.remove(e)

def mostrar_efeitos(efeitos):
    if not efeitos:
        return "Nenhum"
    return ", ".join([f"{e['tipo']}({e['turnos']})" for e in efeitos])

#=======================
# FUNÇÕES
#=======================

def comprar_cartas():
    return random.sample(cartas, 3)

def critico(dano):
    if random.random() < (0.2 + critico_bonus):
        print("💥 CRÍTICO!")
        return dano * 2
    return dano

def teste_precisao(precisao):
    if random.random() > precisao:
        print("❌ ERROU!")
        return False
    return True

#=======================
# LOOP
#=======================

while vida_jogador > 0 and vida_inimigo > 0:

    print("\n" + "="*50)
    print(f"Vida: {vida_jogador} | Energia: {energia_jogador} | Defesa: {defesa_jogador}")
    print(f"Efeitos: {mostrar_efeitos(efeitos_jogador)}")
    print("-"*50)
    print(f"Inimigo Vida: {vida_inimigo} | Energia: {energia_inimigo} | Defesa: {defesa_inimigo}")
    print(f"Efeitos Inimigo: {mostrar_efeitos(efeitos_inimigo)}")
    print("="*50)

    aplicar_efeitos(efeitos_jogador, "jogador")
    aplicar_efeitos(efeitos_inimigo, "inimigo")

    # JOGADOR
    turno_jogador_repetido = True
    while turno_jogador_repetido:
        turno_jogador_repetido = False
        
        if pular_turno_jogador:
            print("Você perdeu o turno!")
            pular_turno_jogador = False
        else:
            mao = comprar_cartas()

            for i, c in enumerate(mao):
                print(f"{i+1}. {c['nome']} ({c['custo']})")

            escolha = input("> ")
            if escolha not in ["1","2","3"]:
                turno_jogador_repetido = True
            else:
                carta = mao[int(escolha)-1]

                if carta["custo"] > energia_jogador:
                    print("⚡ Sem energia!")
                else:
                    energia_jogador -= carta["custo"]

                    acertou = True
                    if "dano" in carta:
                        acertou = teste_precisao(min(1.0, carta.get("precisao",1.0) + precisao_bonus))

                        if acertou:
                            dano_bruto = critico(carta["dano"])
                            dano_com_buff = int(dano_bruto * (1 + dano_bonus_deck))
                            dano_real = max(0, dano_com_buff - defesa_inimigo)

                            defesa_inimigo = max(0, defesa_inimigo - dano_com_buff)
                            vida_inimigo -= dano_real

                            print(f"⚔️ {dano_real} dano!")

                            if "lifesteal" in carta:
                                cura = int(dano_real * carta["lifesteal"])
                                vida_jogador += cura
                                print(f"🩸 +{cura} vida")

                    if acertou and "efeito" in carta:
                        efeito_copy = carta["efeito"].copy()
                        if "dano" in efeito_copy:
                            efeito_copy["dano"] += efeito_dano_bonus
                        efeitos_inimigo.append(efeito_copy)

                    if "cura" in carta:
                        cura_valor = int(carta["cura"] * (1 + cura_bonus_deck))
                        vida_jogador += cura_valor
                        print(f"💚 +{cura_valor} vida (cura)")

                    if extra_turno_jogador:
                        print("⚡ Turno extra!")
                        extra_turno_jogador = False
                        turno_jogador_repetido = True

    # INIMIGO
    turno_inimigo_repetido = True
    while turno_inimigo_repetido and vida_inimigo > 0:
        turno_inimigo_repetido = False
        
        if pular_turno_inimigo:
            print("Inimigo perdeu o turno!")
            pular_turno_inimigo = False
        else:
            mao_i = comprar_cartas()
            carta_i = random.choice(mao_i)

            if carta_i["custo"] <= energia_inimigo:
                energia_inimigo -= carta_i["custo"]

                acertou = True
                if "dano" in carta_i:
                    acertou = teste_precisao(carta_i.get("precisao",1.0))

                    if acertou:
                        dano_bruto = carta_i["dano"]
                        dano_real = max(0, dano_bruto - defesa_jogador)

                        defesa_jogador = max(0, defesa_jogador - dano_bruto)
                        vida_jogador -= dano_real

                        print(f"⚔️ Inimigo causou {dano_real}")

                        if "lifesteal" in carta_i:
                            cura = int(dano_real * carta_i["lifesteal"])
                            vida_inimigo += cura
                            print(f"🩸 Inimigo +{cura}")

                if acertou and "efeito" in carta_i:
                    efeitos_jogador.append(carta_i["efeito"].copy())

                if "cura" in carta_i:
                    vida_inimigo += carta_i["cura"]

                if extra_turno_inimigo:
                    print("⚡ Inimigo ganhou turno extra!")
                    extra_turno_inimigo = False
                    turno_inimigo_repetido = True
            else:
                print("Inimigo sem energia!")

    energia_jogador = min(50 + energia_extra, energia_jogador + 3)
    energia_inimigo = min(50, energia_inimigo + 3)

#=======================
# RESULTADO
#=======================

print("\n--- FIM ---")
if vida_jogador > 0:
    print("Você venceu!")
else:
    print("Você perdeu!")

print("Jogar novamente? (s/n)")
if input("> ") == "s":
    print("Reinicie o programa 😎")
