import numpy as np
from Game import Game, StochasticGame
from collections import namedtuple
import random
from utils import argmax, vector_add
import time

infinity = float('inf')
GameState = namedtuple('GameState', 'to_move,pedras,pedras_restantes,  ponta1, ponta2, moves, utility')

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

def expectiminimax(game,state):
    """Return the best move for a player after dice are thrown. The game tree
	includes chance nodes along with min and max nodes. [Figure 5.11]"""
    player = game.to_move(state)
    d = 0
    n = len(state.pedras)
    if n == 7:
        d = 7
    elif n<= 6:
        d = 9
    def max_value(state, depth):
        #print("Profundidade: ", depth)
        v = -infinity
        if depth >= d:
            return game.eval(state, player)
        #for i in state.moves:
        #    print("(", i[0], ", ponta=", i[1], ")")

        for acao in game.actions(state):
            v = max(v, chance_node(state, acao, depth))
        return v

    def min_value(state, depth):
        if depth >= d:
            return game.eval(state, player)
        v = infinity
        for acao in game.actions(state):
            v = min(v, chance_node(state, acao, depth))
        return v

    def chance_node(state, action, depth):
        res_state = game.result(state, action, player)
        if game.terminal_test(res_state):
            return game.utility(res_state, player)
        if depth >= d:
            return game.eval(state, player)
        sum_chances = 0
        chances = game.chances(res_state)
        num_chances = len(chances)
        for chance in chances:
            res_state = game.outcome(res_state, chance)
            util = 0
            if res_state.to_move == player:
                util = max_value(res_state, depth+1)
            else:
                util = min_value(res_state, depth+1)
            sum_chances += util * game.probability(chance)
        return sum_chances / num_chances

    # Body of expectiminimax:
    """k = -infinity
    action = None
    for a in game.actions(state):
        print(a[0])
        c = chance_node(state, a, 1)
        print(c)
        k = max(k,c)
        action = a
    print("k: ", k)
    return action"""
    return argmax(game.actions(state),
                  key=lambda a: chance_node(state, a, 1), default=None)

class Pedra:

    def __init__(self, a, b,position):
        self.valor = (a, b)
        self.position = position

    def __eq__(self, other):
        return (self.valor[0] == other.valor[0] and self.valor[1] == other.valor[1]) or (self.valor[0] == other.valor[1] and self.valor[1] == other.valor[0])

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


def imprimestate(res_state):
    print("To move: ", res_state.to_move)
    print("Ponta 1 = ", res_state.ponta1, " Ponta 2 = ", res_state.ponta2)
    print("Pedras")
    for i in res_state.pedras:
        print(i)
    print("Restantes")
    for i in res_state.pedras_restantes:
        print(i)
    print("Moves")
    for i in res_state.moves:
        print("(", i[0], ", ponta=", i[1], ")")

