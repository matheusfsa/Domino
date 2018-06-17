import numpy as np
from collections import namedtuple
from Game import Game
from collections import namedtuple
import random
import time

infinity = float('inf')
GameState = namedtuple('GameState', 'to_move,pedras,pedras_restantes, utility, board')

def alphabeta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = game.to_move(state)

    # Functions used by alphabeta
    def max_value(state, alpha, beta):
        if game.terminal_test(state):
            print("terminal")
            return game.utility(state, player)
        v = -infinity
        #print(len(state.pedras))
        #game.display(state)
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = infinity
        #print(len(state.pedras))
        #game.display(state)
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_cutoff_search:
    best_score = -infinity
    beta = infinity
    best_action = None
    for a in game.actions(state):

        v = min_value(game.result(state, a), best_score, beta)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


def alphabeta_player(game, state):
    return alphabeta_search(state, game)

def query_player(game, state):
    """Make a move by querying standard input."""
    print("current state:")
    game.display(state)
    print("available moves: {}".format(game.actions(state)))
    print("")
    move_string = input('Your move? ')
    try:
        move = eval(move_string)
    except NameError:
        move = move_string
    return move


def random_player(game, state):
    """A player that chooses a legal move at random."""
    return random.choice(game.actions(state))

class Pedra:

    def __init__(self, a, b,position):
        self.valor = (a, b)
        self.position = position

    def __eq__(self, other):
        print("Comp ",self.valor)
        if self.valor[0] == other.valor[0] and self.valor[1] == other.valor[1]:
            return True
        if self.valor[0] == other.valor[1] and self.valor[1] == other.valor[0]:
            return True
        return False

    def igual(self, p):
        if p.position == -1:
            if self.valor[0] == p.valor[0] or self.valor[1] == p.valor[1] or self.valor[1] == p.valor[0] or self.valor[1] == p.valor[0]:
                return True
        if p.position == 0:
            if self.valor[1] == p.valor[0] or self.valor[0] == p.valor[0]:
                return True
        if p.position == 1:
            if self.valor[1] == p.valor[1] or self.valor[0] == p.valor[1]:
                return True
        return False

    def getValor(self):
        return self.valor[0] + self.valor[1]

    def __str__(self):
        if self.position != 1:
            return "(" + str(self.valor[0]) + ", " + str(self.valor[1]) + ")"
        else:
            return "(" + str(self.valor[1]) + ", " + str(self.valor[0]) + ")"
        #return " ___\n| " + str(self.valor[0]) + " |\n|___|\n| " + str(self.valor[1]) + " |\n|___|"



