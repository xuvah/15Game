# -*- coding: utf-8 -*-
import random
import tkinter as tk
import time
from collections import deque

class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.create_grid()

    def create_grid(self):
        for i in range(4):
            for j in range(4):
                number = self.game.table[i][j]
                text = str(number) if number != 0 else ''
                btn = tk.Button(self.master, text=text, width=4, height=2, font=('Helvetica', 20),
                                command=lambda x=i, y=j: self.handle_click(x, y))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def update_grid(self):
        for i in range(4):
            for j in range(4):
                number = self.game.table[i][j]
                text = str(number) if number != 0 else ''
                self.buttons[i][j]['text'] = text

    def handle_click(self, i, j):
        zero_i = self.game.zero_pos['i']
        zero_j = self.game.zero_pos['j']
        if abs(zero_i - i) + abs(zero_j - j) == 1:
            self.game.table[zero_i][zero_j], self.game.table[i][j] = self.game.table[i][j], self.game.table[zero_i][zero_j]
            self.game.zero_pos = {'i': i, 'j': j}
            self.update_grid()

class Game15:
    def __init__(self, table=None):
        if table:
            self.table = [row[:] for row in table]  # cópia profunda leve
        else:
            self.table = self._generate_random_table()
        self.zero_pos = self._find_zero()
        self.move = ""

    @classmethod
    def from_parent(cls, table, zero_pos, move):
        obj = cls.__new__(cls)  # cria a instância sem chamar __init__
        obj.table = table
        obj.zero_pos = zero_pos
        obj.move = move
        return obj

    def _generate_random_table(self):
        flat = list(range(16))
        random.shuffle(flat)
        return [flat[i * 4:(i + 1) * 4] for i in range(4)]

    def __eq__(self, other):
        return isinstance(other, Game15) and self.table == other.table

    def __hash__(self):
        flat = tuple(num for row in self.table for num in row)
        return hash(flat)

    def get_state_id(self):
        return tuple(num for row in self.table for num in row)

    def _find_zero(self):
        for i in range(4):
            for j in range(4):
                if self.table[i][j] == 0:
                    return {'i': i, 'j': j}
        return None

    def get_moves(self, table_zero=None, last_move=None):
        i = table_zero['i'] if table_zero else self.zero_pos['i']
        j = table_zero['j'] if table_zero else self.zero_pos['j']

        possible_moves = {
            "Up": i > 0,
            "Down": i < 3,
            "Left": j > 0,
            "Right": j < 3
        }

        reverse = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }

        if last_move and reverse.get(last_move):
            possible_moves[reverse[last_move]] = False

        return possible_moves

    def test_factible(self):
        inversions = 0
        flat = [num for row in self.table for num in row if num != 0]
        zero_row = 4 - self.zero_pos['i']
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        return (inversions + zero_row) % 2 != 0

    def print_board(self):
        print("\033c", end="")
        for row in self.table:
            print(" ".join(f"{n if n != 0 else '_':>2}" for n in row))

    def do_moves(self):
        i, j = self.zero_pos['i'], self.zero_pos['j']
        new_states = []

        move_offsets = {
            "Up": (-1, 0),
            "Down": (1, 0),
            "Left": (0, -1),
            "Right": (0, 1)
        }

        for move, allowed in self.get_moves(self.zero_pos, self.move).items():
            if allowed:
                di, dj = move_offsets[move]
                ni, nj = i + di, j + dj
                new_table = [row[:] for row in self.table]
                new_table[i][j], new_table[ni][nj] = new_table[ni][nj], new_table[i][j]
                new_state = Game15.from_parent(new_table, {'i': ni, 'j': nj}, move)
                new_states.append(new_state)

        return new_states

    def solve_game(self, meta=None, method='BFS'):
        if not meta:
            meta_flat = list(range(1, 16)) + [0]
            meta = [meta_flat[i * 4:(i + 1) * 4] for i in range(4)]
        meta_id = tuple(num for row in meta for num in row)

        visited = set()
        initial_state = Game15.from_parent(self.table, self.zero_pos.copy(), "")
        initial_id = initial_state.get_state_id()
        visited.add(initial_id)

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

        frontier_append((initial_state, []))

        while frontier:
            current_state, path = frontier_pop()

            if current_state.get_state_id() == meta_id:
                print(f"Solução encontrada com {len(path)} movimentos")
                return path

            for next_state in current_state.do_moves():
                next_id = next_state.get_state_id()
                if next_id not in visited:
                    visited.add(next_id)
                    frontier_append((next_state, path + [next_state.move]))

            if len(visited) % 100000 == 0:
                print(f"Visitados: {len(visited)} - Profundidade atual: {len(path)}")


# main
if __name__ == "__main__":
    easy = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [0, 10, 11, 12],
        [9, 13, 14,15]
    ]
    lot_of_moves = [
        [1, 2, 4, 3],
        [5, 6, 8, 7],
        [15, 13, 14, 12],
        [11, 10, 0, 9]
    ]
    game = Game15()
    game.print_board()
    print("Solucionável?", game.test_factible())
    time.sleep(1)
    solve_path = game.solve_game(method= 'BFS')
    print("Solução:", solve_path)
    root = tk.Tk()
    root.title("Jogo dos 15")
    gui = GameGUI(root, game)
    root.mainloop()
