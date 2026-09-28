import pygame
import random
from guloso import busca_gulosa
from a_estrela import busca_a_estrela

import math

TAMANHO_CELULA = 24
ESPACO_CELULA = 2
COLUNAS = 35
LINHAS = 25
LARGURA_GRADE = COLUNAS * TAMANHO_CELULA
ALTURA_GRADE = LINHAS * TAMANHO_CELULA
PAINEL_LATERAL = 280
LARGURA = LARGURA_GRADE + PAINEL_LATERAL
ALTURA = ALTURA_GRADE
FPS = 60
MARGEM_PAINEL = 15
RAIO_BORDA_CELULA = 4

BRANCO = (230, 228, 232)
CINZA_CLARO = (170, 165, 175)
CINZA = (110, 105, 115)
FUNDO_GRADE = (38, 35, 42)
CELULA_LIVRE = (90, 86, 98)
CELULA_OBSTACULO = (48, 45, 54)
COR_VISITADO = (75, 135, 100)
COR_CAMINHO = (50, 185, 110)
COR_NO_EXPLORADO = (35, 220, 120)
COR_MARCADOR = (235, 140, 145)
FUNDO_PAINEL = (42, 39, 48)
SEPARADOR_PAINEL = (65, 60, 70)
AZUL = (100, 145, 200)
AMARELO = (220, 190, 90)
ROXO = (165, 130, 210)
VERDE_BARRA = (130, 170, 110)

VELOCIDADES = [
    ("Muito lento", 200),
    ("Lento", 100),
    ("Normal", 40),
    ("Rápido", 15),
    ("Muito rápido", 5),
    ("Instantâneo", 0),
]

DIRECOES = [(-1, 0), (1, 0), (0, -1), (0, 1)]



class EstadoSimulacao:
    def __init__(self):
        self.grade = criar_grade()
        self.ponto_inicio = (12, 3)
        self.ponto_objetivo = (12, 31)
        self.algoritmo_selecionado = "a_estrela"
        self.proximo_ponto = "inicio"
        self.indice_velocidade = 2

        self.visitados_visiveis = set()
        self.caminho_visivel = set()
        self.metricas = None

        self.esta_animando = False
        self.visitados_em_ordem = []
        self.caminho_completo = []
        self.indice_animacao = 0
        self.fase_animacao = "explorando"
        self.tempo_ultimo_passo_ms = 0
        self.metricas_pendentes = None
        self.no_sendo_explorado = None

    def limpar_resultado(self):
        self.esta_animando = False
        self.no_sendo_explorado = None
        self.visitados_visiveis.clear()
        self.caminho_visivel.clear()
        self.metricas = None

    def executar_busca(self):
        if self.algoritmo_selecionado == "guloso":
            caminho, nos_visitados, tempo = busca_gulosa(
                self.grade, self.ponto_inicio, self.ponto_objetivo)
        else:
            caminho, nos_visitados, tempo = busca_a_estrela(
                self.grade, self.ponto_inicio, self.ponto_objetivo)

        self.visitados_em_ordem = nos_visitados
        self.caminho_completo = caminho
        self.metricas_pendentes = {
            "nos_explorados": len(nos_visitados),
            "custo_caminho": len(caminho) - 1 if caminho else 0,
            "tempo_ms": tempo,
            "encontrou": len(caminho) > 0,
        }

        intervalo_ms = VELOCIDADES[self.indice_velocidade][1]
        if intervalo_ms == 0:
            self.visitados_visiveis = set(nos_visitados)
            self.caminho_visivel = set(caminho)
            self.no_sendo_explorado = None
            self.metricas = self.metricas_pendentes
        else:
            self.visitados_visiveis = set()
            self.caminho_visivel = set()
            self.indice_animacao = 0
            self.fase_animacao = "explorando"
            self.esta_animando = True
            self.no_sendo_explorado = None
            self.tempo_ultimo_passo_ms = pygame.time.get_ticks()
            self.metricas = None

    def concluir_animacao(self):
        self.visitados_visiveis = set(self.visitados_em_ordem)
        self.caminho_visivel = set(self.caminho_completo)
        self.esta_animando = False
        self.no_sendo_explorado = None
        self.metricas = self.metricas_pendentes

    def atualizar_animacao(self):
        if not self.esta_animando:
            return

        tempo_atual_ms = pygame.time.get_ticks()
        intervalo_ms = VELOCIDADES[self.indice_velocidade][1]

        if intervalo_ms == 0:
            self.concluir_animacao()
            return

        while tempo_atual_ms - self.tempo_ultimo_passo_ms >= intervalo_ms:
            if self.fase_animacao == "explorando":
                if self.indice_animacao < len(self.visitados_em_ordem):
                    self.no_sendo_explorado = self.visitados_em_ordem[self.indice_animacao]
                    self.visitados_visiveis.add(self.no_sendo_explorado)
                    self.indice_animacao += 1
                    self.tempo_ultimo_passo_ms += intervalo_ms
                else:
                    self.fase_animacao = "caminho"
                    self.indice_animacao = 0
                    self.no_sendo_explorado = None
                    self.tempo_ultimo_passo_ms = tempo_atual_ms
                    break
            elif self.fase_animacao == "caminho":
                if self.indice_animacao < len(self.caminho_completo):
                    self.no_sendo_explorado = self.caminho_completo[self.indice_animacao]
                    self.caminho_visivel.add(self.no_sendo_explorado)
                    self.indice_animacao += 1
                    self.tempo_ultimo_passo_ms += intervalo_ms
                else:
                    self.concluir_animacao()
                    break

    def obter_progresso_animacao(self):
        if not self.esta_animando:
            return None
        if self.fase_animacao == "explorando":
            return ("explorando",
                    len(self.visitados_visiveis),
                    len(self.visitados_em_ordem))
        return ("caminho",
                len(self.caminho_visivel),
                len(self.caminho_completo))



