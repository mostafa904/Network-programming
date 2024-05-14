import pygame
import socket
import sys
import math

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7


def create_board():
    board = [[0] * COLUMN_COUNT for _ in range(ROW_COUNT)]
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print("\n".join([" ".join(map(str, row)) for row in board]))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True


def draw_board(screen, board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (
            int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def receive_data(client_socket):
    data = client_socket.recv(1024).decode()
    if data:
        return eval(data)
    return None


def send_data(client_socket, data):
    try:
        client_socket.sendall(str(data).encode())
    except ConnectionAbortedError as e:
        print(f"Connection aborted: {e}")


# Initialize Pygame
pygame.init()

# Set up the window
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4 Client")

# Define game constants
RADIUS = int(SQUARESIZE / 2 - 5)

board = create_board()
print_board(board)
draw_board(screen, board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

client_socket = connect_to_server('127.0.0.1', 12345)

turn = 0
game_over = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            send_data(client_socket, "quit")
            client_socket.close()
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            col = int(math.floor(posx / SQUARESIZE))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, turn + 1)

                draw_board(screen, board)
                pygame.display.update()

                if winning_move(board, turn + 1):
                    label = myfont.render(f"Player {turn + 1} wins!!", 1, RED if turn == 0 else YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                send_data(client_socket, board)
                turn += 1
                turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