class Domino(Game):

    def __init__(self):
        self.pedras = self.cria_domino()
        self.jogadores = self.escolhe_pedras()
        pedras_restantes = []
        for i in range(1, 4):
            pedras_restantes += self.jogadores[i]
        self.initial = GameState(to_move=0, pedras=self.jogadores[0], pedras_restantes=pedras_restantes,board =[], utility=0)

    def cria_domino(self):
        pedras = []
        for i in range(7):
            for j in range(7):
                if i >= j:
                    pedras.append(Pedra(i, j, -1))
        return pedras

    def escolhe_pedras(self):
        pedras = self.pedras.copy()
        n = len(self.pedras)
        jogadores = [[] for i in range(4)]
        for j in range(4):
            for k in range(7):
                pos = np.random.randint(0, n)
                jogadores[j].append(pedras.pop(pos))
                n -= 1

        return jogadores

    def actions(self, state):
        moves = []
        n = len(state.board)
        if n != 0:
            pontas = (state.board[0], state.board[n-1])
        i = 0
        if state.to_move == 0:
            for pedra in state.pedras:
                if n != 0:
                    if pedra.igual(pontas[0]):
                        i += 1
                        moves.append((pedra, 0))
                    elif pedra.igual(pontas[1]):
                        i += 1
                        moves.append((pedra, 1))
                else:
                    moves.append((pedra, -1))
        else:
            for pedra in pedras_restantes:
                if n != 0:
                    if pedra.igual(pontas[0]):
                        i += 1
                        moves.append((pedra, 0))
                    elif pedra.igual(pontas[1]):
                        i += 1
                        moves.append((pedra, 1))
                else:
                    moves.append((pedra, -1))

        if i == 0:
            moves.append((Pedra(-1, -1, -1), -1))
        #print("Move")
        #for i in moves:
            #print(i)
        return moves

    def compute_utility(self, to_move, pedras, pedras_restantes, board, move):
        n = len(board)

        if move[0].valor[0] == -1 and n != 0:
            for p in pedras_restantes:
                pontas = (board[0], board[n - 1])
                if p.igual(pontas[0]) == True or p.igual(pontas[1]) == True:
                    return 0
            total = len(pedras)
            soma = 0
            for pedra in pedras:
                soma += pedra.getValor()
            pedras_restantes.sort(key=lambda x: (x.valor[0] + x.valor[1]))
            soma_res = 0
            for i in range(min([total, len(pedras_restantes)])):
                soma_res += pedras_restantes[i].getValor()
            if soma < soma_res:
                if to_move != 0:
                    return -1
                else:
                    return 4
            else:
                if to_move != 0:
                    return 4
                else:
                    return -1
        elif move[0].valor[0] != -1:
            if to_move == 0:
                if len(pedras) == 1:
                    return 4
                else:
                    return 0
            else:
                if len(pedras_restantes) == 3:
                    return 4
                else:
                    return 0
        else:
            return -1

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0

    def display(self, state):
        board = state.board
        print("Board")
        for x in board:
            print(x)

    def result(self, state, move):
        board = state.board.copy()
        pedras = state.pedras.copy()
        pedras_restantes = state.pedras_restantes.copy()
        utility = self.compute_utility(state.to_move, state.pedras, state.pedras_restantes, state.board, move)
        n = len(board)
        if move[0].valor[0] != -1:
            if n != 0:
                pontas = (state.board[0], state.board[n - 1])
                if move[1] == 0:
                    if move[0].valor[0] == pontas[0].valor[0] or move[0].valor[0] == pontas[0].valor[1]:
                        move[0].position = 1
                        if state.board[0].position == -1:
                            state.board[0].position = 1
                    elif move[0].valor[1] == pontas[0].valor[0] or move[0].valor[1] == pontas[0].valor[1]:
                        move[0].position = 0
                        if state.board[0].position == -1:
                            state.board[0].position = 1
                    board.insert(0, move[0])
                elif move[1] == 1:
                    if move[0].valor[0] == pontas[1].valor[0] or move[0].valor[0] == pontas[1].valor[1]:
                        move[0].position = 1
                    elif move[0].valor[1] == pontas[1].valor[0] or move[0].valor[1] == pontas[1].valor[1]:
                        move[0].position = 0
                    board.append(move[0])
            else:
                move[0].position = -1
                board.append(move[0])
            if state.to_move == 0:
                print(move[0])
                pedras.remove(move[0])
                print(len(pedras))
            else:
                pedras_restantes.remove(move[0])

        to_move = (state.to_move + 1) % 4

        new_state = GameState(to_move=to_move, pedras=pedras, pedras_restantes=pedras_restantes,board = board, utility=utility)
        return new_state

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state_res = self.result(state, move)
                self.jogadores[state_res.to_move] = state_res.pedras
                board = state_res.board
                to_move = (state_res.to_move +1)%4
                utility = state_res.utility
                pedras_restantes = []
                for i in range(4):
                    if i != to_move:
                        pedras_restantes += self.jogadores[i]
                state = GameState(to_move=to_move, pedras=self.jogadores[to_move], pedras_restantes=pedras_restantes,board = board, utility=utility)
                if self.terminal_test(state):
                    print("Jogador Vencedor:", state.to_move)
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


d = Domino()
board = [Pedra(0, 0, -1), Pedra(3, 0, 0), Pedra(1, 3, 0), Pedra(1, 1, 1), Pedra(1, 2, 1), Pedra(2, 2, 0),
         Pedra(3, 2, 0), Pedra(3, 3, 1), Pedra(6, 3, 0), Pedra(6, 6, 1), Pedra(2, 6, 0), Pedra(5, 2, 0), Pedra(1, 5, 0),
         Pedra(4, 1, 0), Pedra(4, 4, 0), Pedra(3, 4, 0)]
pedras = [Pedra(3, 5, -1), Pedra(4, 2, -1), Pedra(4, 0, -1)]
pedras_restantes = [Pedra(1, 0, -1), Pedra(5, 5, -1), Pedra(6, 5, -1),
                    Pedra(1, 6, -1), Pedra(4, 5, -1), Pedra(4, 6, -1),
                    Pedra(0, 2, -1), Pedra(0, 5, -1), Pedra(6, 0, -1)]
#GameState = namedtuple('GameState', 'to_move, pedras,pedras_restantes, utility, board')
state = GameState(to_move=0, pedras=pedras, pedras_restantes=pedras_restantes, utility=0, board=board)
acoes = d.actions(state)
print("Jogador")

for i in acoes:
    print("(", i[0], ", ponta=", i[1], ")")
new_state = d.result(state, acoes[0])
print("Após jogar pedra ",  acoes[0][0], " na ponta ", acoes[0][1])
print("Pedras")
for i in new_state.pedras:
    print(i)
print("Pedras Restantes")
for i in new_state.pedras_restantes:
    print(i)
print("Utilidade")
print(new_state.utility)
print("Board")
for i in new_state.board:
    print(i)
state = GameState(to_move=1, pedras=pedras, pedras_restantes=pedras_restantes, utility=0, board=board)
acoes = d.actions(state)
print("Adversário")
for i in acoes:
    print("(", i[0], ", ponta=", i[1], ")")
