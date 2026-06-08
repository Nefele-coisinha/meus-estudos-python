import random

# =============================================================================
# CONSTANTES E DADOS DO JOGO
# =============================================================================

# Classes disponíveis
CLASSES = {
    "1": {"nome": "Guerreiro", "vida": 600, "critico": 0.0, "precisao": 0.0},
    "2": {"nome": "Mago", "vida": 500, "critico": 0.1, "precisao": 0.0},
    "3": {"nome": "Assassino", "vida": 500, "critico": 0.2, "precisao": 0.0},
    "4": {"nome": "Samurai", "vida": 500, "critico": 0.0, "precisao": 0.15}
}

# Decks Fantasiosos (passivas)
DECK_FANTASIOSO = [
    {"nome": "A Lenda do Dragão", "historia": "Um antigo dragão deixou seu legado...", "buff": {"tipo": "dano", "valor": 0.3}},
    {"nome": "A Maldição da Sombra", "historia": "As sombras sussurram poder e perdição...", "buff": {"tipo": "critico", "valor": 0.15}},
    {"nome": "O Pacto do Anjo", "historia": "Um anjo celestial selou um pacto contigo...", "buff": {"tipo": "vida", "valor": 100}},
    {"nome": "A Bênção do Tempo", "historia": "O tempo flui a seu favor...", "buff": {"tipo": "energia", "valor": 10}},
    {"nome": "O Sussurro da Floresta", "historia": "A natureza te protege com sua sabedoria...", "buff": {"tipo": "defesa", "valor": 0.25}},
    {"nome": "O Chamado do Abismo", "historia": "Poderes antigos despertam em você...", "buff": {"tipo": "efeito_dano", "valor": 10}},
    {"nome": "A Cicatriz do Guerreiro", "historia": "Cada ferida te faz mais forte...", "buff": {"tipo": "cura", "valor": 0.5}},
    {"nome": "O Olho do Predador", "historia": "Você vê tudo que se move...", "buff": {"tipo": "precisao", "valor": 0.2}}
]

# Relíquias (sistema roguelike)
RELICS = [
    {"nome": "Cálice do Gladiador Feroz", "tipo": "calice", "set": "gladiador", "bonus": {"dano": 0.1}},
    {"nome": "Coroa do Gladiador Feroz", "tipo": "coroa", "set": "gladiador", "bonus": {"critico": 0.05}},
    {"nome": "Flor do Gladiador Feroz", "tipo": "flor", "set": "gladiador", "bonus": {"energia_por_critico": 2}},
    {"nome": "Coroa da Ação e Reação", "tipo": "coroa", "set": "acao", "bonus": {"precisao": 0.1}},
    {"nome": "Relógio da Ação e Reação", "tipo": "relogio", "set": "acao", "bonus": {"energia_regen": 1}},
    {"nome": "Flor da Ação e Reação", "tipo": "flor", "set": "acao", "bonus": {"efeito_dano": 5}},
    {"nome": "Cálice do Guardião do Tempo", "tipo": "calice", "set": "tempo", "bonus": {"energia": 10}},
    {"nome": "Coroa do Guardião do Tempo", "tipo": "coroa", "set": "tempo", "bonus": {"precisao": 0.05}},
    {"nome": "Relógio do Guardião do Tempo", "tipo": "relogio", "set": "tempo", "bonus": {"energia_regen": 1}},
    {"nome": "Cálice da Flor Sereníssima", "tipo": "calice", "set": "flor", "bonus": {"defesa": 0.15}},
    {"nome": "Coroa da Flor Sereníssima", "tipo": "coroa", "set": "flor", "bonus": {"cura": 0.2}},
    {"nome": "Relógio da Flor Sereníssima", "tipo": "relogio", "set": "flor", "bonus": {"precisao": 0.05}}
]

# Bônus de conjunto das relíquias
SET_BONUS_RELICS = {
    "gladiador": {"dano": 0.1, "precisao": 0.05, "energia_por_critico": 1},
    "acao": {"dano": 0.1, "critico": 0.05, "efeito_dano": 5},
    "tempo": {"energia": 5, "energia_regen": 1, "defesa": 0.1},
    "flor": {"cura": 0.3, "defesa": 0.1, "precisao": 0.05}
}

