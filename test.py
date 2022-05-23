import pygame.draw
from games import *

pygame.init()

SQUARESIZE = 100
GAME_OVER = False

COLUMN_COUNT = 7
ROW_COUNT = 6

GAP_ROWS = 1

WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + GAP_ROWS) * SQUARESIZE

SIZE = (WIDTH, HEIGHT)
SCREEN = pygame.display.set_mode(SIZE)

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (61, 145, 64)

RADIUS = SQUARESIZE // 3

FONT = pygame.font.SysFont("verdana", 60)


class Game(Game):
    def play_test(self, player):
        """Play an n-person, move-alternating game."""
        state = self.initial
        print(player)
        while True:
            if state.to_move == 'X':
                move = player(self, state)
                print("alpha_beta_move: ", move)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.draw_board(state)
                    return self.utility(state, self.to_move(self.initial))
            elif state.to_move == 'O':
                self.draw_board(state)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos_mouse = event.pos
                        print("x value:", pos_mouse[0])
                        column_value = (pos_mouse[0] // SQUARESIZE) + 1
                        print("column_click_in: ", column_value)
                        for move in self.actions(state):
                            if move[1] == column_value:
                                print("Move is: ", move)
                                break
                        state = self.result(state, move)
                        if self.terminal_test(state):
                            self.draw_board(state)
                            return self.utility(state, self.to_move(self.initial))
                    if event.type == pygame.MOUSEMOTION:
                        pygame.draw.rect(SCREEN, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        slider_pos = event.pos[0]
                        pygame.draw.circle(SCREEN, YELLOW, (slider_pos, SQUARESIZE // 2), RADIUS)
            pygame.display.update()
            


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

    def display(self, state):
        board = state.board
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

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

    def draw_board(self, state):
        board = state.board
        y_buffer = SQUARESIZE * GAP_ROWS
        suggested_move = alpha_beta_cutoff_player(self, state)
        for column in range(self.v):
            for row in range(self.h):
                current_square_x = column * SQUARESIZE
                current_square_y = row * SQUARESIZE + y_buffer
                current_square_center = (
                    current_square_x + (SQUARESIZE // 2),
                    current_square_y + (SQUARESIZE // 2)
                )
                pygame.draw.rect(SCREEN, WHITE, (current_square_x, current_square_y, SQUARESIZE, SQUARESIZE))
                pygame.draw.rect(SCREEN, BLUE, (current_square_x, current_square_y, SQUARESIZE, SQUARESIZE), 2)
                if board.get((row + 1, column + 1)) == 'X':
                    pygame.draw.circle(SCREEN, RED, current_square_center, RADIUS)
                elif board.get((row + 1, column + 1)) == 'O':
                    pygame.draw.circle(SCREEN, YELLOW, current_square_center, RADIUS)
                elif row + 1 == suggested_move[0] and column + 1 == suggested_move[1]:
                    if self.terminal_test(state):
                        pygame.draw.circle(SCREEN, BLACK, current_square_center, RADIUS)
                    else:
                        pygame.draw.circle(SCREEN, GREEN, current_square_center, RADIUS)
                else:
                    pygame.draw.circle(SCREEN, BLACK, current_square_center, RADIUS)
        pygame.display.flip()
        pygame.display.update()


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
    return (fours * 10 + threes * 5 + twos * 2) - (opp_fours * 10 + opp_threes * 5 + opp_twos * 2)


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


if __name__ == "__main__":
    print(FONT)
    test = ConnectFour(6, 7, 4)
    utility = test.play_test(alpha_beta_cutoff_player)  # computer moves first1
    if utility < 0:
        label1 = FONT.render("Player Victory!", 1, YELLOW)
        pygame.draw.rect(SCREEN,BLACK,(0,0,WIDTH,SQUARESIZE))
        SCREEN.blit(label1, (40, 10))
        pygame.display.update()
        pygame.time.wait(900)
    elif utility > 0:
        label2 = FONT.render("Computer Victory!", 1, RED)
        pygame.draw.rect(SCREEN,BLACK,(0,0,WIDTH,SQUARESIZE))
        SCREEN.blit(label2, (40, 10))
        pygame.display.update()
        pygame.time.wait(900)
    elif utility == 0:
        label3 = FONT.render("Game is tied", 1, WHITE)
        pygame.draw.rect(SCREEN,BLACK,(0,0,WIDTH,SQUARESIZE))
        SCREEN.blit(label3, (40, 10))
        pygame.display.update()
        pygame.time.wait(900)
