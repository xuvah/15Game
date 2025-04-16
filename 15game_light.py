from collections import deque
from collections import defaultdict
from array import array
import random

def is_solvable(flat):
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] != 0 and flat[j] != 0 and flat[i] > flat[j]:
                inversions += 1
    zero_row_from_bottom = 4 - (flat.index(0) // 4)
    return (inversions + zero_row_from_bottom) % 2 != 0

def flatten_to_id(state):
    return bytes(state)

def solve_game_flat(start_flat, method='BFS', max_depth=50):
    start_flat = array('B', start_flat)
    goal = array('B', list(range(1, 16)) + [0])

    goal_id = flatten_to_id(goal)
    visited = set()
    parent = defaultdict()

    zero_pos = start_flat.index(0)
    start_id = flatten_to_id(start_flat)
    visited.add(start_id)
    frontier_state = (start_id, zero_pos, 0)

    if method == 'BFS':
        frontier = deque()
        frontier_append = frontier.append
        frontier_pop = frontier.popleft
    elif method == 'DFS':
        frontier = []
        frontier_append = frontier.append
        frontier_pop = frontier.pop
    else:
        raise ValueError("Método não suportado. Use 'BFS' ou 'DFS'.")

    frontier_append(frontier_state)

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
        state_id, zero, depth = frontier_pop()
        state = array('B', state_id)

        if state_id == goal_id:
            # reconstruir caminho
            path = []
            while state_id in parent:
                state_id, move = parent[state_id]
                path.append(move)
            path.reverse()
            return path

        if method == 'DFS' and depth >= max_depth:
            continue

        last_move = None
        if state_id in parent:
            _, last_move = parent[state_id]

        for move, offset in offsets.items():
            if move == reverse_move.get(last_move):
                continue  # evita desfazer o último movimento

            if not can_move(zero, move):
                continue

            new_state = state[:]
            new_zero = zero + offset
            new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]

            new_state_id = flatten_to_id(new_state)
            if new_state_id not in visited:
                visited.add(new_state_id)
                parent[new_state_id] = (state_id, move)
                frontier_append((new_state_id, new_zero, depth + 1))

        if len(visited) % 100000 == 0:
            print(f"Visitados: {len(visited)} - Profundidade: {depth}")

def print_board_flat(flat):
    for i in range(0, 16, 4):
        row = flat[i:i+4]
        print(" ".join(f"{n if n != 0 else '_':>2}" for n in row))

def create_random_game():
  flat= list(range(16))
  random.shuffle(flat)
  return flat

# Exemplo de uso
if __name__ == "__main__":
    start = [5, 1, 15, 4,
             3, 7, 2, 8,
             10, 6, 0, 11,
             9, 13, 14, 12]

    print("Estado inicial:")
    randomic_game = create_random_game()
    print_board_flat(randomic_game)

    print("\nSolucionável?", is_solvable(randomic_game))

    if is_solvable(randomic_game):
        print("\nResolvendo com BFS...")
        path = solve_game_flat(randomic_game, method='BFS')

        if path:
            print("\nSolução encontrada:", path)
            print("\nNúmero de movimentos:", len(path))
        else:
            print("\nNenhuma solução encontrada dentro do limite de profundidade.")
    else:
        print("\nEsse tabuleiro não é solucionável.")