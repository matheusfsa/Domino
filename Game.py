import random


class Game:
    """A game has a utility for each
    state and a terminal test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))

class StochasticGame(Game):
    """A stochastic game includes uncertain events which influence
    the moves of players at each state. To create a stochastic game, subclass
    this class and implement chances and outcome along with the other
    unimplemented game class methods."""

    def chances(self, state):
        """Return a list of all possible uncertain events at a state."""
        raise NotImplementedError

    def outcome(self, state, chance):
        """Return the state which is the outcome of a chance trial."""
        raise NotImplementedError

    def probability(self, chance):
        """Return the probability of occurence of a chance."""
        raise NotImplementedError

    def play_game(self, *players):
        """Play an n-person, move-alternating stochastic game."""
        state = self.initial
        while True:
            for player in players:
                chance = random.choice(self.chances(state))
                state = self.outcome(state, chance)
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))