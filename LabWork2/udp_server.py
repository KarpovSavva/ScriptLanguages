import socket

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    HOST = '127.0.0.1'
    PORT = 65433  
    server_socket.bind((HOST, PORT))
    print(f"[UDP Server] Ожидание пакетов на {HOST}:{PORT}...")

    while True:
        data, client_addr = server_socket.recvfrom(1024)
        print(f"[UDP Server] Получено от {client_addr}: {data.decode('utf-8')}")

        server_socket.sendto(data, client_addr)
        print(f"[UDP Server] Отправлено обратно клиенту {client_addr}\n")

if __name__ == "__main__":
    udp_server()
