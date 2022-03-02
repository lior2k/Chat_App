import socket
import sys
import threading
import time

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 2048

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 55000
client_socket.connect(('127.0.0.1', port))

print('---Client Manual---')
print('To send a message to a single user use the syntax "@username:message"')
print('To send a message to all connected users use the syntax "@all:message"')
print()
print("For the following commands use !'insert command here'")
print('!users - get a list of current online users')
print('!files - get a list of server files')
print("!request 'file name' - make sure to enter full name including suffix. Example '!request dog.jpg'")
print("!download 'save as name' - to download, make sure you request the file. Example '!download dog_copy")
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
        recv_msg = client_socket.recv(1024)
        if recv_msg.startswith(bytes('&download', "utf-8")):
            _, suffix, save_as, file_size, available_port, number_of_packets = recv_msg.decode().split(SEPARATOR)
            available_port = int(available_port)
            t3 = threading.Thread(target=download_file(suffix, save_as, file_size, available_port, number_of_packets))
            t3.start()
        elif len(recv_msg) > 0:
            print(recv_msg.decode())
        # time.sleep(2)


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
            # if else to prevent mis use of space
            if ord(client_input[9]) == ord(' '):
                client_input = client_input[:9] + SEPARATOR + client_input[10:]
            else:
                client_input = client_input[:9] + SEPARATOR + client_input[9:]
            out_msg = (client_input + SEPARATOR + myname).encode()
        elif client_input.startswith('!request'):
            # if else to prevent mis use of space
            if ord(client_input[8]) == ord(' '):
                client_input = client_input[:8] + SEPARATOR + client_input[9:]
            else:
                client_input = client_input[:8] + SEPARATOR + client_input[8:]
            out_msg = (client_input + SEPARATOR + myname).encode()
        else:
            out_msg = client_input.encode()
        client_socket.send(out_msg)
        # time.sleep(2)


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


def download_file(suffix, save_as_name, file_size, available_port, number_of_packets):
    file_size = int(file_size)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', available_port))
    packets = init_packets_dict(int(number_of_packets))
    received = 0
    while True:
        missing_packets = checksum(packets)
        if len(missing_packets) == 0:
            client_socket.send('!check'.encode())
            print('sent check')
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
    return


t1 = threading.Thread(target=recv_msg)
t2 = threading.Thread(target=send_msg)
t1.start()
t2.start()
t1.join()
t2.join()

client_socket.close()
sys.exit(0)
