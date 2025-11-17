import socket

def udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    HOST = '127.0.0.1'
    PORT = 65433

    message = input("Введите сообщение: ")
    client_socket.sendto(message.encode('utf-8'), (HOST, PORT))
    print(f"[UDP Client] Сообщение отправлено на {HOST}:{PORT}")

    data, server_addr = client_socket.recvfrom(1024)
    print(f"[UDP Client] Ответ от сервера {server_addr}: {data.decode('utf-8')}")

    client_socket.close()
    print("[UDP Client] Сокет закрыт.")

if __name__ == "__main__":
    udp_client()
