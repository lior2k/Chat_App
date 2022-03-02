import os
import socket
import threading
import time
import traceback
import select

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 2048


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
    try:
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
    except ValueError:
        sock.send('ValueError(incorrect syntax).\n Correct syntax for message: [@all:msg] or [@username:msg]'.encode())


def get_users():
    st = ""
    for user in users:
        if st == "":
            st = st + str(user)
        else:
            st = st + ", " + str(user)
    sock.send(bytes(st, "utf-8"))


def remove_user():
    exit_data = data.decode().split(SEPARATOR)
    socket_list.remove(sock)
    client_name = exit_data[1]
    users.pop(client_name)
    msg = "User " + client_name + " disconnected."
    print(msg)
    for sock_ in socket_list:
        if sock_ != server_socket:
            sock_.send(msg.encode())


def request_file():
    request_data = data.decode().split(SEPARATOR)

    # prevent miss use of space
    if (request_data[1])[0] == ord(' '):
        request_data[1] = (request_data[1])[1:]
    filename = request_data[1]
    user_name = request_data[2]

    try:
        open(filename, 'r')
    except FileNotFoundError:
        traceback.print_exception(FileNotFoundError)
        sock.send('FileNotFoundError, please make sure to enter the exact name and try again.')
        return
    files[user_name] = filename
    sock.send(('file - ' + filename + ' request received, to download use !download').encode())


def get_available_port() -> (int, int):
    available_port = 0
    for port_, bool_ in ports.items():
        if bool_ is False:
            available_port = port_
            ports[port_] = True
            break
    return available_port, port_


def get_file_related_data(user_name):
    server_file_name = files[user_name]
    dot_index = 0
    while ord(server_file_name[dot_index]) != ord('.'):
        dot_index -= 1
    file_type = server_file_name[dot_index + 1:]
    abs_path = os.path.abspath(server_file_name)
    file_size = os.path.getsize(server_file_name)
    return file_type, file_size, abs_path


def load_file_into_dict(abs_path) -> {str: bytes}:
    packets = {}
    file = open(abs_path, 'rb')
    seq_num_int = 1
    while True:
        bytes_read = file.read(BUFFER_SIZE - 2)
        if not bytes_read:
            break
        if seq_num_int <= 9:
            seq_num = '0' + str(seq_num_int)
        else:
            seq_num = str(seq_num_int)
        bytes_to_send = seq_num.encode() + bytes_read
        packets[seq_num] = bytes_to_send
        seq_num_int += 1
    file.close()
    return packets


def send_file():
    download_msg = data.decode().split(SEPARATOR)
    save_as_name = download_msg[1]
    user_name = download_msg[2]
    if not files.keys().__contains__(user_name):
        sock.send('error: no file was requested'.encode())
    else:
        file_type, file_size, abs_path = get_file_related_data(user_name)
        available_port, port_ = get_available_port()
        if available_port == 0:
            sock.send('all ports used, try again later'.encode())
            return
        client_addr = sock.getsockname()[0]
        time.sleep(1)
        packets = load_file_into_dict(abs_path)
        sock.send(f'&download{SEPARATOR}{file_type}{SEPARATOR}{save_as_name}{SEPARATOR}{file_size}{SEPARATOR}{available_port}{SEPARATOR}{len(packets)}'.encode())
        while True:
            acknowledge_msg = sock.recv(1024).decode()
            time.sleep(0.25)
            if acknowledge_msg == '!check':
                print('received check')
                break
            else:
                try:
                    missing_packets = acknowledge_msg.split(',')
                    udp_server_socket.sendto(packets[missing_packets[0]], (client_addr, available_port))
                    print(f'sent pnum {missing_packets[0]} of len {len(packets[missing_packets[0]])}')
                except ValueError and OSError:
                    traceback.print_exc()

        # port_ will always be recognized even tho there's a warning
        ports[port_] = False

        # remove client's file request
        files.pop(user_name)


# port = int(input('enter server port'))
port = 55000
socket_list = []
users = {}
files = {}
ports = {55011: False, 55002: False, 55003: False, 55004: False, 55005: False, 55006: False, 55007: False, 55008: False, 55009: False, 55010: False}
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
                # sign in #clientname
                if data.startswith(bytes("#", "utf-8")):
                    sign_in()
                # send msg to user @name:msg
                elif data.startswith(bytes("@", "utf-8")):
                    send_msg()
                # !users
                if data.startswith(bytes("!users", "utf-8")):
                    get_users()
                # !exit 'client name'
                if data.startswith(bytes("!exit", "utf-8")):
                    remove_user()
                # !files
                if data.startswith(bytes("!files", "utf-8")):
                    pass
                # !request 'file name'
                if data.startswith(bytes("!request", "utf-8")):
                    request_file()

                # file download over UDP (proceed button)
                if data.startswith(bytes("!download", "utf-8")):
                    t1 = threading.Thread(target=send_file())
                    t1.start()

            except ValueError and KeyError and FileNotFoundError as e:
                traceback.print_exc()
                continue

server_socket.close()