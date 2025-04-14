# -*- coding: utf-8 -*-
import random
import tkinter as tk
import copy
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
        # tenta mover se for adjacente ao espaço vazio
        zero_i = self.game.zero_pos['i']
        zero_j = self.game.zero_pos['j']
        if abs(zero_i - i) + abs(zero_j - j) == 1:
            self.game.table[zero_i][zero_j], self.game.table[i][j] = self.game.table[i][j], self.game.table[zero_i][zero_j]
            self.game.zero_pos = {'i': i, 'j': j}
            self.update_grid()

class Game15:
    def __init__(self, table=None):
        if table:
            self.table = table
        else:
            self.table = self._generate_random_table()
        self.zero_pos = self._find_zero()
        self.move = ""

# método de criação
    def _generate_random_table(self):
        flat = list(range(16))
        random.shuffle(flat)
        table = [flat[i * 4:(i + 1) * 4] for i in range(4)]
        return table

    def __eq__(self, other):
        return isinstance(other, Game15) and self.table == other.table

    def __hash__(self):
        flat = tuple(num for row in self.table for num in row)
        return hash(flat)

    def _find_zero(self):
        for i in range(4):
            for j in range(4):
                if self.table[i][j] == 0:
                    return {'i': i, 'j': j}
        return None

    def get_moves(self, table_zero=None, last_move=None):
        if table_zero:
            i = table_zero['i']
            j = table_zero['j']
        else:
            i = self.zero_pos['i']
            j = self.zero_pos['j']

        possible_moves = {
            "Up": i > 0,
            "Down": i < 3,
            "Left": j > 0,
            "Right": j < 3
        }

        # Remover o movimento reverso (não desfazer o último passo)
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
        flat = [num if num != 0 else "_" for row in self.table for num in row]
        zero_row = 4 - self.zero_pos['i']
        for i in range(len(flat)-1):
            try:
                if flat[i] > flat[i+1]:
                    inversions += 1
            except:
                pass #tratativa para não realizar comparações entre o vazio (0) e os números
        return (inversions + zero_row) % 2 != 0

    def print_board(self,state=None):
        
        if state:
            print("\033c", end="")
            for row in state.table:
                print(" ".join(f"{n if n != 0 else '_':>2}" for n in row))
        else:
            print("\033c", end="")
            for row in self.table:
                print(" ".join(f"{n if n != 0 else '_':>2}" for n in row))

    def do_moves(self):
        i, j = self.zero_pos['i'], self.zero_pos['j']
        new_states = []

        move_offsets = {
            "Up":    (-1, 0),
            "Down":  (1, 0),
            "Left":  (0, -1),
            "Right": (0, 1)
        }

        for move, allowed in self.get_moves().items():
            if allowed:
                di, dj = move_offsets[move]
                ni, nj = i + di, j + dj
                new_table = [row[:] for row in self.table]  # cópia rasa
                new_table[i][j], new_table[ni][nj] = new_table[ni][nj], new_table[i][j]
                new_state = Game15(new_table)
                new_state.zero_pos = {'i': ni, 'j': nj}
                new_state.move = move
                new_states.append(new_state)

        return new_states

    def solve_game(self, meta=None, method='BFS'):
        if not meta:
            meta_flat = list(range(1, 16)) + [0]
            meta = [meta_flat[i * 4:(i + 1) * 4] for i in range(4)]

        meta_game = Game15(meta)
        queue = deque()
        visited = set()

        initial_state = copy.deepcopy(self)
        queue.append((initial_state, []))
        visited.add(initial_state)

        while queue:
            current_state, path = queue.popleft()

            if current_state == meta_game:
                return path

            next_states = current_state.do_moves()


            for next_state in next_states:
                if next_state not in visited:
                    queue.append((next_state, path + [next_state.move]))
                    visited.add(next_state)


#main
if __name__ == "__main__":
    easy = [
        [1, 2, 4, 3],
        [5, 6, 8, 7],
        [14, 13, 15, 12],
        [11, 10, 0, 9]
    ]
    game = Game15(easy)
    game.print_board()
    movimentos= game.get_moves()
    print ( "jogo solucioavel?", game.test_factible())
    time.sleep(1)
    solve_path = game.solve_game()
    print("Solução: ", solve_path)
    root = tk.Tk()
    root.title("Jogo dos 15")
    gui = GameGUI(root, game)
    root.mainloop()