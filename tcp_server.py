import socket

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    HOST = '127.0.0.1'  
    PORT = 65432        
    server_socket.bind((HOST, PORT))
    
    server_socket.listen(1)
    print(f"[TCP Server] Ожидание подключения на {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"[TCP Server] Подключён клиент: {addr}")

        data = conn.recv(1024)  # буфер 1024 байта
        if data:
            print(f"[TCP Server] Получено: {data.decode('utf-8')}")
            conn.sendall(data)
        
        conn.close()
        print(f"[TCP Server] Соединение с {addr} закрыто.\n")

if __name__ == "__main__":
    tcp_server()
