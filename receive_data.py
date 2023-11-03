import socket

received_data = ""

def tcp_interact(host, port):
    global received_data
    # 创建一个TCP客户端套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("服务器正在运行，等待客户端连接...")
    client_socket, addr = server_socket.accept()
    print("已连接到客户端:", addr)
    try:
        while True:
            # 接收数据
            data = client_socket.recv(1024).decode()
            if data != 'HeartBeat1':
                received_data = data
    finally:
        client_socket.close()

def get_data():
    global received_data
    print(received_data)
    while True:
        if received_data:
            data = received_data
            received_data = ""
            return data
            print(data)