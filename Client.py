import socket
import sys
import threading
import time

client_socket = socket.socket()
port = 55000
client_socket.connect(('127.0.0.1', port))

# receive connection message from server
recv_msg = client_socket.recv(1024)
print(recv_msg.decode())

# send user details to server
send_msg = input("Enter your user name(prefix with #):")
myname = send_msg[1:]
client_socket.send(bytes(send_msg, "utf-8"))

flag = 0


def recv_msg():
    global flag
    while True:
        if flag == 1:
            break
        recv_msg = client_socket.recv(1024)
        if len(recv_msg) > 0:
            print(recv_msg.decode())
        time.sleep(2)


def send_msg():
    global flag
    while True:
        send_msg = input("Send your message in format @user:message or @all:message ")
        if send_msg == 'exit':
            exit_msg = send_msg+","+myname
            client_socket.send(exit_msg.encode())
            flag = 1
            break
        else:
            # client_socket.send(bytes(send_msg, "utf-8"))
            client_socket.send(send_msg.encode())
        time.sleep(2)


t1 = threading.Thread(target=recv_msg)
t2 = threading.Thread(target=send_msg)
t1.start()
t2.start()
t2.join()
t1.join()
client_socket.close()
sys.exit(0)


# import socket
# import sys
# import threading
# import time
#
# client_socket = socket.socket()
# port = 55000
# client_socket.connect(('127.0.0.1', port))
#
# # receive connection message from server
# recv_msg = client_socket.recv(1024)
# print(recv_msg.decode())
#
# # send user details to server
# while True:
#     send_msg = input("Enter your user name(prefix with #):")
#     myname = send_msg[1:]
#     client_socket.send(bytes(send_msg, "utf-8"))
#     time.sleep(2)
#     server_approval = client_socket.recv(1024)
#     if not server_approval.startswith(myname.encode()):
#         break
#     else:
#         print(server_approval.decode())
#         send_msg = input("Enter your user name(prefix with #):")
#         myname = send_msg[1:]
#         client_socket.send(bytes(send_msg, "utf-8"))
#
# flag = 0
#
#
# def recv_msg():
#     global flag
#     while True:
#         if flag == 1:
#             break
#         recv_msg = client_socket.recv(1024)
#         if len(recv_msg) > 0:
#             print(recv_msg.decode())
#         time.sleep(2)
#
#
# def send_msg():
#     global flag
#     while True:
#         send_msg = input("Send your message in format @user:message or @all:message ")
#         if send_msg == 'exit':
#             exit_msg = send_msg+","+myname
#             client_socket.send(exit_msg.encode())
#             flag = 1
#             break
#         else:
#             # client_socket.send(bytes(send_msg, "utf-8"))
#             client_socket.send(send_msg.encode())
#         time.sleep(2)
#
#
# t1 = threading.Thread(target=recv_msg)
# t2 = threading.Thread(target=send_msg)
# t1.start()
# t2.start()
# t2.join()
# t1.join()
# client_socket.close()
# sys.exit(0)