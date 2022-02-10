import socket
import traceback

import select

port = 55000
socket_list = []
users = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port))
server_socket.listen(5)
socket_list.append(server_socket)

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

                # sign in
                if data.startswith(bytes("#", "utf-8")):
                    name = data[1:].decode().lower()
                    users[name] = connect
                    print("User " + data[1:].decode() + " added.")
                    connect.send(("Your user detail saved as : " + name).encode())

                # send msg to user
                elif data.startswith(bytes("@", "utf-8")):
                    index = str(data).index(':')
                    msg = data[index - 1:]
                    if data.startswith(bytes("@all", "utf-8")):
                        for user in users.values():
                            user.send(msg)
                    else:
                        name = data[1:index - 2].decode().lower()
                        user = users[name]
                        user.send(msg)

                # get users
                if data.startswith(bytes("get_users", "utf-8")):
                    st = ""
                    for user in users:
                        if st == "":
                            st = st + str(user)
                        else:
                            st = st + ", " + str(user)
                    sock.send(bytes(st, "utf-8"))

                # client exit / remove
                if data.startswith(bytes("exit", "utf-8")):
                    sp = str(data).split(',')
                    socket_list.remove(sock)
                    name = (sp[1])[:-1]
                    users.pop(name)
                    msg = "User "+ name +" disconnected."
                    print(msg)
                    for sock in socket_list:
                        if sock != server_socket:
                            sock.send(msg.encode())

            except ValueError and KeyError as e:
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
#                     msg = "User "+ name +" disconnected."
#                     print(msg)
#                     for sock_ in socket_list:
#                         if sock_ != server_socket:
#                             sock_.send(msg.encode())
#
#             except ValueError and KeyError as e:
#                 traceback.print_exc(e)
#                 continue
#
# server_socket.close()