class Domino(StochasticGame):

    def __init__(self):
        self.pedras = self.cria_domino()
        self.jogadores = self.escolhe_pedras()
        pedras_restantes = []
        for i in range(1, 4):
            pedras_restantes += self.jogadores[i]
        self.initial = GameState(to_move=0, pedras=self.jogadores[0].copy(), pedras_restantes=pedras_restantes, ponta1=None,ponta2=None,
                                 moves=self.moves(0,self.jogadores[0], pedras_restantes, None, None, 0), utility=0)

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
        return state.moves

    def buchas(self, pedras):
        res = 0
        for pedra in pedras:
            if pedra.valor[0] == pedra.valor[1]:
                if pedra.valor[0] != 0:
                    res += pedra.valor[0]
                else:
                    res += 1
        return res

    def eval(self, state, player):
        n = len(state.pedras)
        m = len(state.pedras_restantes)/3
        to_move = 4 if state.to_move == 0 else state.to_move - 1
        if to_move == player:
            #print("player : ", player)
            buchas = self.buchas(state.pedras)
            n_pedras = n
            delta = n - m
            return -0.2*buchas - 0.2*n_pedras + 0.9*delta
        else:
            buchas = self.buchas(state.pedras_restantes)/3
            n_pedras = m

            delta = m - n
            return -0.1 * buchas - 0.1 * n_pedras + 5 * delta

    def moves(self,to_move,pedras, pedras_restantes, ponta1, ponta2, player):
        moves = []
        i = 0
        if to_move == player:

            for pedra in pedras:
                if ponta1 is not None:
                    if pedra.igual(ponta1):
                        i += 1
                        moves.append((pedra, 0))
                    elif pedra.igual(ponta2):
                        i += 1
                        moves.append((pedra, 1))
                else:
                    moves.append((pedra, -1))
        else:
            for pedra in pedras_restantes:
                if ponta1 is not None:
                    if pedra.igual(ponta1):
                        i += 1
                        moves.append((pedra, 0))
                    elif pedra.igual(ponta2):
                        i += 1
                        moves.append((pedra, 1))
                else:
                    moves.append((pedra, -1))

        if i == 0:
            moves.append((Pedra(-1, -1, -1), -1))
        return moves

    def compute_utility(self, to_move, pedras, pedras_restantes, ponta1, ponta2, move,player):

        if move[0].valor[0] == -1 and ponta1 is not None:
            for p in pedras_restantes:
                if p.igual(ponta1) or p.igual(ponta2):
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
            if to_move == player:
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

    def soma_pedras(self,i):
        res = 0
        for pedra in self.jogadores[i]:
            res += pedra.getValor()
        return res

    def menor_soma(self):
        return argmax([0, 1, 2, 3],
               key=lambda a: -self.soma_pedras(a), default=None)

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0

    def display(self, state):
        imprimestate(state)

    def vitoria(self, i, state):
        print("Utility: ", state.utility)
        if state.utility == 4:
            return i
        elif state.utility == 0:
            return -1
        else:
            return self.menor_soma()



    def result(self, state, move,player):
        pedras = state.pedras.copy()
        pedras_restantes = state.pedras_restantes.copy()
        ponta1 = state.ponta1
        ponta2 = state.ponta2
        utility = self.compute_utility(state.to_move, state.pedras, state.pedras_restantes, state.ponta1,state.ponta2, move, player)

        if move[0].valor[0] != -1:
            if state.ponta1 is not None:
                if move[1] == 0:
                    if move[0].valor[0] == state.ponta1.valor[0] or move[0].valor[0] == state.ponta1.valor[1]:
                        move[0].position = 1
                        if state.ponta1.position == -1:
                            state.ponta1.position = 1
                    elif move[0].valor[1] == state.ponta1.valor[0] or move[0].valor[1] == state.ponta1.valor[1]:
                        move[0].position = 0
                        if state.ponta1.position == -1:
                            state.ponta1.position = 1
                    ponta1 = move[0]
                elif move[1] == 1:
                    if move[0].valor[0] == state.ponta2.valor[0] or move[0].valor[0] == state.ponta2.valor[1]:
                        move[0].position = 1
                    elif move[0].valor[1] == state.ponta2.valor[0] or move[0].valor[1] == state.ponta2.valor[1]:
                        move[0].position = 0
                    ponta2 = move[0]

            else:
                move[0].position = -1
                ponta1 = move[0]
                ponta2 = move[0]
            if state.to_move == player:
                pedras.remove(move[0])
            else:
                pedras_restantes.remove(move[0])

        to_move = (state.to_move + 1) % 4
        new_state = GameState(to_move=to_move, pedras=pedras, pedras_restantes=pedras_restantes, ponta1=ponta1,
                              ponta2=ponta2, moves=self.moves(to_move, pedras, pedras_restantes, ponta1, ponta2, player), utility=utility)
        return new_state

    def ponta1(self, move):
        return move[1] == 0

    def ponta2(self, move):
        return move[1] == 1


    def chances(self, state):
        n_moves = len(state.moves)
        lista = []
        if state.to_move != 0:
            n = len(state.pedras_restantes)

            p1 = (1, list(filter(self.ponta1, state.moves)), n_moves, n)
            if len(p1[1]) > 0:
                lista.append(p1)
            p2 = (2, list(filter(self.ponta2, state.moves)), n_moves, n)
            if len(p2[1]) > 0:
                lista.append(p2)
            pi = (-1, [(Pedra(-1, -1, -1), -1)], n_moves, n)
            lista.append(pi)

            return lista
        else:
            return [(0, state.moves, n_moves, len(state.pedras))]

    def probability(self, chance):
        if chance[0] == 1 or chance[0] == 2:
            return len(chance[1])/chance[3]
        elif chance[0] == -1:
            return 1 - (chance[2]/chance[3])
        else:
            return 1

    def imprime_jogadores(self):
        i = 0
        for jogador in self.jogadores:
            print("Jogador ", i)
            i+=1
            for pedra in jogador:
                print(pedra)

    def outcome(self, state, chance):
        return GameState(to_move=state.to_move, pedras=state.pedras, pedras_restantes=state.pedras_restantes, ponta1=state.ponta1,
                         ponta2=state.ponta2, moves=chance[1], utility=state.utility)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        inicio = time.time()
        k = 0
        while True:
            print("Rodada: ", k)
            k += 1
            for player in players:
                #print("Antes")
                #imprimestate(state)
                move = player(self, state)
                self.imprime_jogadores()
                print("To_move: ", state.to_move)
                print("Pontas: ", state.ponta1, " ", state.ponta2)
                print("Move: ", move[0], ", ", move[1])
                #print("Move: ", move[0], ", ", move[1])
                if move[0].valor[0] != -1:
                    self.jogadores[state.to_move].remove(move[0])

                state_res = self.result(state, move, state.to_move)
                vencedor = self.vitoria(state.to_move, state_res)
                if vencedor != -1:
                    fim = time.time()
                    #print("Jogador Vencedor:", vencedor)
                    self.imprime_jogadores()
                    #print("Pontas: ", state_res.ponta1, " ", state_res.ponta2)
                    #print("Tempo: ", fim - inicio)
                    return vencedor
                ponta1 = state_res.ponta1
                ponta2 = state_res.ponta2
                to_move = state_res.to_move
                pedras_restantes = []
                for i in range(4):
                    if i != to_move:
                        pedras_restantes += self.jogadores[i]
                state = GameState(to_move=to_move, pedras=self.jogadores[to_move].copy(), pedras_restantes=pedras_restantes, ponta1=ponta1, ponta2=ponta2,
                                  moves=self.moves(to_move, self.jogadores[to_move], pedras_restantes, ponta1, ponta2, to_move),
                                  utility=self.compute_utility(to_move, self.jogadores[to_move], pedras_restantes, ponta1, ponta2, move,to_move))
                #print("Depois")
                #imprimestate(state)


