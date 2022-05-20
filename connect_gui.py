import numpy as np
import pygame
import sys
import math

'''RGB Color Values'''
CYAN = (0,255,255)
BLACK = (0,0,0)
GREEN = (0,128,0)
MAROON = (128,0,0)

'''Column and Row Counter, Square size)'''
COL = 7
ROW = 6
SQ_SIZE = 100

def create_board():
    board = np.zeros((ROW,COL))
    return board

def print_board(board):
	print(np.flip(board, 0))

'''To check the location'''
def check_location(board, column):
    return board[ROW-1][column] == 0

'''To drop token to right row and column'''
def token_drop(board, row, column, token):
    board[row][column] = token

def empty_row(board, column):
    for r in range(ROW):
        if board[r][column] == 0:
            return r

'''Drawing a 6 X 7 board for connect4 game'''
def d_board(board):
	for c in range(COL):
		for r in range(ROW):
			pygame.draw.rect(window, CYAN, (c*SQ_SIZE, r*SQ_SIZE+SQ_SIZE, SQ_SIZE, SQ_SIZE))
			pygame.draw.circle(window, BLACK, (int(c*SQ_SIZE+SQ_SIZE/2), int(r*SQ_SIZE+SQ_SIZE+SQ_SIZE/2)), RAD)
	
	for c in range(COL):
		for r in range(ROW):		
			if board[r][c] == 1:
				pygame.draw.circle(window, MAROON, (int(c*SQ_SIZE+SQ_SIZE/2), height-int(r*SQ_SIZE+SQ_SIZE/2)), RAD)
			elif board[r][c] == 2:
				pygame.draw.circle(window, GREEN, (int(c*SQ_SIZE+SQ_SIZE/2), height-int(r*SQ_SIZE+SQ_SIZE/2)), RAD)
	pygame.display.update()

board = create_board()
game_over = False
turn = 0
pygame.init()

width = COL * SQ_SIZE
height = (ROW + 1) * SQ_SIZE
size = (width, height)
RAD = int(SQ_SIZE/2 - 5)

window = pygame.display.set_mode(size)
d_board(board)
pygame.display.update()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
        	pygame.draw.rect(window, BLACK, (0, 0, width, SQ_SIZE))
        	position = event.pos[0]
        	if turn == 0:
        		pygame.draw.circle(window, MAROON, (position, int(SQ_SIZE/2)), RAD)
        	else:
        		pygame.draw.circle(window, GREEN, (position, int(SQ_SIZE/2)), RAD)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            position = event.pos[0]
            if turn == 0:
                position = event.pos[0]
                column = int(math.floor(position/SQ_SIZE))

                if check_location(board, column):
                    row = empty_row(board, column)
                    token_drop(board, row, column, 1)
            else:
                position = event.pos[0]
                column = int(math.floor(position/SQ_SIZE))

                if check_location(board, column):
                    row = empty_row(board, column)
                    token_drop(board, row, column, 2)
            
            print_board(board)
            d_board(board)
            turn = turn + 1
            turn = turn % 2
