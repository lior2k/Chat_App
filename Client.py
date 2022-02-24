import socket
import sys
import threading
import time

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 55000          # '109.65.63.141'
client_socket.connect(('127.0.0.1', port))

isConnected_msg = client_socket.recv(1024)
print(isConnected_msg.decode())

# sign in to server (name overlap validation)
while True:
    send_msg = input("Enter your user name(prefix with #):")
    myname = send_msg[1:]
    client_socket.send(bytes(send_msg, "utf-8"))
    time.sleep(2)
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
            suffix = recv_msg.decode()[9:]
            t3 = threading.Thread(target=download_file(suffix))
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
            out_msg = (send_msg + ',' + myname).encode()
        else:
            out_msg = send_msg.encode()
        client_socket.send(out_msg)
        # time.sleep(2)


def download_file(suffix: str):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', 55015))
    save_as_name = input('enter the name you want to save the file (without suffix)')
    file = open((save_as_name + '.' + suffix), 'wb')
    while True:
        bytes_read = udp_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            break
        file.write(bytes_read)
    file.close()
    udp_socket.close()


t1 = threading.Thread(target=recv_msg)
t2 = threading.Thread(target=send_msg)
t1.start()
t2.start()
t2.join()
t1.join()

client_socket.close()
sys.exit(0)
