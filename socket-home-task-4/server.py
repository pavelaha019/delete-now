import socket
import threading

def handle_client(client_socket, port):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(f"{port} says: {message}")
                client_socket.send("Server received".encode())
        except:
            break
    client_socket.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(1)
    while True:
        client, addr = server.accept()
        print(f"Connected {port}")
        threading.Thread(target=handle_client, args=(client, port)).start()

if __name__ == "__main__":
    print("Server started")
    threading.Thread(target=start_server, args=(5004,)).start()
    threading.Thread(target=start_server, args=(5005,)).start()