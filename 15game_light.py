from collections import deque
from array import array
import heapq
import time
import matplotlib.pyplot as plt
import random
from PIL import Image, ImageDraw, ImageFont
import matplotlib.patches as patches
import matplotlib.animation as animation
from IPython.display import HTML
import numpy as np

def is_solvable(flat):
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] != 0 and flat[j] != 0 and flat[i] > flat[j]:
                inversions += 1
    zero_row_from_bottom = 4 - (flat.index(0) // 4)
    return (inversions + zero_row_from_bottom) % 2 != 0

def generate_random_board(easy=False):
    if easy:
        # Tabuleiro próximo da solução, mas embaralhado levemente
        flat = list(range(1, 16)) + [0]
        # Fazer um pequeno embaralhamento reversível
        flat[12], flat[15] = flat[15], flat[12]  # troca 14 com 15, ainda é solucionável
        return flat

    while True:
        flat = list(range(16))
        random.shuffle(flat)
        if is_solvable(flat):
            return flat

def flatten_to_id(state):
    result = 0
    for num in state:
        result = (result << 4) | num
    return result

def manhattan_distance(state):
    distance = 0
    for index, value in enumerate(state):
        if value == 0:
            continue
        target_row, target_col = divmod(value - 1, 4)
        current_row, current_col = divmod(index, 4)
        distance += abs(target_row - current_row) + abs(target_col - current_col)
    return distance

def solve_game_flat(start_flat, method='BFS', max_depth=50):
    start_flat = array('B', start_flat)
    goal = array('B', list(range(1, 16)) + [0])
    goal_id = flatten_to_id(goal)

    parent = dict()
    visited = set()

    zero_pos = start_flat.index(0)
    start_id = flatten_to_id(start_flat)
    frontier_state = (start_id, zero_pos, 0)

    if method == 'BFS':
        frontier = deque()
        frontier_append = frontier.append
        frontier_pop = frontier.popleft
        frontier_append(frontier_state)
    elif method == 'DFS':
        frontier = []
        frontier_append = frontier.append
        frontier_pop = frontier.pop
        frontier_append(frontier_state)
    elif method == 'A*':
        frontier = []
        heapq.heappush(frontier, (manhattan_distance(start_flat), 0, start_id, zero_pos))
    else:
        raise ValueError("Método não suportado. Use 'BFS', 'DFS' ou 'A*'.")

    visited.add(start_id)
    total_visited = 0

    offsets = {
        "Up": -4, "Down": 4,
        "Left": -1, "Right": 1
    }

    reverse_move = {
        "Up": "Down",
        "Down": "Up",
        "Left": "Right",
        "Right": "Left"
    }

    def can_move(pos, direction):
        if direction == "Left" and pos % 4 == 0:
            return False
        if direction == "Right" and pos % 4 == 3:
            return False
        if direction == "Up" and pos < 4:
            return False
        if direction == "Down" and pos > 11:
            return False
        return True

    while frontier:
        if method == 'A*':
            f, g, state_id, zero = heapq.heappop(frontier)
            depth = g
        else:
            state_id, zero, depth = frontier_pop()

        state = array('B')
        temp = state_id
        for _ in range(16):
            state.insert(0, temp & 0xF)
            temp >>= 4

        if state_id == goal_id:
            path = []
            while state_id in parent:
                state_id, move = parent[state_id]
                path.append(move)
            path.reverse()
            return path

        if method != 'A*' and depth >= max_depth:
            if time.time() - start_time > 3000 and method == 'DFS': #ALTERAR AQUI O TEMPO LIMITE DO DFS
                print("DFS interrompido por tempo.")
                return None
            else: continue

        last_move = None
        if state_id in parent:
            _, last_move = parent[state_id]

        for move, offset in offsets.items():
            if move == reverse_move.get(last_move):
                continue

            if not can_move(zero, move):
                continue

            new_state = state[:]
            new_zero = zero + offset
            new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]

            new_state_id = flatten_to_id(new_state)
            if new_state_id not in visited:
                visited.add(new_state_id)
                parent[new_state_id] = (state_id, move)
                total_visited += 1
                if method == 'A*':
                    g = depth + 1
                    h = manhattan_distance(new_state)
                    heapq.heappush(frontier, (g + h, g, new_state_id, new_zero))
                    if total_visited % 100000 == 0:
                        print(f"Visitados: {total_visited} - g(n): {g} - h(n): {h}")
                else:
                    frontier_append((new_state_id, new_zero, depth + 1))
                    if total_visited % 100000 == 0:
                        print(f"Visitados: {total_visited} - Profundidade: {depth}")

def print_board_flat(flat):
    for i in range(0, 16, 4):
        row = flat[i:i+4]
        print(" ".join(f"{n if n != 0 else '_':>2}" for n in row))

def apply_move(board, move):
    board = board[:]  # copy
    idx = board.index(0)
    x, y = idx % 4, idx // 4
    dx, dy = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}[move]
    nx, ny = x + dx, y + dy
    if 0 <= nx < 4 and 0 <= ny < 4:
        nidx = ny * 4 + nx
        board[idx], board[nidx] = board[nidx], board[idx]
    return board

