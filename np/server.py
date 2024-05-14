import socket
import numpy as np
import threading

HOST = '127.0.0.1'  # Server's IP address
PORT = 12345        # Port to listen on

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server is listening on {HOST}:{PORT}")

ROW_COUNT = 6
COLUMN_COUNT = 7
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

clients = []
board = create_board()  # Your existing Connect 4 board creation function

def handle_client(client_socket, player):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data == "quit":
                break
            # Process player moves and update the board state
            # Example: Assuming data is a column number chosen by the player
            column = int(data)
            if is_valid_location(board, column):
                row = get_next_open_row(board, column)
                drop_piece(board, row, column, player)
                # Send updated board state to all clients
                send_board_state()
        except Exception as e:
            print(e)
            break

    client_socket.close()
    clients.remove(client_socket)

def send_board_state():
    for client in clients:
        client.sendall(str(board).encode())

while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    clients.append(client_socket)

    # Assign players (0 and 1)
    player = len(clients) - 1

    # Start a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, player))
    client_thread.start()
