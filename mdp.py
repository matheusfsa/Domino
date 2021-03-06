"""Markov Decision Processes (Chapter 17)

First we define an MDP, and the special case of a GridMDP, in which
states are laid out in a 2-dimensional grid.  We also represent a policy
as a dictionary of {state:action} pairs, and a Utility function as a
dictionary of {state:number} pairs.  We then define the value_iteration
and policy_iteration algorithms."""
from collections import namedtuple
from utils import argmax, vector_add, print_table
from grid import orientations, turn_right, turn_left
from domino import Domino,GameState
import random
from collections import namedtuple

LearningState = namedtuple('LearningState', 'pedras,pedras_restantes,  pontas')


class MDP:

    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of P(s' | s, a) being a probability number for each
    state/state/action triplet, we instead have T(s, a) return a
    list of (p, s') pairs.  We also keep track of the possible states,
    terminal states, and actions for each state. [page 646]"""

    def __init__(self, init, actlist, terminals, gamma=.9):
        self.init = init
        self.actlist = actlist
        self.terminals = terminals
        if not (0 <= gamma < 1):
            raise ValueError("An MDP must have 0 <= gamma < 1")
        self.gamma = gamma
        self.states = set()
        self.reward = {}

    def R(self, state):
        "Return a numeric reward for this state."
        return self.reward[state]

    def T(self, state, action):
        """Transition model.  From a state and an action, return a list
        of (probability, result-state) pairs."""
        raise NotImplementedError

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.terminals:
            return [None]
        else:
            return self.actlist


class DominoMDP(MDP):

    def __init__(self,domino, player, gamma=.9):
        self.domino = domino
        self.player = player
        MDP.__init__(self, self.convert(domino.initial), actlist=orientations,
                     terminals=[], gamma=gamma)
        self.init = domino.initial
        self.reward[self.convert(self.init)] = domino.eval(domino.initial, player)

    def R(self, state):
        s = self.convert(state)
        if state.utility == 0:
            self.reward[s] = -0.1
        else:
            self.reward[s] = state.utility
        return self.reward[s]

    def T(self, state, action):
        if state.to_move == self.player:
            return [(1, self.domino.result(state, action, self.player))]
        else:
            return [(1/len(state.pedras_restantes), self.domino.result(state, action, state.to_move))]

    def convert(self,state):
        pedras = tuple()
        state.pedras.sort(key=lambda x: (x.valor[0] + x.valor[1]))
        state.pedras_restantes.sort(key=lambda x: (x.valor[0] + x.valor[1]))
        for pedra in state.pedras:
            pedras = pedras + (pedra.tupla(),)
        pedras_restantes = tuple()
        for pedra in state.pedras_restantes:
            pedras_restantes = pedras_restantes + (pedra.tupla(),)
        ponta1, ponta2 = None, None
        pontas = ()
        if state.ponta1 is not None:
            p1 = state.ponta1.position
            p2 = state.ponta1.position
            if p1 != -1:
                ponta1, ponta2 = state.ponta1.valor[p1],  state.ponta2.valor[p1]
            else:
                ponta1, ponta2 = state.ponta1.tupla()
            if ponta1 > ponta2:
                pontas = (ponta1, ponta2)
            else:
                pontas = (ponta2, ponta1)
        return LearningState(pedras=pedras, pedras_restantes=pedras_restantes, pontas=pontas)

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.domino.terminal_test(state):
            return [None]
        else:
            return self.state.moves


class GridMDP(MDP):

    """A two-dimensional grid MDP, as in [Figure 17.1].  All you have to do is
    specify the grid as a list of lists of rewards; use None for an obstacle
    (unreachable state).  Also, you should specify the terminal states.
    An action is an (x, y) unit vector; e.g. (1, 0) means move east."""

    def __init__(self, grid, terminals, init=(0, 0), gamma=.9):
        grid.reverse()  # because we want row 0 on bottom, not on top
        MDP.__init__(self, init, actlist=orientations,
                     terminals=terminals, gamma=gamma)
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        for x in range(self.cols):
            for y in range(self.rows):
                self.reward[x, y] = grid[y][x]
                if grid[y][x] is not None:
                    self.states.add((x, y))

    def T(self, state, action):
        if action is None:
            return [(0.0, state)]
        else:
            return [(0.8, self.go(state, action)),
                    (0.1, self.go(state, turn_right(action))),
                    (0.1, self.go(state, turn_left(action)))]

    def go(self, state, direction):
        "Return the state that results from going in this direction."
        state1 = vector_add(state, direction)
        return state1 if state1 in self.states else state

    def to_grid(self, mapping):
        """Convert a mapping from (x, y) to v into a [[..., v, ...]] grid."""
        return list(reversed([[mapping.get((x, y), None)
                               for x in range(self.cols)]
                              for y in range(self.rows)]))

    def to_arrows(self, policy):
        chars = {
            (1, 0): '>', (0, 1): '^', (-1, 0): '<', (0, -1): 'v', None: '.'}
        return self.to_grid({s: chars[a] for (s, a) in policy.items()})

# ______________________________________________________________________________

""" [Figure 17.1]
A 4x3 grid environment that presents the agent with a sequential decision problem.
"""


# ______________________________________________________________________________


def value_iteration(mdp, epsilon=0.001):
    "Solving an MDP by value iteration. [Figure 17.4]"
    U1 = {s: 0 for s in mdp.states}
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    while True:
        U = U1.copy()
        delta = 0
        for s in mdp.states:
            U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
                                        for a in mdp.actions(s)])
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma:
            return U


def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), key=lambda a: expected_utility(a, s, U, mdp))
    return pi


def expected_utility(a, s, U, mdp):
    "The expected utility of doing a in state s, according to the MDP and U."
    return sum([p * U[s1] for (p, s1) in mdp.T(s, a)])

# ______________________________________________________________________________


def policy_iteration(mdp):
    "Solve an MDP by policy iteration [Figure 17.7]"
    U = {s: 0 for s in mdp.states}
    pi = {s: random.choice(mdp.actions(s)) for s in mdp.states}
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = argmax(mdp.actions(s), key=lambda a: expected_utility(a, s, U, mdp))
            if a != pi[s]:
                pi[s] = a
                unchanged = False
        if unchanged:
            return pi


def policy_evaluation(pi, U, mdp, k=20):
    """Return an updated utility mapping U from each state in the MDP to its
    utility, using an approximation (modified policy iteration)."""
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = R(s) + gamma * sum([p * U[s1] for (p, s1) in T(s, pi[s])])
    return U

__doc__ += """
>>> pi = best_policy(sequential_decision_environment, value_iteration(sequential_decision_environment, .01))

>>> sequential_decision_environment.to_arrows(pi)
[['>', '>', '>', '.'], ['^', None, '^', '.'], ['^', '>', '^', '<']]

>>> print_table(sequential_decision_environment.to_arrows(pi))
>   >      >   .
^   None   ^   .
^   >      ^   <

>>> print_table(sequential_decision_environment.to_arrows(policy_iteration(sequential_decision_environment)))
>   >      >   .
^   None   ^   .
^   >      ^   <
"""