def draw_board(board):
    img = Image.new("RGB", (160, 160), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, val in enumerate(board):
        x = (i % 4) * 40
        y = (i // 4) * 40
        draw.rectangle([x, y, x+39, y+39], outline="black", width=2)
        if val != 0:
            draw.text((x+12, y+12), str(val), fill="black", font=font)
    return img

def generate_gif(start_board, moves, output_file="solucao.gif"):
    frames = [draw_board(start_board)]  # Adiciona o estado inicial
    board = start_board[:]
    
    # Adiciona as imagens dos movimentos
    for move in moves:
        board = apply_move(board, move)
        frames.append(draw_board(board))

    # Adiciona o quadro final, que será a última imagem
    frames.append(draw_board(board))  # A última posição do tabuleiro
    
    # Define uma pausa maior no último quadro
    duration = 300  # 300 ms entre quadros
    frames[0].save(output_file, save_all=True, append_images=frames[1:], duration=duration, loop=0) # loop=0 faz o GIF parar no final

if __name__ == "__main__":
    num_testes = 5 # Número de testes a serem realizados
    resultados_tempo = {'BFS': [], 'DFS': [], 'A*': []}
    resultados_movs = {'BFS': [], 'DFS': [], 'A*': []}

    for teste in range(1, num_testes + 1):
        print(f"\n===== Teste {teste} =====")
        start = generate_random_board(False)
        print("Estado inicial:")
        print_board_flat(start)

        for method in ['BFS', 'DFS', 'A*']:
            max_depth = 30 if method == 'BFS' else 50 #ALTERAR AQUI O VALOR DO MAX_DEPTH DO BFS
            print(f"\nResolvendo com {method}...")
            start_time = time.time()
            path = solve_game_flat(start, method=method, max_depth=max_depth)
            elapsed = time.time() - start_time

            if path:
                print(f"Solução encontrada com {len(path)} movimentos")
                print("Movimentos:", path)
                resultados_movs[method].append(len(path))
                generate_gif(start, path, f"resolucao_teste_{teste}_{method}.gif")
            else:
                print("Nenhuma solução encontrada.")
                resultados_movs[method].append(0)

            print(f"Tempo decorrido: {elapsed:.2f} segundos")
            resultados_tempo[method].append(elapsed)



    # Cálculo de médias
    medias_tempo = {m: sum(resultados_tempo[m])/num_testes for m in resultados_tempo}
    medias_movs = {m: sum(resultados_movs[m])/num_testes for m in resultados_movs}

    # Gráficos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(medias_tempo.keys(), medias_tempo.values(), color=['skyblue', 'salmon', 'lightgreen'])
    ax1.set_title('Tempo Médio de Execução por Método')
    ax1.set_ylabel('Segundos')
    ax1.set_xlabel('Método')

    ax2.bar(medias_movs.keys(), medias_movs.values(), color=['skyblue', 'salmon', 'lightgreen'])
    ax2.set_title('Movimentos Médios até a Solução')
    ax2.set_ylabel('Movimentos')
    ax2.set_xlabel('Método')

    plt.tight_layout()
    plt.show()














# # Exemplo de uso
# if __name__ == "__main__":
#     start = [1, 2, 4, 3,
#              5, 6, 8, 7,
#              15, 13, 14, 12,
#              11, 10, 0, 9]

#     print("Estado inicial:")
#     print_board_flat(start)

#     print("\nSolucionável?", is_solvable(start))

#     if is_solvable(start):
#         tempos = {}
#         movimentos = {}

#         for method in ['BFS', 'DFS', 'A*']:
#             max_depth = 21 if method == 'BFS' else 50
#             print(f"\nResolvendo com {method}...")
#             start_time = time.time()
#             path = solve_game_flat(start, method=method, max_depth=max_depth)
#             elapsed = time.time() - start_time
#             tempos[method] = elapsed
#             movimentos[method] = len(path) if path else 0

#             if path:
#                 print(f"\nSolução encontrada com {len(path)} movimentos")
#                 print("Movimentos:", path)
#             else:
#                 print("\nNenhuma solução encontrada dentro do limite de profundidade.")
#             print(f"Tempo decorrido: {elapsed:.2f} segundos")

#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

#         ax1.bar(tempos.keys(), tempos.values(), color=['skyblue', 'salmon', 'lightgreen'])
#         ax1.set_title('Tempo de Execução por Método')
#         ax1.set_ylabel('Segundos')
#         ax1.set_xlabel('Método')

#         ax2.bar(movimentos.keys(), movimentos.values(), color=['skyblue', 'salmon', 'lightgreen'])
#         ax2.set_title('Número de Movimentos até a Solução')
#         ax2.set_ylabel('Movimentos')
#         ax2.set_xlabel('Método')

#         plt.tight_layout()
#         plt.show()

#     else:
#         print("\nEsse tabuleiro não é solucionável.")
