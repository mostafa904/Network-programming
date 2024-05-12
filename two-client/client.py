import socket
import threading

def receive_messages(sock):
    while True:
        try:
            size_bytes = sock.recv(8)
            size = int.from_bytes(size_bytes, 'big')
            data = sock.recv(size).decode('utf-8')
            print(data)
        except socket.error:
            break

def send_message(sock):
    while True:
        message = input()
        recipient = input("Enter recipient address (host:port): ")
        data = f"{recipient}:{message}"
        sock.send(len(data).to_bytes(8,'big'))
        sock.send(data.encode('utf-8'))

def start_chat():
    host = 'localhost'
    port = 8000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port)) # connected to server

    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_message, args=(sock,))
    send_thread.start()

if __name__ == '__main__':
    start_chat()