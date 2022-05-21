from games import *
import pygame
import sys

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (61, 145,64)


class TicTacToe(Game):
    """Play TicTacToe on an h x v board, with Max (first player) playing 'X'.
    A state has the player to move, a cached utility, a list of moves in
    the form of a list of (x, y) positions, and a board, in the form of
    a dict of {(x, y): Player} entries, where Player is 'X' or 'O'."""

    def __init__(self, h=3, v=3, k=3):
        self.h = h
        self.v = v
        self.k = k
        moves = [(x, y) for x in range(1, h + 1)
                 for y in range(1, v + 1)]
        self.initial = GameState(to_move='X', utility=0, board={}, moves=moves)

    def actions(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def result(self, state, move):
        if move not in self.actions(state):
            return state  # Illegal move has no effect
        board = state.board.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state, suggested_move = (10,10)):
        board = state.board
        square_size = 100
        gap_rows = 1
        y_buffer = square_size * gap_rows
        width = self.v * square_size
        height = (self.h + gap_rows) * square_size
        gui_board_size = (width, height)
        screen = pygame.display.set_mode(gui_board_size)
        screen.fill(WHITE)
        radius = square_size // 3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # filling blank row circles
            for column in range(self.v):
                #add 7 to call to remove top row
                current_square_x, current_square_y = (column * square_size), 0
                current_square_center = (
                    current_square_x + (square_size // 2),
                    current_square_y + (square_size // 2)
                )
                pygame.draw.circle(screen, BLACK, current_square_center, radius)
            for column in range(self.v):
                for row in range(self.h):
                    current_square_x = column * square_size
                    current_square_y = row * square_size + y_buffer
                    current_square_center = (
                        current_square_x + (square_size // 2),
                        current_square_y + (square_size // 2)
                    )
                    pygame.draw.rect(screen, BLUE, (current_square_x, current_square_y, square_size, square_size), 2)
                    if board.get((row + 1, column + 1)) == 'X':
                        pygame.draw.circle(screen, RED, current_square_center, radius)
                    elif board.get((row + 1, column + 1)) == 'O':
                        pygame.draw.circle(screen, YELLOW, current_square_center, radius)
                    elif row + 1 == suggested_move[0] and column + 1 == suggested_move[1]:
                            pygame.draw.circle(screen, GREEN, current_square_center, radius)
                    else:
                        pygame.draw.circle(screen, BLACK, current_square_center, radius)
            pygame.display.flip()

    def compute_utility(self, board, move, player):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""
        if (self.k_in_row(board, move, player, (0, 1)) or
                self.k_in_row(board, move, player, (1, 0)) or
                self.k_in_row(board, move, player, (1, -1)) or
                self.k_in_row(board, move, player, (1, 1))):
            return +1 if player == 'X' else -1
        else:
            return 0

    def k_in_row(self, board, move, player, delta_x_y):
        """Return true if there is a line through move on board for player."""
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k


class ConnectFour(TicTacToe):
    """A TicTacToe-like game in which you can only make a move on the bottom
    row, or in a square directly above an occupied square.  Traditionally
    played on a 7x6 board and requiring 4 in a row."""

    def __init__(self, h=7, v=6, k=4):
        TicTacToe.__init__(self, h, v, k)

    def actions(self, state):
        return [(x, y) for (x, y) in state.moves
                if x == self.h or (x + 1, y) in state.board]


def alpha_beta_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


def query_player(game, state):
    """Make a move by querying standard input."""
    suggested_move = alpha_beta_cutoff_search(state, game, 4, None, evaluation_function)
    print("current state:")
    game.display(state, suggested_move)
    print("available moves: {}".format(game.actions(state)))
    #suggested_move = alpha_beta_cutoff_search(state, game, 4, None, evaluation_function)
    print("suggested move (represented by green token): ", suggested_move)

    print("")
    move = None
    if game.actions(state):
        move_string = input('Your move? ')
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print('no legal moves: passing turn to next player')
    return move


def evaluation_function(state):
    if state.to_move == 'X':
        other_player = 'O'
    else:
        other_player = 'X'
    fours = connect_count(state.board, state.to_move, 4)
    threes = connect_count(state.board, state.to_move, 3)
    twos = connect_count(state.board, state.to_move, 2)
    opp_fours = connect_count(state.board, other_player, 4)
    opp_threes = connect_count(state.board, other_player, 3)
    opp_twos = connect_count(state.board, other_player, 2)
    return (fours * 100 + threes * 5 + twos * 2) - (opp_fours * 100 + opp_threes * 5 + opp_twos * 2)


def connect_count(board, player, streak):
    count = 0
    for row in range(1, 8):
        for column in range(1, 7):
            move = row, column
            if board.get(move) == player:
                count += vertical_count(row, column, board, player, streak)
                count += horizontal_count(row, column, board, player, streak)
                count += diagonal_count(row, column, board, player, streak)
    return count


def vertical_count(row, column, board, player, streak):
    count = 0
    for x in range(row, 7):
        if board.get((x, column)) == player:
            count += 1
        else:
            break
    if count >= streak:
        return 1
    else:
        return 0


def horizontal_count(row, column, board, player, streak):
    count = 0
    for y in range(column, 6):
        if board.get((row, y)) == player:
            count += 1
        else:
            break
    if count >= streak:
        return 1
    else:
        return 0


def diagonal_count(row, column, board, player, streak):
    total = 0
    count = 0
    y = column

    for x in range(row, 7):
        if y > 6:
            break
        elif board.get((x, y)) == player:
            count += 1
        else:
            break
        y += 1
    if count >= streak:
        total += 1
    count = 0
    y = column
    for x in range(row, -1, -1):
        if y > 6:
            break
        elif board.get((x, y)) == player:
            count += 1
        else:
            break
        y += 1
    if count >= streak:
        total += 1
    return total


def alpha_beta_cutoff_player(game, state):
    return alpha_beta_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=evaluation_function)


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


if __name__ == "__main__":
    pygame.init()
    test = ConnectFour(6, 7, 4)

    utility = test.play_game(alpha_beta_cutoff_player, query_player)  # computer moves first1
    if utility < 0:
        print("MIN won the game")
    elif utility > 0:
        print("MAX won the game")
    elif utility == 0:
        print("Game is a tie.")