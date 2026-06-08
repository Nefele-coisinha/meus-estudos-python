import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("❤️")

clock = pygame.time.Clock()

font = pygame.font.SysFont("georgia", 24, bold=False)
font_final = pygame.font.SysFont("georgia", 44, bold=True)

TEXTO = "I love you"
NOME = "AGATA"

tempo = 0

TEMPO_FRASE = 5
FADE = 1.2

mensagens = [
    "...",
    "Eu sei que é meio clichê, mas o importante é ser sincero.",
    "Você foi a primeira pessoa que eu conversei, e a primeira que eu realmente me apaixonei.",
    "Admito que tinha uma quedinha por você kkk, mas não botava tanta fé.",
    "Mesmo com a tragédia que foi no primeiro relacionamento, eu não desisti.",
    "Busquei melhorar... e hoje, aqui estamos kkkk.",
    "mais..",
    "Não sabemos se vai dar certo...",
    "Não por falta de esforço nosso, mas por causa de terceiros.",
    "Mas eu quero tentar.",
    "Quero viver isso com você.",
    "Quero te fazer feliz...",
    "E quero ser feliz ao seu lado.",
    "Então o que eu tenho a dizer é..."
]

total_texto_tempo = len(mensagens) * TEMPO_FRASE
final_alpha = 0


def desenhar_texto(texto, fonte, y, alpha):
    palavras = texto.split(" ")
    linhas = []
    linha = ""

    max_largura = WIDTH - 120

    for palavra in palavras:
        teste = linha + palavra + " "
        if fonte.size(teste)[0] <= max_largura:
            linha = teste
        else:
            linhas.append(linha)
            linha = palavra + " "

    linhas.append(linha)

    altura_total = len(linhas) * fonte.get_height()
    y_inicio = y - altura_total // 2

    for i, l in enumerate(linhas):
        surf = fonte.render(l.strip(), True, (255, 120, 160))
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(WIDTH//2, y_inicio + i * fonte.get_height()))
        screen.blit(surf, rect)


def coracao_pontos(escala):
    pontos = []
    for t in range(0, 360, 8):
        t_rad = math.radians(t)

        x = 16 * math.sin(t_rad)**3
        y = -(13 * math.cos(t_rad)
              - 5 * math.cos(2*t_rad)
              - 2 * math.cos(3*t_rad)
              - math.cos(4*t_rad))

        px = WIDTH//2 + x * escala
        py = HEIGHT//2 + y * escala

        pontos.append((px, py))
    return pontos


while True:
    dt = clock.tick(60) / 1000
    tempo += dt * 2

    tempo_total = pygame.time.get_ticks() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((15, 15, 25))

    # 📝 FRASES
    if tempo_total < total_texto_tempo:
        index = int(tempo_total // TEMPO_FRASE)
        frase = mensagens[index]

        tempo_na_frase = tempo_total % TEMPO_FRASE

        if tempo_na_frase < FADE:
            alpha = int((tempo_na_frase / FADE) * 255)
        elif tempo_na_frase > TEMPO_FRASE - FADE:
            alpha = int(((TEMPO_FRASE - tempo_na_frase) / FADE) * 255)
        else:
            alpha = 255

        desenhar_texto(frase, font, HEIGHT//2, alpha)

    # ❤️ CORAÇÃO
    else:
        pontos = coracao_pontos(18)

        for i, (x, y) in enumerate(pontos):

            posicao_x_normalizada = (x - WIDTH//2) / (WIDTH//2)
            fade_wave = (math.sin(tempo_total * 2 * math.pi / 6 - posicao_x_normalizada * 3) + 1) / 2
            alpha = int(fade_wave * 200 + 55)

            surf = font.render(TEXTO, True, (255, 120, 160))
            surf.set_alpha(alpha)

            offset = math.sin(tempo + i * 0.3) * 2
            screen.blit(surf, (x, y + offset))

        # 💖 TEXTO CENTRAL (AJUSTADO)
        final_alpha += 100 * dt
        if final_alpha > 255:
            final_alpha = 255

        texto_final = font_final.render(f"Eu te amo, {NOME}", True, (255, 160, 190))
        texto_final.set_alpha(int(final_alpha))

        ondinha = math.sin(tempo * 0.8) * 6

        # 🔥 AQUI FOI O ÚNICO AJUSTE
        ajuste_y = -20  # sobe pro centro do coração

        rect = texto_final.get_rect(center=(WIDTH//2, HEIGHT//2 + ajuste_y + ondinha))
        screen.blit(texto_final, rect)

    pygame.display.flip()