# Cartas do jogo
CARTAS = [
    {"nome": "bola de fogo", "dano": 25, "custo": 10, "precisao": 0.9, "efeito": {"tipo": "queimadura", "dano": 5, "turnos": 3}},
    {"nome": "veneno", "custo": 8, "precisao": 0.85, "efeito": {"tipo": "veneno", "dano": 7, "turnos": 3}},
    {"nome": "gelo", "dano": 15, "custo": 8, "precisao": 0.8, "efeito": {"tipo": "stun", "turnos": 1}},
    {"nome": "neblina confusa", "custo": 9, "precisao": 0.8, "efeito": {"tipo": "confusao", "turnos": 2}},
    {"nome": "cura", "cura": 20, "custo": 10, "precisao": 1.0},
    {"nome": "escudo", "custo": 6, "precisao": 1.0, "efeito": {"tipo": "escudo", "defesa": 15, "turnos": 2}},
    {"nome": "ataque forte", "dano": 30, "custo": 15, "precisao": 0.75},
    {"nome": "sangramento", "dano": 12, "custo": 9, "precisao": 0.85, "efeito": {"tipo": "sangramento", "dano": 6, "turnos": 4}},
    {"nome": "mordida vampira", "dano": 20, "custo": 12, "precisao": 0.8, "lifesteal": 0.5},
    {"nome": "rajada dupla", "dano": 18, "custo": 11, "precisao": 0.7, "efeito": {"tipo": "extra_turno", "turnos": 1}}
]

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def mostrar_menu(titulo, opcoes):
    """Exibe um menu com título e opções numeradas"""
    print(f"\n{'='*50}")
    print(titulo)
    print('='*50)
    for i, opcao in enumerate(opcoes, 1):
        print(f"{i}. {opcao}")
    return input("> ")

def escolher_multiplas_opcoes(titulo, itens, max_selecoes=3):
    """Permite escolher múltiplas opções até o limite"""
    print(f"\n{'='*50}")
    print(titulo)
    print('='*50)
    for i, item in enumerate(itens):
        print(f"{i+1}. {item['nome']} ({item.get('tipo', '')} - {item.get('set', '')})")

    selecionados = []
    while len(selecionados) < max_selecoes:
        escolha = input(f"Escolha item {len(selecionados)+1} (1-{len(itens)} ou enter para parar): ")
        if escolha == "":
            break
        if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(itens):
            print("Escolha inválida.")
            continue
        index = int(escolha) - 1
        if index in selecionados:
            print("Você já escolheu esse item.")
            continue
        selecionados.append(index)

    if not selecionados:
        selecionados = [0, 1, 2]  # Padrão
        print("Nenhuma escolha feita. Itens padrão atribuídos.")

    return [itens[i] for i in selecionados]

def aplicar_buff(buff, stats):
    """Aplica um buff aos stats do jogador"""
    tipo = buff["tipo"]
    valor = buff["valor"]
    if tipo == "dano":
        stats["dano_bonus"] += valor
    elif tipo == "critico":
        stats["critico_bonus"] += valor
    elif tipo == "vida":
        stats["vida"] += valor
    elif tipo == "energia":
        stats["energia_extra"] += valor
    elif tipo == "defesa":
        stats["defesa_bonus"] += valor
    elif tipo == "efeito_dano":
        stats["efeito_dano_bonus"] += valor
    elif tipo == "cura":
        stats["cura_bonus"] += valor
    elif tipo == "precisao":
        stats["precisao_bonus"] += valor

def aplicar_relic_bonus(relic, stats):
    """Aplica bônus de relíquia aos stats"""
    bonus = relic["bonus"]
    stats["energia_extra"] += bonus.get("energia", 0)
    stats["dano_bonus"] += bonus.get("dano", 0)
    stats["critico_bonus"] += bonus.get("critico", 0)
    stats["precisao_bonus"] += bonus.get("precisao", 0)
    stats["defesa_bonus"] += bonus.get("defesa", 0)
    stats["efeito_dano_bonus"] += bonus.get("efeito_dano", 0)
    stats["cura_bonus"] += bonus.get("cura", 0)
    stats["energia_por_critico"] += bonus.get("energia_por_critico", 0)
    stats["energia_regen_bonus"] += bonus.get("energia_regen", 0)

def verificar_set_bonus(relics_selecionadas, stats):
    """Verifica e aplica bônus de conjunto se aplicável"""
    sets = [r["set"] for r in relics_selecionadas]
    if len(relics_selecionadas) == 3 and len(set(sets)) == 1:
        set_nome = sets[0]
        set_bonus = SET_BONUS_RELICS[set_nome]
        print(f"\n✨ Bônus de conjunto ativado: {set_nome.title()}!\n")
        aplicar_relic_bonus({"bonus": set_bonus}, stats)

# =============================================================================
# FUNÇÕES DO JOGO
# =============================================================================

