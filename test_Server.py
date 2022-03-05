import sys
from unittest import TestCase
import socket

global server_socket
global client_socket1
global client_socket2
global client_socket3
global flag


class Test(TestCase):

    def init(self):
        global server_socket
        global client_socket1
        global client_socket2
        global client_socket3
        socket_list = []
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', 5000))
        server_socket.listen(5)
        socket_list.append(server_socket)
        # udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket1.connect(('127.0.0.1', 5000))
        connected_msg1 = client_socket1.recv(1024)

        client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket2.connect(('127.0.0.1', 5000))
        connected_msg2 = client_socket2.recv(1024)

        client_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket3.connect(('127.0.0.1', 5000))
        connected_msg3 = client_socket3.recv(1024)

    def shutdown(self):
        global server_socket
        global client_socket1
        global client_socket2
        global client_socket3
        client_socket1.close()
        client_socket2.close()
        client_socket3.close()
        server_socket.close()

    def test_sign_in(self):
        self.init()

        client_socket1.send(bytes('#lior', "utf-8"))
        expected1 = client_socket1.recv(1024).decode()  # "User " + client_name + " added."
        print('asd')
        client_socket2.send(bytes('#lior', "utf-8"))
        expected2 = client_socket2.recv(1024).decode()  # client_name + " already taken, please try with a different name"
        client_socket2.send(bytes('#notlior', "utf-8"))
        expected3 = client_socket2.recv(1024).decode()  # "User " + client_name + " added."
        self.assertEqual(expected1, 'User lior added')
        self.assertEqual(expected2, 'lior already taken, please try with a different name')
        self.assertEqual(expected3, 'User notlior added')
        self.shutdown()

    def test_send_msg(self):
        self.fail()

    def test_get_users(self):
        self.fail()

    def test_remove_user(self):
        self.fail()

    def test_get_file_list(self):
        self.fail()

    def test_request_file(self):
        self.fail()

    def test_get_available_port(self):
        self.fail()

    def test_get_file_related_data(self):
        self.fail()

    def test_load_file_into_dict(self):
        self.fail()

    def test_get_address(self):
        self.fail()

    def test_send_file(self):
        self.fail()
