import socket
import datetime

#发送数据
def send_data(host, port, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print("已连接到服务器:", (host, port))
        client_socket.sendall(data.encode())
        print("已发送数据:", data)
        return "OK"
    except Exception as e:
        print("发送数据出错:", str(e))
        return "NG"
    finally:
        client_socket.close()