def comprar_cartas():
    """Retorna 3 cartas aleatórias do baralho"""
    return random.sample(CARTAS, 3)

def critico(dano, stats):
    """Calcula se é crítico e aplica bônus de energia se necessário"""
    if random.random() < (0.2 + stats["critico_bonus"]):
        print("💥 CRÍTICO!")
        if stats["energia_por_critico"] > 0:
            ganho = stats["energia_por_critico"]
            stats["energia"] = min(50 + stats["energia_extra"], stats["energia"] + ganho)
            print(f"⚡ +{ganho} energia por crítico")
        return dano * 2
    return dano

def teste_precisao(precisao):
    """Testa se o ataque acerta baseado na precisão"""
    if random.random() > precisao:
        print("❌ ERROU!")
        return False
    return True

def jogador_confuso(efeitos_jogador):
    """Verifica se o jogador está confuso"""
    return any(e["tipo"] == "confusao" for e in efeitos_jogador)

def inimigo_confuso(efeitos_inimigo):
    """Verifica se o inimigo está confuso"""
    return any(e["tipo"] == "confusao" for e in efeitos_inimigo)

def avaliar_carta_inimigo(carta, situacao):
    """Avalia o score de uma carta para o inimigo escolher a melhor"""
    if carta["custo"] > situacao["energia_inimigo"]:
        return -999

    score = 0
    if "cura" in carta:
        score += 80 if situacao["vida_inimigo"] < situacao["max_vida_inimigo"] * 0.3 else 15
    if carta.get("efeito", {}).get("tipo") == "stun":
        score += 45 if situacao["energia_jogador"] > 30 else 20
    if carta.get("efeito", {}).get("tipo") == "extra_turno":
        score += 35
    if carta.get("efeito", {}).get("tipo") == "escudo":
        score += 30 if situacao["vida_inimigo"] < situacao["max_vida_inimigo"] * 0.6 else 15
    if "dano" in carta:
        expected = carta["dano"] * carta.get("precisao", 1.0)
        if carta.get("lifesteal"):
            expected += 10
        if carta.get("precisao", 1.0) >= 0.85:
            expected += 5
        score += expected
    score -= carta["custo"] * 0.2
    return score

def aplicar_efeitos(efeitos, alvo, stats_jogador, stats_inimigo):
    """Aplica todos os efeitos ativos"""
    for e in efeitos[:]:
        if e["tipo"] in ["queimadura", "veneno", "sangramento"]:
            if alvo == "jogador":
                stats_jogador["vida"] -= e["dano"]
            else:
                stats_inimigo["vida"] -= e["dano"]
            print(f"🔥 {e['tipo']} -{e['dano']} vida")

        elif e["tipo"] == "stun":
            if alvo == "jogador":
                stats_jogador["pular_turno"] = True
            else:
                stats_inimigo["pular_turno"] = True
            print(f"🔵 {alvo} perdeu o turno")

        elif e["tipo"] == "escudo":
            if alvo == "jogador":
                defesa_valor = int(e["defesa"] * (1 + stats_jogador["defesa_bonus"]))
                stats_jogador["defesa"] = max(stats_jogador["defesa"], defesa_valor)
            else:
                stats_inimigo["defesa"] = max(stats_inimigo["defesa"], e["defesa"])
            print(f"🛡️ +{e['defesa']} defesa")

        elif e["tipo"] == "extra_turno":
            if alvo == "jogador":
                stats_jogador["extra_turno"] = True
            else:
                stats_inimigo["extra_turno"] = True
            print("⚡ Extra turno ativado!")

        elif e["tipo"] == "confusao":
            print(f"😵 {alvo} está confuso e escolherá cartas aleatórias")

        e["turnos"] -= 1
        if e["turnos"] <= 0:
            efeitos.remove(e)

def mostrar_efeitos(efeitos):
    """Retorna string formatada dos efeitos ativos"""
    if not efeitos:
        return "Nenhum"
    return ", ".join([f"{e['tipo']}({e['turnos']})" for e in efeitos])

