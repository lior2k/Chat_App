import socket
import sys
import threading
import time

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 2048
server_address = input("Enter Server IP - Should be something like '10.0.0.8' - ")
# server_address = '127.0.0.1'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 55000
client_socket.connect((server_address, port))
flag = 0
isConnected_msg = client_socket.recv(1024)
print(isConnected_msg.decode())

# sign in to server (name overlap validation)
while True:
    send_msg = input("Enter your user name:")
    myname = send_msg
    send_msg = '#' + send_msg
    client_socket.send(bytes(send_msg, "utf-8"))
    server_approval = client_socket.recv(1024)
    if not server_approval.startswith(myname.encode()):
        break
    else:
        print(server_approval.decode())


# check if all packets arrived, return a list of keys of packets that didn't.
def checksum(packets: {}) -> []:
    missing_packets = []
    for key in packets.keys():
        if packets[key] is False or None:
            missing_packets.append(key)
    return missing_packets


def recv_msg():
    global flag
    while True:
        if flag == 1:
            break
        socket_input = client_socket.recv(1024)
        if socket_input.startswith(bytes('&download', "utf-8")):
            _, suffix, save_as, file_size, available_port, number_of_packets = socket_input.decode().split(SEPARATOR)
            available_port = int(available_port)
            t3 = threading.Thread(target=download_file(suffix, save_as, file_size, available_port, number_of_packets))
            t3.start()
        elif len(socket_input) > 0:
            print(socket_input.decode())


def send_msg():
    print('Thanks for signing in - you can chat now')
    global flag
    while True:
        client_input = input()

        if client_input == '!exit':
            out_msg = (client_input + SEPARATOR + myname).encode()
            client_socket.send(out_msg)
            flag = 1
            break

        elif client_input.startswith('!download'):
            # if else to prevent miss use of space
            if ord(client_input[9]) == ord(' '):
                client_input = client_input[:9] + SEPARATOR + client_input[10:]
            else:
                client_input = client_input[:9] + SEPARATOR + client_input[9:]
            out_msg = (client_input + SEPARATOR + myname).encode()

        elif client_input.startswith('!request'):
            # if else to prevent miss use of space
            if ord(client_input[8]) == ord(' '):
                client_input = client_input[:8] + SEPARATOR + client_input[9:]
            else:
                client_input = client_input[:8] + SEPARATOR + client_input[8:]
            out_msg = (client_input + SEPARATOR + myname).encode()

        else:
            out_msg = client_input.encode()

        client_socket.send(out_msg)


def init_packets_dict(number_of_packets: int) -> {}:
    packets = {}
    for i in range(1, number_of_packets + 1):
        if i <= 9:
            index = '0' + str(i)
        else:
            index = str(i)
        packets[index] = False
    return packets


def unsplit(missing_packets: [str]) -> str:
    st = ''
    for i in missing_packets:
        if st == '':
            st = i
        else:
            st = st + ',' + i
    return st


def write_to_file(packets, save_as_name, suffix):
    file = open((save_as_name + '.' + suffix), 'wb')
    for packet in packets.values():
        file.write(packet)
    file.close()


# every packet starts with a sequence number such as '01', '02', ... '10', '11', ...
# since the demand for server files is limited to not such large files, we figured 99
# packets would be sufficient. note that there probably will be a problem for files
# larger then 2*99 = 198kb which would require more then 99 packets since our buffer size
# is 2048 (minus the 2 bytes we save for each sequence number)
def download_file(suffix, save_as_name, file_size, available_port, number_of_packets):
    file_size = int(file_size)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', available_port))
    packets = init_packets_dict(int(number_of_packets))
    received = 0
    while True:
        missing_packets = checksum(packets)
        if len(missing_packets) == 0:
            client_socket.send('!check'.encode())
            print('download finished!')
            break
        time.sleep(0.25)
        st = unsplit(missing_packets)
        client_socket.send(st.encode())
        bytes_read = udp_socket.recv(BUFFER_SIZE)
        data = bytes_read[2:]
        seq_num_str = bytes_read[:2].decode()
        packets[seq_num_str] = data
        received += len(data)
        print(f'recevied {received} / {file_size} bytes')

    # received all packets, write and close file
    write_to_file(packets, save_as_name, suffix)
    udp_socket.close()


t1 = threading.Thread(target=recv_msg)
t2 = threading.Thread(target=send_msg)
t1.start()
t2.start()

print('---Client Manual---')
print("To send a message use the syntax '@username:msg' or '@all:msg'")
print('!users - get a list of current online users')
print('!files - get a list of server files')
print("!request 'file name' - make sure to enter full name including suffix. Example '!request dog.jpg'")
print("!download 'save as name' - to download, make sure you request the file. Example '!download dog_copy")
print('---Client Manual---')

t1.join()
t2.join()

client_socket.close()
sys.exit(0)
