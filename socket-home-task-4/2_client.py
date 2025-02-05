import socket

def start_client(port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', port))
    
    while True:
        message = input("Enter message: ")
        client.send(message.encode())
        response = client.recv(1024).decode()
        print(response)

if __name__ == "__main__":
    start_client(5005)