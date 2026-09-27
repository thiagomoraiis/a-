"""
Simulação de Busca de Caminho — Guloso vs A*

Controles:
    Clique esquerdo  — colocar/remover obstáculo
    Clique direito   — definir ponto A (início) ou B (objetivo)
    G                — alternar para Busca Gulosa
    A                — alternar para A*
    ESPAÇO           — executar a busca (durante animação: concluir)
    C                — limpar grade
    R                — gerar obstáculos aleatórios
    ↑ / ↓            — aumentar / diminuir velocidade da animação
"""

import pygame
import random
from guloso import busca_gulosa
from a_estrela import busca_a_estrela

# --- Configurações da janela ---
TAMANHO_CELULA = 24
COLUNAS = 35
LINHAS = 25
LARGURA_GRADE = COLUNAS * TAMANHO_CELULA
ALTURA_GRADE = LINHAS * TAMANHO_CELULA
PAINEL_LATERAL = 280
LARGURA = LARGURA_GRADE + PAINEL_LATERAL
ALTURA = ALTURA_GRADE
FPS = 60

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (30, 30, 30)
CINZA_CLARO = (200, 200, 200)
CINZA = (140, 140, 140)
VERDE = (46, 204, 113)
VERMELHO = (231, 76, 60)
AZUL = (52, 152, 219)
AMARELO = (241, 196, 15)
ROXO = (155, 89, 182)
FUNDO_PAINEL = (45, 45, 55)
FUNDO_GRADE = (240, 240, 245)
COR_VISITADO = (174, 214, 241)
COR_CAMINHO = (46, 204, 113)
COR_NO_EXPLORADO = (41, 128, 185)

# --- Velocidades: (nome, delay em ms entre nós) ---
VELOCIDADES = [
    ("Muito lento", 200),
    ("Lento", 100),
    ("Normal", 40),
    ("Rápido", 15),
    ("Muito rápido", 5),
    ("Instantâneo", 0),
]


def criar_grade():
    return [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]


def gerar_obstaculos(grade, inicio, objetivo, densidade=0.25):
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            posicao = (linha, coluna)
            if posicao != inicio and posicao != objetivo:
                grade[linha][coluna] = 1 if random.random() < densidade else 0


def desenhar_grade(tela, grade, inicio, objetivo, visitados, caminho,
                   no_sendo_explorado):
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            pixel_x = coluna * TAMANHO_CELULA
            pixel_y = linha * TAMANHO_CELULA
            retangulo = pygame.Rect(pixel_x, pixel_y,
                                    TAMANHO_CELULA, TAMANHO_CELULA)

            if (linha, coluna) == inicio:
                cor = VERDE
            elif (linha, coluna) == objetivo:
                cor = VERMELHO
            elif (linha, coluna) == no_sendo_explorado:
                cor = COR_NO_EXPLORADO
            elif (linha, coluna) in caminho:
                cor = COR_CAMINHO
            elif (linha, coluna) in visitados:
                cor = COR_VISITADO
            elif grade[linha][coluna] == 1:
                cor = PRETO
            else:
                cor = FUNDO_GRADE

            pygame.draw.rect(tela, cor, retangulo)
            pygame.draw.rect(tela, CINZA_CLARO, retangulo, 1)