def criar_grade():
    return [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]


def gerar_obstaculos(grade, inicio, objetivo, densidade=0.25):
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            posicao = (linha, coluna)
            if posicao != inicio and posicao != objetivo:
                grade[linha][coluna] = 1 if random.random() < densidade else 0



def desenhar_estrela(tela, centro_x, centro_y, raio, cor):
    pontos = []
    for i in range(10):
        angulo = -math.pi / 2 + i * math.pi / 5
        r = raio if i % 2 == 0 else raio * 0.4
        pontos.append((centro_x + r * math.cos(angulo),
                       centro_y + r * math.sin(angulo)))
    pygame.draw.polygon(tela, cor, pontos)


def desenhar_grade(tela, estado):
    area_grade = pygame.Rect(0, 0, LARGURA_GRADE, ALTURA_GRADE)
    pygame.draw.rect(tela, FUNDO_GRADE, area_grade)

    metade = TAMANHO_CELULA // 2
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            pixel_x = coluna * TAMANHO_CELULA
            pixel_y = linha * TAMANHO_CELULA
            retangulo = pygame.Rect(pixel_x + ESPACO_CELULA,
                                    pixel_y + ESPACO_CELULA,
                                    TAMANHO_CELULA - ESPACO_CELULA * 2,
                                    TAMANHO_CELULA - ESPACO_CELULA * 2)

            celula = (linha, coluna)
            if celula == estado.no_sendo_explorado:
                cor = COR_NO_EXPLORADO
            elif celula in estado.caminho_visivel:
                cor = COR_CAMINHO
            elif celula in estado.visitados_visiveis:
                cor = COR_VISITADO
            elif estado.grade[linha][coluna] == 1:
                cor = CELULA_OBSTACULO
            else:
                cor = CELULA_LIVRE

            pygame.draw.rect(tela, cor, retangulo,
                             border_radius=RAIO_BORDA_CELULA)

            centro_x = pixel_x + metade
            centro_y = pixel_y + metade
            if celula == estado.ponto_inicio:
                pygame.draw.circle(tela, COR_MARCADOR,
                                   (centro_x, centro_y), 6)
            elif celula == estado.ponto_objetivo:
                desenhar_estrela(tela, centro_x, centro_y, 8, COR_MARCADOR)


def desenhar_separador(tela, posicao_y):
    pygame.draw.line(tela, SEPARADOR_PAINEL,
                     (LARGURA_GRADE + MARGEM_PAINEL, posicao_y),
                     (LARGURA - MARGEM_PAINEL, posicao_y))
    return posicao_y + 15