def mostrar_status(stats_jogador, stats_inimigo, efeitos_jogador, efeitos_inimigo):
    """Exibe o status atual do combate"""
    print("\n" + "="*50)
    print(f"Vida: {stats_jogador['vida']} | Energia: {stats_jogador['energia']} | Defesa: {stats_jogador['defesa']}")
    print(f"Efeitos: {mostrar_efeitos(efeitos_jogador)}")
    print("-"*50)
    print(f"Inimigo Vida: {stats_inimigo['vida']} | Energia: {stats_inimigo['energia']} | Defesa: {stats_inimigo['defesa']}")
    print(f"Efeitos Inimigo: {mostrar_efeitos(efeitos_inimigo)}")
    print("="*50)

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal do jogo"""
    # Escolha de classe
    print("Escolha sua classe:")
    for key, classe in CLASSES.items():
        print(f"{key}. {classe['nome']} ({'mais vida' if key=='1' else 'efeitos melhores' if key=='2' else 'crítico alto' if key=='3' else 'precisão alta'})")

    classe_escolhida = input("> ")
    classe = CLASSES.get(classe_escolhida, CLASSES["1"])

    # Inicializar stats do jogador
    stats_jogador = {
        "vida": classe["vida"],
        "energia": 50,
        "energia_extra": 0,
        "defesa": 0,
        "critico_bonus": classe["critico"],
        "precisao_bonus": classe["precisao"],
        "dano_bonus": 0,
        "defesa_bonus": 0,
        "efeito_dano_bonus": 0,
        "cura_bonus": 0,
        "energia_por_critico": 0,
        "energia_regen_bonus": 0,
        "pular_turno": False,
        "extra_turno": False
    }

    # Escolha do Deck Fantasioso
    print("\nEscolha seu Deck Fantasioso:")
    for i, deck in enumerate(DECK_FANTASIOSO):
        print(f"{i+1}. {deck['nome']}")
        print(f"   📖 {deck['historia']}")

    escolha_deck = None
    while escolha_deck is None:
        entrada = input("\nEscolha (1-8): ").strip()
        if entrada.isdigit():
            indice = int(entrada) - 1
            if 0 <= indice < len(DECK_FANTASIOSO):
                escolha_deck = indice
                break
        print("Escolha inválida. Digite um número de 1 a 8.")

    deck_escolhido = DECK_FANTASIOSO[escolha_deck]
    aplicar_buff(deck_escolhido["buff"], stats_jogador)
    print(f"\n✨ Você escolheu: {deck_escolhido['nome']}!\n")

    # Escolha de Relíquias
    relics_selecionadas = escolher_multiplas_opcoes("Escolha até 3 Relíquias:", RELICS, 3)
    print("\nRelíquias escolhidas:")
    for relic in relics_selecionadas:
        print(f"- {relic['nome']}")

    for relic in relics_selecionadas:
        aplicar_relic_bonus(relic, stats_jogador)

    verificar_set_bonus(relics_selecionadas, stats_jogador)

    # Inicializar stats do inimigo
    stats_inimigo = {
        "vida": 500,
        "max_vida": 500,
        "energia": 50,
        "defesa": 0,
        "pular_turno": False,
        "extra_turno": False
    }

    # Aplicar energia extra ao jogador
    stats_jogador["energia"] += stats_jogador["energia_extra"]

    # Listas de efeitos
    efeitos_jogador = []
    efeitos_inimigo = []

    # =============================================================================
    # LOOP PRINCIPAL DO JOGO
    # =============================================================================

    while stats_jogador["vida"] > 0 and stats_inimigo["vida"] > 0:
        mostrar_status(stats_jogador, stats_inimigo, efeitos_jogador, efeitos_inimigo)

        # Aplicar efeitos
        aplicar_efeitos(efeitos_jogador, "jogador", stats_jogador, stats_inimigo)
        aplicar_efeitos(efeitos_inimigo, "inimigo", stats_jogador, stats_inimigo)

        # TURNO DO JOGADOR
        turno_jogador_ativo = True
        while turno_jogador_ativo and stats_jogador["vida"] > 0:
            turno_jogador_ativo = False

            if stats_jogador["pular_turno"]:
                print("Você perdeu o turno!")
                stats_jogador["pular_turno"] = False
                continue

            mao = comprar_cartas()
            for i, c in enumerate(mao):
                print(f"{i+1}. {c['nome']} ({c['custo']})")

            if jogador_confuso(efeitos_jogador):
                opcoes_validas = [c for c in mao if c["custo"] <= stats_jogador["energia"]]
                carta = random.choice(opcoes_validas or mao)
                print(f"😵 Você está confuso e usou: {carta['nome']}")
            else:
                escolha = input("> ")
                if escolha not in ["1","2","3"]:
                    turno_jogador_ativo = True
                    continue
                carta = mao[int(escolha)-1]

            if carta["custo"] > stats_jogador["energia"]:
                print("⚡ Sem energia!")
                turno_jogador_ativo = True
                continue

            stats_jogador["energia"] -= carta["custo"]

            acertou = True
            if "dano" in carta:
                precisao_total = min(1.0, carta.get("precisao", 1.0) + stats_jogador["precisao_bonus"])
                acertou = teste_precisao(precisao_total)

                if acertou:
                    dano_bruto = critico(carta["dano"], stats_jogador)
                    dano_com_buff = int(dano_bruto * (1 + stats_jogador["dano_bonus"]))
                    dano_real = max(0, dano_com_buff - stats_inimigo["defesa"])

                    stats_inimigo["defesa"] = max(0, stats_inimigo["defesa"] - dano_com_buff)
                    stats_inimigo["vida"] -= dano_real

                    print(f"⚔️ {dano_real} dano!")

                    if "lifesteal" in carta:
                        cura = int(dano_real * carta["lifesteal"])
                        stats_jogador["vida"] += cura
                        print(f"🩸 +{cura} vida")

            if acertou and "efeito" in carta:
                efeito_copy = carta["efeito"].copy()
                if "dano" in efeito_copy:
                    efeito_copy["dano"] += stats_jogador["efeito_dano_bonus"]
                efeitos_inimigo.append(efeito_copy)

            if "cura" in carta:
                cura_valor = int(carta["cura"] * (1 + stats_jogador["cura_bonus"]))
                stats_jogador["vida"] += cura_valor
                print(f"💚 +{cura_valor} vida (cura)")

            if stats_jogador["extra_turno"]:
                print("⚡ Turno extra!")
                stats_jogador["extra_turno"] = False
                turno_jogador_ativo = True

        # TURNO DO INIMIGO
        turno_inimigo_ativo = True
        while turno_inimigo_ativo and stats_inimigo["vida"] > 0:
            turno_inimigo_ativo = False

            if stats_inimigo["pular_turno"]:
                print("Inimigo perdeu o turno!")
                stats_inimigo["pular_turno"] = False
                continue

            mao_i = comprar_cartas()
            situacao = {
                "vida_inimigo": stats_inimigo["vida"],
                "max_vida_inimigo": stats_inimigo["max_vida"],
                "energia_inimigo": stats_inimigo["energia"],
                "energia_jogador": stats_jogador["energia"],
            }

            if inimigo_confuso(efeitos_inimigo):
                opcoes = [c for c in mao_i if c["custo"] <= stats_inimigo["energia"]]
                carta_i = random.choice(opcoes or mao_i)
                print("😵 Inimigo está confuso e escolheu carta aleatória.")
            else:
                carta_i = max(mao_i, key=lambda c: avaliar_carta_inimigo(c, situacao))

            if carta_i["custo"] <= stats_inimigo["energia"]:
                stats_inimigo["energia"] -= carta_i["custo"]

                acertou = True
                if "dano" in carta_i:
                    acertou = teste_precisao(carta_i.get("precisao", 1.0))

                    if acertou:
                        dano_bruto = carta_i["dano"]
                        dano_real = max(0, dano_bruto - stats_jogador["defesa"])

                        stats_jogador["defesa"] = max(0, stats_jogador["defesa"] - dano_bruto)
                        stats_jogador["vida"] -= dano_real

                        print(f"⚔️ Inimigo causou {dano_real}")

                        if "lifesteal" in carta_i:
                            cura = int(dano_real * carta_i["lifesteal"])
                            stats_inimigo["vida"] += cura
                            print(f"🩸 Inimigo +{cura}")

                if acertou and "efeito" in carta_i:
                    efeitos_jogador.append(carta_i["efeito"].copy())

                if "cura" in carta_i:
                    stats_inimigo["vida"] += carta_i["cura"]
                    print(f"💚 Inimigo usou cura e recuperou {carta_i['cura']} vida")

                if stats_inimigo["extra_turno"]:
                    print("⚡ Inimigo ganhou turno extra!")
                    stats_inimigo["extra_turno"] = False
                    turno_inimigo_ativo = True
            else:
                print("Inimigo sem energia!")

        # Regeneração de energia
        max_energia_jogador = 50 + stats_jogador["energia_extra"]
        stats_jogador["energia"] = min(max_energia_jogador, stats_jogador["energia"] + 3 + stats_jogador["energia_regen_bonus"])
        stats_inimigo["energia"] = min(50, stats_inimigo["energia"] + 3)

    # RESULTADO FINAL
    print("\n--- FIM ---")
    if stats_jogador["vida"] > 0:
        print("Você venceu! 🏆")
    else:
        print("Você perdeu! 💀")

    print("Jogar novamente? (s/n)")
    if input("> ").lower() == "s":
        print("Reinicie o programa 😎")

# =============================================================================
# EXECUÇÃO DO JOGO
# =============================================================================

if __name__ == "__main__":
    main()