def desenhar_painel(tela, fonte, fonte_titulo, algoritmo_selecionado,
                    metricas, indice_velocidade, esta_animando,
                    progresso_animacao):
    painel = pygame.Rect(LARGURA_GRADE, 0, PAINEL_LATERAL, ALTURA)
    pygame.draw.rect(tela, FUNDO_PAINEL, painel)

    posicao_y = 20

    titulo = fonte_titulo.render("Busca de Caminho", True, BRANCO)
    tela.blit(titulo, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 40

    pygame.draw.line(tela, CINZA, (LARGURA_GRADE + 15, posicao_y),
                     (LARGURA - 15, posicao_y))
    posicao_y += 15

    # Algoritmo
    nome_algoritmo = "Guloso" if algoritmo_selecionado == "guloso" else "A*"
    cor_algoritmo = AMARELO if algoritmo_selecionado == "guloso" else ROXO
    rotulo = fonte.render("Algoritmo atual:", True, CINZA_CLARO)
    valor = fonte_titulo.render(nome_algoritmo, True, cor_algoritmo)
    tela.blit(rotulo, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 22
    tela.blit(valor, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 35

    pygame.draw.line(tela, CINZA, (LARGURA_GRADE + 15, posicao_y),
                     (LARGURA - 15, posicao_y))
    posicao_y += 15

    # Velocidade
    rotulo_velocidade = fonte.render("Velocidade:", True, CINZA_CLARO)
    tela.blit(rotulo_velocidade, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 22

    nome_velocidade = VELOCIDADES[indice_velocidade][0]
    valor_velocidade = fonte_titulo.render(nome_velocidade, True, AZUL)
    tela.blit(valor_velocidade, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 26

    # Barra de velocidade
    barra_x = LARGURA_GRADE + 15
    barra_largura = PAINEL_LATERAL - 30
    barra_altura = 6
    pygame.draw.rect(tela, CINZA,
                     (barra_x, posicao_y, barra_largura, barra_altura),
                     border_radius=3)
    if len(VELOCIDADES) > 1:
        largura_preenchida = int(
            barra_largura * indice_velocidade / (len(VELOCIDADES) - 1))
        if largura_preenchida > 0:
            pygame.draw.rect(tela, AZUL,
                             (barra_x, posicao_y, largura_preenchida,
                              barra_altura),
                             border_radius=3)
    posicao_y += 16

    pygame.draw.line(tela, CINZA, (LARGURA_GRADE + 15, posicao_y),
                     (LARGURA - 15, posicao_y))
    posicao_y += 15

    # Status / Métricas
    if esta_animando and progresso_animacao:
        fase, quantidade_atual, quantidade_total = progresso_animacao
        if fase == "explorando":
            texto_status = "Explorando..."
        else:
            texto_status = "Traçando caminho..."
        status = fonte_titulo.render(texto_status, True, BRANCO)
        tela.blit(status, (LARGURA_GRADE + 15, posicao_y))
        posicao_y += 28

        texto_progresso = f"{quantidade_atual} / {quantidade_total}"
        progresso = fonte.render(texto_progresso, True, CINZA_CLARO)
        tela.blit(progresso, (LARGURA_GRADE + 25, posicao_y))
        posicao_y += 26

        # Barra de progresso
        barra_progresso_largura = PAINEL_LATERAL - 30
        barra_progresso_altura = 8
        pygame.draw.rect(tela, CINZA,
                         (barra_x, posicao_y, barra_progresso_largura,
                          barra_progresso_altura),
                         border_radius=4)
        if quantidade_total > 0:
            preenchimento = int(
                barra_progresso_largura * quantidade_atual / quantidade_total)
            if preenchimento > 0:
                cor_barra = AZUL if fase == "explorando" else VERDE
                pygame.draw.rect(tela, cor_barra,
                                 (barra_x, posicao_y, preenchimento,
                                  barra_progresso_altura),
                                 border_radius=4)
        posicao_y += 20

    elif metricas:
        titulo_metricas = fonte_titulo.render("Métricas", True, BRANCO)
        tela.blit(titulo_metricas, (LARGURA_GRADE + 15, posicao_y))
        posicao_y += 30

        dados = [
            ("Nós explorados:", str(metricas["nos_explorados"])),
            ("Custo do caminho:", str(metricas["custo_caminho"])),
            ("Tempo (ms):", f"{metricas['tempo_ms']:.3f}"),
            ("Caminho encontrado:",
             "Sim" if metricas["encontrou"] else "Não"),
        ]

        for texto_rotulo, texto_valor in dados:
            rotulo = fonte.render(f"{texto_rotulo} ", True, CINZA_CLARO)
            valor = fonte.render(texto_valor, True, BRANCO)
            tela.blit(rotulo, (LARGURA_GRADE + 15, posicao_y))
            tela.blit(valor,
                      (LARGURA_GRADE + 15 + rotulo.get_width(), posicao_y))
            posicao_y += 24
    else:
        instrucao_1 = fonte.render("Pressione ESPAÇO", True, CINZA_CLARO)
        instrucao_2 = fonte.render("para executar", True, CINZA_CLARO)
        tela.blit(instrucao_1, (LARGURA_GRADE + 15, posicao_y))
        posicao_y += 22
        tela.blit(instrucao_2, (LARGURA_GRADE + 15, posicao_y))
        posicao_y += 30

    # Controles
    posicao_y = ALTURA - 230
    pygame.draw.line(tela, CINZA, (LARGURA_GRADE + 15, posicao_y),
                     (LARGURA - 15, posicao_y))
    posicao_y += 12

    titulo_controles = fonte_titulo.render("Controles", True, BRANCO)
    tela.blit(titulo_controles, (LARGURA_GRADE + 15, posicao_y))
    posicao_y += 28

    lista_controles = [
        "Esquerdo: obstáculo",
        "Direito: ponto A / B",
        "G: Busca Gulosa",
        "A: Algoritmo A*",
        "ESPAÇO: executar",
        "C: limpar grade",
        "R: obstáculos aleatórios",
        "↑/↓: velocidade",
    ]

    for texto in lista_controles:
        linha_texto = fonte.render(texto, True, CINZA_CLARO)
        tela.blit(linha_texto, (LARGURA_GRADE + 15, posicao_y))
        posicao_y += 22


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Busca de Caminho — Guloso vs A*")
    relogio = pygame.time.Clock()

    fonte = pygame.font.SysFont("DejaVu Sans", 15)
    fonte_titulo = pygame.font.SysFont("DejaVu Sans", 18, bold=True)

    grade = criar_grade()
    ponto_inicio = (12, 3)
    ponto_objetivo = (12, 31)
    algoritmo_selecionado = "a_estrela"

    visitados_visiveis = set()
    caminho_visivel = set()
    metricas = None

    # Animação
    esta_animando = False
    visitados_em_ordem = []
    caminho_completo = []
    indice_animacao = 0
    fase_animacao = "explorando"
    tempo_ultimo_passo_ms = 0
    metricas_pendentes = None
    no_sendo_explorado = None

    # Velocidade
    indice_velocidade = 2

    proximo_ponto = "inicio"
    executando = True

    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    indice_velocidade = min(indice_velocidade + 1,
                                           len(VELOCIDADES) - 1)

                elif evento.key == pygame.K_DOWN:
                    indice_velocidade = max(indice_velocidade - 1, 0)

                elif evento.key == pygame.K_g:
                    algoritmo_selecionado = "guloso"
                    esta_animando = False
                    no_sendo_explorado = None
                    visitados_visiveis.clear()
                    caminho_visivel.clear()
                    metricas = None

                elif evento.key == pygame.K_a:
                    algoritmo_selecionado = "a_estrela"
                    esta_animando = False
                    no_sendo_explorado = None
                    visitados_visiveis.clear()
                    caminho_visivel.clear()
                    metricas = None

                elif evento.key == pygame.K_SPACE:
                    if esta_animando:
                        visitados_visiveis = set(visitados_em_ordem)
                        caminho_visivel = set(caminho_completo)
                        esta_animando = False
                        no_sendo_explorado = None
                        metricas = metricas_pendentes
                    else:
                        if algoritmo_selecionado == "guloso":
                            caminho, nos_visitados, tempo = busca_gulosa(
                                grade, ponto_inicio, ponto_objetivo)
                        else:
                            caminho, nos_visitados, tempo = busca_a_estrela(
                                grade, ponto_inicio, ponto_objetivo)

                        visitados_em_ordem = nos_visitados
                        caminho_completo = caminho
                        metricas_pendentes = {
                            "nos_explorados": len(nos_visitados),
                            "custo_caminho": len(caminho) - 1 if caminho else 0,
                            "tempo_ms": tempo,
                            "encontrou": len(caminho) > 0,
                        }

                        intervalo_ms = VELOCIDADES[indice_velocidade][1]
                        if intervalo_ms == 0:
                            visitados_visiveis = set(nos_visitados)
                            caminho_visivel = set(caminho)
                            no_sendo_explorado = None
                            metricas = metricas_pendentes
                        else:
                            visitados_visiveis = set()
                            caminho_visivel = set()
                            indice_animacao = 0
                            fase_animacao = "explorando"
                            esta_animando = True
                            no_sendo_explorado = None
                            tempo_ultimo_passo_ms = pygame.time.get_ticks()
                            metricas = None

                elif evento.key == pygame.K_c:
                    grade = criar_grade()
                    esta_animando = False
                    no_sendo_explorado = None
                    visitados_visiveis.clear()
                    caminho_visivel.clear()
                    metricas = None

                elif evento.key == pygame.K_r:
                    grade = criar_grade()
                    gerar_obstaculos(grade, ponto_inicio, ponto_objetivo)
                    esta_animando = False
                    no_sendo_explorado = None
                    visitados_visiveis.clear()
                    caminho_visivel.clear()
                    metricas = None

            elif evento.type == pygame.MOUSEBUTTONDOWN and not esta_animando:
                mouse_x, mouse_y = evento.pos
                if mouse_x < LARGURA_GRADE:
                    coluna_clicada = mouse_x // TAMANHO_CELULA
                    linha_clicada = mouse_y // TAMANHO_CELULA

                    if evento.button == 1:
                        posicao_clicada = (linha_clicada, coluna_clicada)
                        if (posicao_clicada != ponto_inicio
                                and posicao_clicada != ponto_objetivo):
                            grade[linha_clicada][coluna_clicada] = (
                                1 - grade[linha_clicada][coluna_clicada])
                            visitados_visiveis.clear()
                            caminho_visivel.clear()
                            metricas = None

                    elif evento.button == 3:
                        posicao_clicada = (linha_clicada, coluna_clicada)
                        if grade[linha_clicada][coluna_clicada] == 0:
                            if proximo_ponto == "inicio":
                                ponto_inicio = posicao_clicada
                                proximo_ponto = "objetivo"
                            else:
                                ponto_objetivo = posicao_clicada
                                proximo_ponto = "inicio"
                            visitados_visiveis.clear()
                            caminho_visivel.clear()
                            metricas = None

        # Atualizar animação
        if esta_animando:
            tempo_atual_ms = pygame.time.get_ticks()
            intervalo_ms = VELOCIDADES[indice_velocidade][1]

            if intervalo_ms == 0:
                visitados_visiveis = set(visitados_em_ordem)
                caminho_visivel = set(caminho_completo)
                esta_animando = False
                no_sendo_explorado = None
                metricas = metricas_pendentes
            else:
                while tempo_atual_ms - tempo_ultimo_passo_ms >= intervalo_ms:
                    if fase_animacao == "explorando":
                        if indice_animacao < len(visitados_em_ordem):
                            no_sendo_explorado = visitados_em_ordem[indice_animacao]
                            visitados_visiveis.add(no_sendo_explorado)
                            indice_animacao += 1
                            tempo_ultimo_passo_ms += intervalo_ms
                        else:
                            fase_animacao = "caminho"
                            indice_animacao = 0
                            no_sendo_explorado = None
                            tempo_ultimo_passo_ms = tempo_atual_ms
                            break
                    elif fase_animacao == "caminho":
                        if indice_animacao < len(caminho_completo):
                            no_sendo_explorado = caminho_completo[indice_animacao]
                            caminho_visivel.add(no_sendo_explorado)
                            indice_animacao += 1
                            tempo_ultimo_passo_ms += intervalo_ms
                        else:
                            esta_animando = False
                            no_sendo_explorado = None
                            metricas = metricas_pendentes
                            break

        # Progresso da animação para o painel
        progresso_animacao = None
        if esta_animando:
            if fase_animacao == "explorando":
                progresso_animacao = ("explorando",
                                     len(visitados_visiveis),
                                     len(visitados_em_ordem))
            else:
                progresso_animacao = ("caminho",
                                     len(caminho_visivel),
                                     len(caminho_completo))

        tela.fill(FUNDO_PAINEL)
        desenhar_grade(tela, grade, ponto_inicio, ponto_objetivo,
                       visitados_visiveis, caminho_visivel,
                       no_sendo_explorado)
        desenhar_painel(tela, fonte, fonte_titulo, algoritmo_selecionado,
                        metricas, indice_velocidade, esta_animando,
                        progresso_animacao)
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
