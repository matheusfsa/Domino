from collections import defaultdict
from utils import argmax
from mdp import MDP, policy_evaluation, DominoMDP
from domino import Domino, imprimestate, GameState,expectiminimax
from collections import namedtuple
import random
import pickle
import time

def random_player(d, percept):
    """A player that chooses a legal move at random."""
    if len(percept.moves) > 0:
        return random.choice(percept.moves)
    else:
        return None

class QLearningAgent:
    """ An exploratory Q-learning agent. It avoids having to learn the transition
        model because the Q-value of a state can be related directly to those of
        its neighbors. [Figure 21.8]
    """
    def __init__(self, mdp, Ne, Rplus, Q, alpha=None):

        self.gamma = mdp.gamma
        self.terminals = mdp.terminals
        self.all_act = mdp.actlist
        self.Ne = Ne  # iteration limit in exploration function
        self.Rplus = Rplus  # large value to assign before iteration limit
        self.Q = Q
        self.Nsa = defaultdict(float)
        self.s = [None, None, None, None]
        self.a = [None, None, None, None]
        self.r = [None, None, None, None]
        self.mdp = mdp

        if alpha:
            self.alpha = alpha
        else:
            self.alpha = lambda n: 1./(1+n)  # udacity video

    def f(self, u, n):
        """ Exploration function. Returns fixed Rplus untill
        agent has visited state, action a Ne number of times.
        Same as ADP agent in book."""
        if n < self.Ne:
            return self.Rplus
        else:
            return u

    def actions_in_state(self, state):
        """ Returns actions possible in given state.
            Useful for max and argmax. """
        if state.utility != 0:
            return [None]
        else:
            return state.moves

    def __call__(self, d, percept):
        s1, r1 = self.update_state(percept)
        Q, Nsa, s, a, r = self.Q, self.Nsa, self.s[percept.to_move], self.a[percept.to_move], self.r[percept.to_move]
        alpha, gamma, terminals, actions_in_state = self.alpha, self.gamma, self.terminals, self.actions_in_state
        if s1.utility != 0:
            Q[self.mdp.convert(s1), None] = r1
        if s is not None:
            Nsa[self.mdp.convert(s),  convertaction(a)] += 1
            Q[self.mdp.convert(s), convertaction(a)] += alpha(Nsa[self.mdp.convert(s), convertaction(a)]) * (r + gamma * max(Q[self.mdp.convert(s1), convertaction(a1)] for a1 in actions_in_state(s1))
                                             - Q[self.mdp.convert(s), convertaction(a)])
        if s1.utility != 0:
            self.s[percept.to_move] = self.a[percept.to_move] = self.r[percept.to_move] = None
        else:
            self.s[percept.to_move], self.r[percept.to_move] = s1, r1
            self.a[percept.to_move] = argmax(actions_in_state(s1), key=lambda a1: self.f(Q[self.mdp.convert(s1), convertaction(a1)], Nsa[self.mdp.convert(s1), convertaction(a1)]))
        return self.a[percept.to_move]

    def update_state(self, percept):
        ''' To be overridden in most cases. The default case
        assumes the percept to be of type (state, reward)'''
        return percept,self.mdp.R(percept)

def convertaction(a):
    if a is not None:
        return a[0].tupla(), a[1]
    return None

def run_single_trial(agent_program, mdp):
    ''' Execute trial for given agent_program
    and mdp. mdp should be an instance of subclass
    of mdp.MDP '''

    def take_single_action(mdp, s, a):
        '''
        Selects outcome of taking action a
        in state s. Weighted Sampling.
        '''
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        imprimestate(s)
        for probability_state in mdp.T(s, a):
            probability, state = probability_state
            cumulative_probability += probability
            if x < cumulative_probability:
                break
        return state

    current_state = mdp.init
    while True:
        current_reward = mdp.R(current_state)
        percept = (current_state, current_reward)
        next_action = agent_program(percept)
        if next_action is None:
            break
        current_state = take_single_action(mdp, current_state, next_action)

def play_game_mdp(mdp,*players):
    d = Domino()
    state = d.initial
    k = 0
    while True:
        for player in players:
            move = player(d,state)
            if move is not None:
                if move[0].valor[0] != -1:
                    d.jogadores[state.to_move].remove(move[0])
                state_res = d.result(state, move, state.to_move)
                ponta1 = state_res.ponta1
                ponta2 = state_res.ponta2
                to_move = state_res.to_move
                pedras_restantes = []
                for i in range(4):
                    if i != to_move:
                        pedras_restantes += d.jogadores[i]

                state = GameState(to_move=to_move, pedras=d.jogadores[to_move].copy(),
                                  pedras_restantes=pedras_restantes, ponta1=ponta1, ponta2=ponta2,
                                  moves=d.moves(to_move, d.jogadores[to_move], pedras_restantes, ponta1, ponta2,
                                                to_move),
                                  utility=state_res.utility)
            else:
                vencedor = d.vitoria(state)
                if vencedor != -1:
                    return  vencedor




if __name__ == '__main__':
    domino_decision_environment = DominoMDP(Domino(), 0)
    q_agent = QLearningAgent(domino_decision_environment, Ne=5, Rplus=4,Q=defaultdict(float), alpha=lambda n: 60./(59+n))
    #current_reward = domino_decision_environment.R(domino_decision_environment.init)
    #percept = (domino_decision_environment.init, current_reward)
    #print(q_agent(percept))
    for i in range(3000):
        play_game_mdp(domino_decision_environment, q_agent, q_agent, q_agent, q_agent)

    v0 = 0
    v1 = 0

    print(len(q_agent.Q))
    wins = [0, 0, 0, 0]
    graphs = [[],[],[],[]]
    media = 0.0
    i = 0
    file = open("res.txt", "a")
    for i in range(200):
        print("Iteracao: ", i)
        inicio1 = time.time()
        v = play_game_mdp(domino_decision_environment, q_agent, expectiminimax, random_player, random_player)
        fim1 = time.time()
        t = (fim1 - inicio1)/60
        media += t/200
        wins[v] += 1
        print("Tempo: ", t)
        print("Wins: ", wins)
        for agent in [0, 1, 2, 3]:
            graphs[agent].append((i, wins[agent]))
        file.write("i: " + str(i))
        file.write(str(graphs) + "\n")
    print("Tempo: ", media*200)
    print("Tempo médio: ", media)
    print("Wins: ", wins)
    print(graphs)
    """
    U = defaultdict(lambda: -1000.)  # Very Large Negative Value for Comparison see below.
    for state_action, value in q_agent.Q.items():
        state, action = state_action
        if U[state] < value:
            U[state] = value
    print(U)
    """

    """
   with open('q_data.txt', 'wb') as output:
        pickle.dump(q_agent.Q, output, pickle.HIGHEST_PROTOCOL)
    """
