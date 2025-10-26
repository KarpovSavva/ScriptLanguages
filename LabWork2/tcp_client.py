import socket

def tcp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    HOST = '127.0.0.1'
    PORT = 65432
    client_socket.connect((HOST, PORT))
    print(f"[TCP Client] Подключено к серверу {HOST}:{PORT}")

    message = input("Введите сообщение: ")
    client_socket.sendall(message.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"[TCP Client] Ответ от сервера: {data.decode('utf-8')}")

    client_socket.close()
    print("[TCP Client] Соединение закрыто.")

if __name__ == "__main__":
    tcp_client()
