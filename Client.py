import socket
import sys
import threading
import time

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


def checksum(packets: {}):
    missing_packets = []
    for i in packets.keys():
        if not (packets[i])[1]:
            missing_packets.append(i)
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


def binaryToDecimal(binary):
    binary1 = binary
    decimal, i, n = 0, 0, 0
    while (binary != 0):
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary // 10
        i += 1
    return decimal


def download_file(suffix: str, save_as_name, file_size, available_port, number_of_packets):
    file_size = int(file_size)
    number_of_packets = int(number_of_packets)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', available_port))
    file = open((save_as_name + '.' + suffix), 'wb')
    packets = {}
    for i in range(0, number_of_packets):
        packets[i] = (None, False)
    received = 0
    while True:
        missing_packets = checksum(packets)
        if len(missing_packets) == 0:
            client_socket.send('!check'.encode())
            break
        else:
            st = ''
            for i in missing_packets:
                if st == '':
                    st = str(i)
                else:
                    st = st + ',' + str(i)
            client_socket.send(st.encode())
        for i in missing_packets:
            bytes_read = udp_socket.recv(BUFFER_SIZE)
            data = bytes_read[:4000]
            seq_num = bytes_read[4000:].decode()
            seq_num = binaryToDecimal(int(seq_num))
            packets[seq_num] = (data, True)
            # received = received + len(data)
            # print(f'received: {received} / {file_size} bytes')

    for packet in packets.values():
        file.write(packet[0])
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