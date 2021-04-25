# Reverse proxy with load balancer

import socket, errno

#import thread module
from _thread import *
import threading
from threading import Timer

import sys
import argparse
import json
import os
import signal

BUFF_SIZE = 1024

class ReverseProxy(object):
    def __init__(self, port):
        super().__init__()
        
        self.switch_table = {}
        # self.host = ''
        self.host = '3.129.9.175'
        self.port = port
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
            
        self.listen()

    def listen(self):
        self.socket.listen(10)
        print("Reverse proxy is listening on port {0}".format(self.port))
        while True:
            conn, addr = self.socket.accept()
            
            print("Connected to {0}:{1}".format(addr[0], addr[1]))
            
            #reverse proxy forks a thread and pass the connection
            # socket to this thread
            # self.handle_client_connection(client_conn, client_addr)
            start_new_thread(self.multi_thread, (conn,))  
            
            # self.serve(s)
        self.socket.close()
    
    def multi_thread(self, conn):
        while True:
            data = conn.recv(BUFF_SIZE)
            if not data:
                print('Connection disconnected.')
                break
            #lock released on exit
            # print_lock.release()
            # break
        

            data = json.loads(data) #convert string to json object
            
            if(data['type'] == 1):
                self.handle_server_setup(data,conn)
            elif(data['type'] == 0):
                self.handle_client_connection(data,conn)
            # elif(data['type'] == 2):
            #     response = self.handle_server_connection(data,conn)
                
            # send back response
            # conn.send(response)

            # response = json.dumps(response)
            # conn.sendall(bytes(response, encoding="utf-8"))

        # connection closed
        conn.close()
        
    
    # When reverse proxy receives the setup message, it creates 
    # a message switch table that records the server id, its
    # privacy policy and the port number the server is listening
    def handle_server_setup(self, message, conn):
        print("Handling server setup...")
        print('Received setup message from server id {0}, privacy policy {1}, port {2}'\
            .format(message['id'], message['privPolyId'], message['listenport']))
        
        server_id = message['id']
        policy_id = message['privPolyId']
        server_port = message['listenport']
        server = [server_id,server_port, True]
        
        if policy_id in self.switch_table:
            if server not in self.switch_table[policy_id]:
                self.switch_table[policy_id].append(server)
            print(self.switch_table)
        else:
            self.switch_table[policy_id] = [server]
            print(self.switch_table)
            
        ack = {
            'Status': 'Successfully setup with reverse proxy'
            }
        
        response = json.dumps(ack)
        conn.sendall(bytes(response, encoding="utf-8"))


    def handle_client_connection(self, message,conn):
        print("Handling client connection ... ")
        print("Received a data message from client id {0}, privacy policy {1}, payload: {2}"\
            .format(message['srcid'], message['privPoliId'], message['payload']))
        
        # Look up requested privacy policy in switch table
        policy_id = message['privPoliId']
        if policy_id in self.switch_table:
            servers = self.switch_table[policy_id]
   
            for idx, server in enumerate(servers):
                if server[2] == False:
                    send = False
                    if idx == len(servers) - 1:
                        r = Timer(2.0, self.forward_message, (message, servers,conn,policy_id))
                        r.start()
                    else: 
                        print("Server is busy. Please wait.")
                        continue
                
                else:
                    print("Policy exists. Connect to the server and send message")
                    
                    serverPort = server[1]
                    print("Connect to server", server)
                    
                    server[2] = False
                    self.switch_table[policy_id][idx] = server
                    print(self.switch_table)
                    print("Forwarding a data message from client id {0} to server id {1}, payload: {2}"\
                                .format(message['srcid'], server[0], message['payload']))
                    #Create a socket connection to this server, get response and update the switch table.
                    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    check_socket_open = serverSocket.connect_ex((self.host, serverPort))
                    # try:
                    #     serverSocket.connect((self.host,serverPort))
                    # except socket.error as e:
                    #     print(str(e))
            
                    if check_socket_open == 0:
                        print("Port is open")
                    else:
                        print("Port is not open. Create new connection to server.")
                        # try:
                        serverSocket.connect((self.host,serverPort))
                        # except socket.error as e:
                        #     print(str(e))
                            
                    while True:
                        
                        message = json.dumps(message)
                            
                        serverSocket.sendall(bytes(message,encoding="utf-8"))
                        # message received from server
                        response = serverSocket.recv(1024)
                        response = json.loads(response)
                        
                        if response:
                            print("Received a data message from server id {0}, payload: {1}"\
                                .format(response['srcid'], response['payload']))
                        
                            print("Forwarding a data message to client {0}, payload: {1}"\
                                .format(response['destid'], response['payload']))
                            response= json.dumps(response)
                            conn.sendall(bytes(response, encoding="utf-8"))

                            
                            server[2]=True
                            self.switch_table[policy_id][idx] = server
                            print(self.switch_table)
                        
                        
                    serverSocket.close()
                    self.switch_table[policy_id].remove(server)
                    # print(server)
                    break
        else:
            print("Policy does not exist.")
            response = {'Error': 'No server currently serving this privacy policy'}
            response= json.dumps(response)
            conn.sendall(bytes(response, encoding="utf-8"))
        


    def handle_server_connection(self,message, conn):
        print('Received a data message from server id {0}, payload {1}'\
            .format(message['id'], message['payload']))
        
        return message
        
    
    def forward_message(self,message, servers, conn,policy_id):
        
        print("Rescan the switch table")
        for idx, server in enumerate(servers):
            if server[2] == True:
                serverPort = server[1]
                print("Connect to server", server)
                
                server[2] = False
                self.switch_table[policy_id][idx] = server
                print(self.switch_table)
                print("Forwarding a data message from client id {0} to server id {1}, payload: {2}"\
                            .format(message['srcid'], server[0], message['payload']))
                #Create a socket connection to this server, get response and update the switch table.
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                check_socket_open = serverSocket.connect_ex((self.host, serverPort))
                # try:
                #     serverSocket.connect((self.host,serverPort))
                # except socket.error as e:
                #     print(str(e))
        
                if check_socket_open == 0:
                    print("Port is open")
                else:
                    print("Port is not open. Create new connection to server.")
                    # try:
                    serverSocket.connect((self.host,serverPort))
                    # except socket.error as e:
                    #     print(str(e))
                        
                while True:
                    
                    message = json.dumps(message)
                        
                    serverSocket.sendall(bytes(message,encoding="utf-8"))
                    # message received from server
                    response = serverSocket.recv(1024)
                    response = json.loads(response)
                    
                    if response:
                        print("Received a data message from server id {0}, payload: {1}"\
                            .format(response['srcid'], response['payload']))
                    
                        print("Forwarding a data message to client {0}, payload: {1}"\
                            .format(response['destid'], response['payload']))
                        response= json.dumps(response)
                        conn.sendall(bytes(response, encoding="utf-8"))
                        
                        server[2]=True
                        self.switch_table[policy_id][idx] = server
                        print(self.switch_table)
                    
                serverSocket.close()
                break

        
# parse commandline arguments
# initialize the parser
parser = argparse.ArgumentParser(description='Process arguments.')

# add arguments
parser.add_argument('-port', type=int, help='port number of reverse proxy')

# parse
args = parser.parse_args()

proxy = ReverseProxy(args.port)
# proxy = ReverseProxy(port=123)