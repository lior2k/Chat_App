import os
import socket
import threading
import time
import traceback
import select

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 2048


# note that each client must have a unique name, therefore has an infinite loop until he choose a name that isn't taken
def sign_in():
    client_name = data[1:].decode()
    if users.keys().__contains__(client_name):
        sock.send((client_name + " already taken, please try with a different name").encode())
    else:
        users[client_name] = sock, addr[0]
        print("User " + client_name + " added.")
        msg = "User " + client_name + " connected."
        for sock_ in socket_list:
            if sock_ != server_socket:
                sock_.send(msg.encode())


# handling our [@to:msg] syntax
def send_msg():
    try:
        index = str(data).index(':')
        name = ''
        for user in users.keys():
            client_sock = (users[user])[0]
            if client_sock == sock:
                name = user
                break
        msg = data[index - 1:]
        msg = ((name + ': ').encode()) + msg
        if data.startswith(bytes("@all", "utf-8")):
            for user, sock_ in users.items():
                if name != user:
                    sock_[0].send(msg)
        else:
            target = data[1:index - 2].decode()
            target_sock = (users[target])[0]
            target_sock.send(msg)
    except (ValueError, KeyError):
        sock.send('ValueError or KeyError found'.encode())


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
    socket_list.pop(get_address(sock))
    client_name = exit_data[1]
    users.pop(client_name)
    msg = "User " + client_name + " disconnected."
    print(msg)
    for sock_ in socket_list:
        if sock_ != server_socket:
            sock_.send(msg.encode())


def request_file():
    request_data = data.decode().split(SEPARATOR)
    # the if is to prevent miss use of space during file request
    if (request_data[1])[0] == ord(' '):
        request_data[1] = (request_data[1])[1:]
    filename = request_data[1]
    user_name = request_data[2]

    try:
        open(filename, 'r')
    except FileNotFoundError:
        sock.send('FileNotFoundError found during file request')
        print(FileNotFoundError)
        return
    files[user_name] = filename
    sock.send(("file - " + filename + " request received, to download use !download 'save as name'").encode())


def get_available_port() -> int:
    available_port = 0
    for port_, bool_ in ports.items():
        if bool_ is False:
            available_port = port_
            ports[port_] = True
            break
    return available_port


# using our saved data we have from the file request
def get_file_related_data(user_name):
    server_file_name = files[user_name]
    dot_index = 0
    while ord(server_file_name[dot_index]) != ord('.'):
        dot_index -= 1
    file_type = server_file_name[dot_index + 1:]
    abs_path = os.path.abspath(server_file_name)
    file_size = os.path.getsize(server_file_name)
    return file_type, file_size, abs_path


# self explanatory by name
def load_file_into_dict(abs_path) -> {str: bytes}:
    packets = {}
    try:
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
    except FileNotFoundError:
        traceback.print_last()
    return packets


def get_address(client_socket):
    for user in users.keys():
        if (users[user])[0] == client_socket:
            return (users[user])[1]


# every packet starts with a sequence number such as '01', '02', ... '10', '11', ...
# since the demand for server files is limited to not such large files, we figured 99
# packets would be sufficient. note that there probably will be a problem for files
# larger then 2*99 = 198kb which would require more then 99 packets since our buffer size
# is 2048 (minus the 2 bytes we save for each sequence number)
def send_file(client_socket):
    # download msg - client sent the msg !download+saveasname+username
    download_msg = data.decode().split(SEPARATOR)
    save_as_name = download_msg[1]
    user_name = download_msg[2]
    # client_addr = current_socket.getsockname()[0]
    client_addr = get_address(client_socket)

    # in case file was not requested
    if not files.keys().__contains__(user_name):
        client_socket.send('error: no file was requested'.encode())
        return

    # get relevant data to perform the upload
    file_type, file_size, abs_path = get_file_related_data(user_name)
    available_port = get_available_port()

    # in case all ports are in use
    if available_port == 0:
        client_socket.send('all ports used, try again later'.encode())
        return

    packets = load_file_into_dict(abs_path)

    # send the client the relevant data to perform the download
    client_socket.send(
        f'&download{SEPARATOR}{file_type}{SEPARATOR}{save_as_name}{SEPARATOR}{file_size}{SEPARATOR}{available_port}{SEPARATOR}{len(packets)}'.encode())

    # the actual sending of the file:
    while True:
        acknowledge_msg = client_socket.recv(1024).decode()
        time.sleep(0.25)
        if acknowledge_msg == '!check':
            print('download finished!')
            break
        else:
            try:
                missing_packets = acknowledge_msg.split(',')
                udp_server_socket.sendto(packets[missing_packets[0]], (client_addr, available_port))
                print(f'sent pnum {missing_packets[0]} of len {len(packets[missing_packets[0]])}')
            except (ValueError, OSError, KeyError):
                traceback.print_last()

    # download finished, port is available again
    ports[available_port] = False

    # remove client's file request
    files.pop(user_name)


# port = int(input('enter server port'))
port = 55000
socket_list = []
users = {}
files = {}
ports = {55001: False, 55002: False, 55003: False, 55004: False, 55005: False, 55006: False, 55007: False, 55008: False,
         55009: False, 55010: False, 55011: False, 55012: False, 55013: False, 55014: False, 55015: False}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port))
server_socket.listen(5)
socket_list.append(server_socket)
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('---Server is Running---')
print(f'Server IP - {socket.gethostbyname(socket.gethostname())}')
while True:
    ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)
    for sock in ready_to_read:
        if sock == server_socket:
            connect, addr = server_socket.accept()
            socket_list.append(connect)
            connect.send(("You are connected from:" + str(addr)).encode())
        else:
            data = sock.recv(2048)
            # sign in #clientname
            if data.startswith(bytes("#", "utf-8")):
                sign_in()
            # send msg to user [@to:msg]
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
            # !download 'save as name'
            if data.startswith(bytes("!download", "utf-8")):
                t1 = threading.Thread(target=send_file(sock))
                t1.start()

server_socket.close()