"""Testes"""
d = Domino()
#move = expectiminimax(d,d.initial)
#d.imprime_jogadores()
#print("\n", move[0])
#print(d.play_game(expectiminimax, random_player, random_player, random_player))
"""jogadores = np.zeros(4)
s = 0
for i in range(10):
    d = Domino()
    vencedor = d.play_game(expectiminimax, random_player, random_player, random_player)
    s += 1
print(s/10)"""
"""board = [Pedra(0, 0, -1), Pedra(3, 0, 0), Pedra(1, 3, 0), Pedra(1, 1, 1), Pedra(1, 2, 1), Pedra(2, 2, 0),
         Pedra(3, 2, 0), Pedra(3, 3, 1), Pedra(6, 3, 0), Pedra(6, 6, 1), Pedra(2, 6, 0), Pedra(5, 2, 0), Pedra(1, 5, 0),
         Pedra(4, 1, 0), Pedra(4, 4, 0), Pedra(3, 4, 0)]"""
ponta1 = Pedra(1, 2, 1)
ponta2 = Pedra(5, 2, 0)
pedras = [Pedra(3, 5, -1), Pedra(4, 2, -1), Pedra(4, 0, -1),Pedra(4, 1, 0),Pedra(1, 1, 1)]
pedras_restantes = [Pedra(1, 0, -1), Pedra(5, 5, -1), Pedra(6, 5, -1),
                    Pedra(1, 6, -1), Pedra(6, 3, -1), Pedra(4, 6, -1),
                    Pedra(0, 2, -1), Pedra(0, 5, -1), Pedra(6, 0, -1),
                    Pedra(3, 4, 0),Pedra(4, 4, 0), Pedra(0, 0, -1),
                    Pedra(3, 0, 0), Pedra(1, 3, 0),  Pedra(1, 5, 0)]
#GameState = namedtuple('GameState', 'to_move, pedras,pedras_restantes, utility, board')
state = GameState(to_move=0, pedras=pedras, pedras_restantes=pedras_restantes, ponta1=ponta1, ponta2=ponta2,
                  moves=d.moves(0, pedras, pedras_restantes, ponta1, ponta2, 0), utility=0)
#print("Ação")
#state = d.initial
#move = expectiminimax(d,d.initial)
#file = open("res.txt","a")
#file.write(move[0].__str__() + " ponta = " + str(move[1])+"\n")

#print(d.play_game(expectiminimax, random_player, random_player, random_player))
"""acoes = d.actions(state2)


for i in acoes:
    print("(", i[0], ", ponta=", i[1], ")")

print("Chances")
for i in d.chances(state2):
    print("\n\nPonta ", i[0])
    for moves in i[1]:
        print("(",moves[0], ", ponta=", moves[1], ")")
    print("Probabilidade: ", d.probability(i))
    print("Ações")
    for s in d.outcome(state2, i).moves:
        print("(", s[0], ", ponta=", s[1], ")")"""

"""new_state = d.result(state, acoes[0])
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
print("Ponta1", new_state.ponta1)
print("Ponta2", new_state.ponta2)"""
"""state = GameState(to_move=1, pedras=pedras, pedras_restantes=pedras_restantes, utility=0, board=board)
acoes = d.actions(state)
print("Adversário")
for i in acoes:
    print("(", i[0], ", ponta=", i[1], ")")"""
