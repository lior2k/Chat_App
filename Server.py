import os
import socket
import threading
import time
import traceback
import select

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def sign_in():
    client_name = data[1:].decode()
    if users.keys().__contains__(client_name):
        connect.send(("" + client_name + " already taken, please try with a different name").encode())
    else:
        users[client_name] = connect
        print("User " + client_name + " added.")
        msg = "User " + client_name + " connected."
        for sock_ in socket_list:
            if sock_ != server_socket:
                sock_.send(msg.encode())


def send_msg():
    index = str(data).index(':')
    msg = data[index - 1:]
    msg = ((name + ': ').encode()) + msg
    if data.startswith(bytes("@all", "utf-8")):
        for user in users.values():
            user.send(msg)
    else:
        target = data[1:index - 2].decode()
        user = users[target]
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
    client_name = (sp[1])[:-1]
    users.pop(client_name)
    msg = "User " + client_name + " disconnected."
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
    sock.send(('file - ' + filename + ' request received, to download enter "&& save as name" eg && dog').encode())


def send_file():
    data_str = data.decode()
    data_sp = data_str.split(SEPARATOR)
    save_as_name = data_sp[1]
    user_name = data_sp[2]
    if not files.keys().__contains__(user_name):
        sock.send('error: no file was requested'.encode())
    else:
        server_file_name = files[user_name]
        dot_index = 0
        while ord(server_file_name[dot_index]) != ord('.'):
            dot_index -= 1
        file_type = server_file_name[dot_index + 1:]
        abs_path = os.path.abspath(server_file_name)
        file_size = os.path.getsize(server_file_name)
        available_port = 0
        for port_, bool_ in ports.items():
            if bool_ is False:
                available_port = port_
                ports[port_] = True
                break
        if available_port == 0:
            sock.send('all ports used, try again later'.encode())
            return
        sock.send(f'&download{SEPARATOR}{file_type}{SEPARATOR}{save_as_name}{SEPARATOR}{file_size}{SEPARATOR}{available_port}'.encode())
        client_addr = sock.getsockname()[0]
        time.sleep(1)
        sent = 0
        file = open(abs_path, 'rb')
        while True:
            bytes_read = file.read(BUFFER_SIZE)
            udp_server_socket.sendto(bytes_read, (client_addr, available_port))
            sent = sent + len(bytes_read)
            sock.send(f'sent: {sent} / {file_size}'.encode())
            print(f'sent: {sent} / {file_size} bytes to {user_name}')
            if not bytes_read:
                break
        # port_ will always be recognized even tho there's a warning
        ports[port_] = False
        file.close()
        files.pop(user_name)


# port = int(input('enter server port'))
port = 55000
socket_list = []
users = {}
files = {}
ports = {55001: False, 55002: False, 55003: False, 55004: False, 55005: False}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port))
server_socket.listen(5)
socket_list.append(server_socket)
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp_server_socket.bind(('', port))

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
                name = ''
                for user in users.keys():
                    if users[user] == sock:
                        name = user
                        break
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
                if data.startswith(bytes("&&", "utf-8")):
                    t1 = threading.Thread(target=send_file())
                    t1.start()

            except ValueError and KeyError and FileNotFoundError as e:
                traceback.print_exc()
                continue

server_socket.close()
