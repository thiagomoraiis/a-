import heapq
import time


def heuristica(ponto_a, ponto_b):
    return abs(ponto_a[0] - ponto_b[0]) + abs(ponto_a[1] - ponto_b[1])


def busca_a_estrela(grade, inicio, objetivo):
    total_linhas = len(grade)
    total_colunas = len(grade[0])

    tempo_inicio = time.perf_counter()

    fila_prioridade = []
    heapq.heappush(fila_prioridade, (heuristica(inicio, objetivo), 0, inicio))

    antecessor = {inicio: None}
    custo_acumulado = {inicio: 0}
    visitados_set = set()
    visitados_em_ordem = []

    while fila_prioridade:
        _, custo_atual, no_atual = heapq.heappop(fila_prioridade)

        if no_atual in visitados_set:
            continue
        visitados_set.add(no_atual)
        visitados_em_ordem.append(no_atual)

        if no_atual == objetivo:
            break

        for delta_linha, delta_coluna in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            vizinho = (no_atual[0] + delta_linha, no_atual[1] + delta_coluna)
            linha, coluna = vizinho

            if 0 <= linha < total_linhas and 0 <= coluna < total_colunas:
                if grade[linha][coluna] == 0 and vizinho not in visitados_set:
                    novo_custo = custo_atual + 1

                    if vizinho not in custo_acumulado or novo_custo < custo_acumulado[vizinho]:
                        custo_acumulado[vizinho] = novo_custo
                        antecessor[vizinho] = no_atual
                        custo_total_estimado = novo_custo + heuristica(vizinho, objetivo)
                        heapq.heappush(fila_prioridade, (custo_total_estimado, novo_custo, vizinho))

    tempo_ms = (time.perf_counter() - tempo_inicio) * 1000

    caminho = reconstruir_caminho(antecessor, inicio, objetivo)
    return caminho, visitados_em_ordem, tempo_ms


def reconstruir_caminho(antecessor, inicio, objetivo):
    if objetivo not in antecessor:
        return []

    caminho = []
    no_atual = objetivo
    while no_atual is not None:
        caminho.append(no_atual)
        no_atual = antecessor[no_atual]
    caminho.reverse()
    return caminho
