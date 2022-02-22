import os
import socket
import time
import traceback
import select


def sign_in():
    name = data[1:].decode()
    if users.keys().__contains__(name):
        connect.send(("" + name + " already taken, please try with a different name").encode())
    else:
        users[name] = connect
        print("User " + name + " added.")
        connect.send(("Your user detail saved as : " + name).encode())


def send_msg():
    index = str(data).index(':')
    msg = data[index - 1:]
    if data.startswith(bytes("@all", "utf-8")):
        for user in users.values():
            user.send(msg)
    else:
        name = data[1:index - 2].decode()
        user = users[name]
        user.send(msg)


def get_users():
    st = ""
    for user in users:
        if st == "":
            st = st + str(user)
        else:
            st = st + ", " + str(user)
    sock.send(bytes(st, "utf-8"))


def remove_user():
    sp = str(data).split(',')
    socket_list.remove(sock)
    name = (sp[1])[:-1]
    users.pop(name)
    msg = "User " + name + " disconnected."
    print(msg)
    for sock_ in socket_list:
        if sock_ != server_socket:
            sock_.send(msg.encode())


def request_file():
    data_str = data.decode()
    comma_index = 0
    while ord(data_str[comma_index]) != ord(','):
        comma_index -= 1
    filename = data_str[1:comma_index]
    user_name = data_str[comma_index + 1:]
    files[user_name] = filename
    sock.send(('file - ' + filename + ' request received, to download press "proceed"').encode())


port = 55000
socket_list = []
users = {}
files = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port))
server_socket.listen(5)
socket_list.append(server_socket)
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('---Server is Running---')
while True:
    ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)
    for sock in ready_to_read:
        if sock == server_socket:
            connect, addr = server_socket.accept()
            socket_list.append(connect)
            connect.send(("You are connected from:" + str(addr)).encode())
        else:
            try:
                data = sock.recv(2048)
                # sign in #
                if data.startswith(bytes("#", "utf-8")):
                    sign_in()
                # send msg to user @
                elif data.startswith(bytes("@", "utf-8")):
                    send_msg()
                # get users %
                if data.startswith(bytes("%get users", "utf-8")):
                    get_users()
                # client exit / remove !
                if data.startswith(bytes("!exit", "utf-8")):
                    remove_user()

                # get server file list
                if data.startswith(bytes("get files", "utf-8")):
                    pass

                # file requests $
                if data.startswith(bytes("$", "utf-8")):
                    request_file()

                # file download over UDP (proceed button)
                if data.startswith(bytes("&&,", "utf-8")):
                    data_str = data.decode()
                    user_name = data_str[3:]
                    if not files.keys().__contains__(user_name):
                        sock.send('error: no file was requested'.encode())
                        continue
                    file_name = files[user_name]
                    dot_index = 0
                    while ord(file_name[dot_index]) != ord('.'):
                        dot_index -= 1
                    file_type = file_name[dot_index+1:]
                    abs_path = os.path.abspath(file_name)
                    if file_type == 'txt':
                        sock.send('&txt'.encode())
                        time.sleep(1)
                        file = open(abs_path, 'r')
                        file_data = file.read()
                        udp_server_socket.sendto(file_data.encode(), ('127.0.0.1', 55015))
                        file.close()
                        files.pop(user_name)

            except ValueError and KeyError and FileNotFoundError as e:
                traceback.print_exc()
                continue

server_socket.close()


# import socket
# import traceback
# import select
#
# port = 55000
# socket_list = []
# users = {}
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.bind(('', port))
# server_socket.listen(5)
# socket_list.append(server_socket)
#
# while True:
#     ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)
#     for sock in ready_to_read:
#         if sock == server_socket:
#             connect, addr = server_socket.accept()
#             socket_list.append(connect)
#             connect.send(("You are connected from:" + str(addr)).encode())
#         else:
#             try:
#                 data = sock.recv(2048)
#
#                 # sign in
#                 if data.startswith(bytes("#", "utf-8")):
#                     name = data[1:].decode().lower()
#                     users[name] = connect
#                     print("User " + data[1:].decode() + " added.")
#                     connect.send(("Your user detail saved as : " + name).encode())
#
#                 # send msg to user
#                 elif data.startswith(bytes("@", "utf-8")):
#                     index = str(data).index(':')
#                     msg = data[index - 1:]
#                     if data.startswith(bytes("@all", "utf-8")):
#                         for user in users.values():
#                             user.send(msg)
#                     else:
#                         name = data[1:index - 2].decode().lower()
#                         user = users[name]
#                         user.send(msg)
#
#                 # get users
#                 if data.startswith(bytes("get_users", "utf-8")):
#                     st = ""
#                     for user in users:
#                         if st == "":
#                             st = st + str(user)
#                         else:
#                             st = st + ", " + str(user)
#                     sock.send(bytes(st, "utf-8"))
#
#                 # client exit / remove
#                 if data.startswith(bytes("exit", "utf-8")):
#                     sp = str(data).split(',')
#                     socket_list.remove(sock)
#                     name = (sp[1])[:-1]
#                     users.pop(name)
#                     msg = "User " + name + " disconnected."
#                     print(msg)
#                     for sock_ in socket_list:
#                         if sock_ != server_socket:
#                             sock_.send(msg.encode())
#
#             except ValueError and KeyError as e:
#                 traceback.print_exc()
#                 continue
#
# server_socket.close()
