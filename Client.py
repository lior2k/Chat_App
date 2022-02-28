import socket
import sys
import threading
import time
import pygame

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 55000
client_socket.connect(('127.0.0.1', port))

print('---Client Manual---')
print('To send a message to a single user use the syntax "@username:message"')
print('To send a message to all connected users use the syntax "@all:message"')
print('To get a list of online users enter the words "get users"')
print('To get a list of server files ...')
print('To request a file enter "$filename"')
print('To download the file after requesting it enter "&& name to save"')
print('---Client Manual---')
print()

isConnected_msg = client_socket.recv(1024)
print(isConnected_msg.decode())

# sign in to server (name overlap validation)
while True:
    send_msg = input("Enter your user name:")
    myname = send_msg
    send_msg = '#' + send_msg
    client_socket.send(bytes(send_msg, "utf-8"))
    time.sleep(1)
    server_approval = client_socket.recv(1024)
    if not server_approval.startswith(myname.encode()):
        break
    else:
        print(server_approval.decode())

flag = 0


def recv_msg():
    global flag
    while True:
        if flag == 1:
            break
        recv_msg = client_socket.recv(1024)
        if recv_msg.startswith(bytes('&download', "utf-8")):
            _, suffix, save_as, file_size, available_port = recv_msg.decode().split(SEPARATOR)
            available_port = int(available_port)
            t3 = threading.Thread(target=download_file(suffix, save_as, file_size, available_port))
            t3.start()
        elif len(recv_msg) > 0:
            print(recv_msg.decode())
        # time.sleep(2)


def send_msg():
    global flag
    while True:
        send_msg = input("Send your message in format @user:message or @all:message ")
        if send_msg == 'exit':
            out_msg = ('!'+send_msg+","+myname).encode()
            client_socket.send(out_msg)
            flag = 1
            break
        elif send_msg.startswith('$'):
            out_msg = (send_msg+","+myname).encode()
        elif send_msg.startswith('get users'):
            out_msg = ('%' + send_msg).encode()
        elif send_msg.startswith('&&'):
            out_msg = ('&&' + SEPARATOR + send_msg[3:] + SEPARATOR + myname).encode()
        else:
            out_msg = send_msg.encode()
        client_socket.send(out_msg)
        # time.sleep(2)


def download_file(suffix: str, save_as_name, file_size, available_port):
    file_size = int(file_size)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', available_port))
    file = open((save_as_name + '.' + suffix), 'wb')
    received = 0
    while True:
        bytes_read = udp_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            break
        file.write(bytes_read)
        received = received + len(bytes_read)
        print(f'received: {received} / {file_size} bytes')
    file.close()
    udp_socket.close()
    return


t1 = threading.Thread(target=recv_msg)
t2 = threading.Thread(target=send_msg)
t1.start()
t2.start()
t1.join()
t2.join()

client_socket.close()
sys.exit(0)