def desenhar_secao_algoritmo(tela, fonte, fonte_titulo, algoritmo, posicao_y):
    nome = "Guloso" if algoritmo == "guloso" else "A*"
    cor = AMARELO if algoritmo == "guloso" else ROXO

    rotulo = fonte.render("Algoritmo atual:", True, CINZA_CLARO)
    valor = fonte_titulo.render(nome, True, cor)
    tela.blit(rotulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
    posicao_y += 22
    tela.blit(valor, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
    posicao_y += 35

    return desenhar_separador(tela, posicao_y)


def desenhar_secao_velocidade(tela, fonte, fonte_titulo, indice_velocidade,
                              posicao_y):
    rotulo = fonte.render("Velocidade:", True, CINZA_CLARO)
    tela.blit(rotulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
    posicao_y += 22

    nome = VELOCIDADES[indice_velocidade][0]
    valor = fonte_titulo.render(nome, True, AZUL)
    tela.blit(valor, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
    posicao_y += 26

    barra_x = LARGURA_GRADE + MARGEM_PAINEL
    barra_largura = PAINEL_LATERAL - MARGEM_PAINEL * 2
    barra_altura = 6
    pygame.draw.rect(tela, SEPARADOR_PAINEL,
                     (barra_x, posicao_y, barra_largura, barra_altura),
                     border_radius=3)
    if len(VELOCIDADES) > 1:
        preenchimento = int(
            barra_largura * indice_velocidade / (len(VELOCIDADES) - 1))
        if preenchimento > 0:
            pygame.draw.rect(tela, AZUL,
                             (barra_x, posicao_y, preenchimento, barra_altura),
                             border_radius=3)
    posicao_y += 16

    return desenhar_separador(tela, posicao_y)


def desenhar_secao_status(tela, fonte, fonte_titulo, metricas,
                          esta_animando, progresso_animacao, posicao_y):
    if esta_animando and progresso_animacao:
        fase, quantidade_atual, quantidade_total = progresso_animacao
        texto_status = ("Explorando..." if fase == "explorando"
                        else "Traçando caminho...")
        status = fonte_titulo.render(texto_status, True, BRANCO)
        tela.blit(status, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
        posicao_y += 28

        texto_progresso = f"{quantidade_atual} / {quantidade_total}"
        progresso = fonte.render(texto_progresso, True, CINZA_CLARO)
        tela.blit(progresso, (LARGURA_GRADE + MARGEM_PAINEL + 10, posicao_y))
        posicao_y += 26

        barra_x = LARGURA_GRADE + MARGEM_PAINEL
        barra_largura = PAINEL_LATERAL - MARGEM_PAINEL * 2
        barra_altura = 8
        pygame.draw.rect(tela, SEPARADOR_PAINEL,
                         (barra_x, posicao_y, barra_largura, barra_altura),
                         border_radius=4)
        if quantidade_total > 0:
            preenchimento = int(
                barra_largura * quantidade_atual / quantidade_total)
            if preenchimento > 0:
                cor_barra = AZUL if fase == "explorando" else VERDE_BARRA
                pygame.draw.rect(tela, cor_barra,
                                 (barra_x, posicao_y, preenchimento,
                                  barra_altura),
                                 border_radius=4)
        posicao_y += 20

    elif metricas:
        titulo = fonte_titulo.render("Métricas", True, BRANCO)
        tela.blit(titulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
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
            tela.blit(rotulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
            tela.blit(valor,
                      (LARGURA_GRADE + MARGEM_PAINEL + rotulo.get_width(),
                       posicao_y))
            posicao_y += 24
    else:
        instrucao_1 = fonte.render("Pressione ESPAÇO", True, CINZA_CLARO)
        instrucao_2 = fonte.render("para executar", True, CINZA_CLARO)
        tela.blit(instrucao_1, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
        posicao_y += 22
        tela.blit(instrucao_2, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))

    return posicao_y


def desenhar_secao_controles(tela, fonte, fonte_titulo, posicao_y):
    posicao_y = desenhar_separador(tela, posicao_y)

    titulo = fonte_titulo.render("Controles", True, BRANCO)
    tela.blit(titulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
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
        tela.blit(linha_texto, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
        posicao_y += 22


def desenhar_painel(tela, fonte, fonte_titulo, estado):
    painel = pygame.Rect(LARGURA_GRADE, 0, PAINEL_LATERAL, ALTURA)
    pygame.draw.rect(tela, FUNDO_PAINEL, painel)

    posicao_y = 20
    titulo = fonte_titulo.render("Busca de Caminho", True, BRANCO)
    tela.blit(titulo, (LARGURA_GRADE + MARGEM_PAINEL, posicao_y))
    posicao_y += 40

    posicao_y = desenhar_separador(tela, posicao_y)
    posicao_y = desenhar_secao_algoritmo(tela, fonte, fonte_titulo,
                                         estado.algoritmo_selecionado,
                                         posicao_y)
    posicao_y = desenhar_secao_velocidade(tela, fonte, fonte_titulo,
                                          estado.indice_velocidade,
                                          posicao_y)
    desenhar_secao_status(tela, fonte, fonte_titulo,
                          estado.metricas,
                          estado.esta_animando,
                          estado.obter_progresso_animacao(),
                          posicao_y)
    desenhar_secao_controles(tela, fonte, fonte_titulo, ALTURA - 230)



def tratar_eventos(estado):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False

        if evento.type == pygame.KEYDOWN:
            tratar_tecla(estado, evento.key)

        elif evento.type == pygame.MOUSEBUTTONDOWN and not estado.esta_animando:
            tratar_clique(estado, evento)

    return True


def tratar_tecla(estado, tecla):
    if tecla == pygame.K_UP:
        estado.indice_velocidade = min(estado.indice_velocidade + 1,
                                       len(VELOCIDADES) - 1)

    elif tecla == pygame.K_DOWN:
        estado.indice_velocidade = max(estado.indice_velocidade - 1, 0)

    elif tecla == pygame.K_g:
        estado.algoritmo_selecionado = "guloso"
        estado.limpar_resultado()

    elif tecla == pygame.K_a:
        estado.algoritmo_selecionado = "a_estrela"
        estado.limpar_resultado()

    elif tecla == pygame.K_SPACE:
        if estado.esta_animando:
            estado.concluir_animacao()
        else:
            estado.executar_busca()

    elif tecla == pygame.K_c:
        estado.grade = criar_grade()
        estado.limpar_resultado()

    elif tecla == pygame.K_r:
        estado.grade = criar_grade()
        gerar_obstaculos(estado.grade, estado.ponto_inicio,
                         estado.ponto_objetivo)
        estado.limpar_resultado()


def tratar_clique(estado, evento):
    mouse_x, mouse_y = evento.pos
    if mouse_x >= LARGURA_GRADE:
        return

    coluna_clicada = mouse_x // TAMANHO_CELULA
    linha_clicada = mouse_y // TAMANHO_CELULA
    posicao_clicada = (linha_clicada, coluna_clicada)

    if evento.button == 1:
        if (posicao_clicada != estado.ponto_inicio
                and posicao_clicada != estado.ponto_objetivo):
            estado.grade[linha_clicada][coluna_clicada] = (
                1 - estado.grade[linha_clicada][coluna_clicada])
            estado.limpar_resultado()

    elif evento.button == 3:
        if estado.grade[linha_clicada][coluna_clicada] == 0:
            if estado.proximo_ponto == "inicio":
                estado.ponto_inicio = posicao_clicada
                estado.proximo_ponto = "objetivo"
            else:
                estado.ponto_objetivo = posicao_clicada
                estado.proximo_ponto = "inicio"
            estado.limpar_resultado()



def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Busca de Caminho — Guloso vs A*")
    relogio = pygame.time.Clock()

    fonte = pygame.font.SysFont("DejaVu Sans", 15)
    fonte_titulo = pygame.font.SysFont("DejaVu Sans", 18, bold=True)

    estado = EstadoSimulacao()

    while True:
        if not tratar_eventos(estado):
            break

        estado.atualizar_animacao()

        tela.fill(FUNDO_PAINEL)
        desenhar_grade(tela, estado)
        desenhar_painel(tela, fonte, fonte_titulo, estado)
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
