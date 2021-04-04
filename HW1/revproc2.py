# Reverse proxy with load balancer

import socket

#import thread module
from _thread import *
import threading

import sys
import argparse
import json
import os
import signal

child_pd1 = -1
BUFF_SIZE = 1024

class ReverseProxy(object):
    def __init__(self, port):
        super().__init__()
        
        self.switch_table = {}
        self.host = ''
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
        print("Reverse proxy is listening on {0}".format(self.port))
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
            
            #lock released on exit
            # print_lock.release()
            # break
        

            data = json.loads(data) #convert string to json object
            
            if(data['type'] == 1):
                response = self.handle_server_setup(data)
            elif(data['type'] == 0):
                response = self.handle_client_connection(data)
            # elif(data['type'] == 2):
            #     response = self.handle_server_connection(data)
                
            # send back response
            # conn.send(response)

            response = json.dumps(response)
            conn.sendall(bytes(response, encoding="utf-8"))
  
        # connection closed
        conn.close()
        
    
    # def serve(self, s):
    #     client_conn, client_addr = s.accept()
    #     forward_sock = self.init_forwarding()
        
        # if forward_sock and client_conn:
        #     # thread for multiple connections
        #     child_pd1 = os.fork()
        #     if child_pd1 == 0:
        #         signal.signal(signal.SIGTERM, self.do_close)
        #         child_pid2 = os.fork()
        
        # self.handle_client_connection(fr=client_addr, to=forward_sock)
        
            
        
    # def handle_client_connection(self,clientsocket, client_addr):
    #     data = clientsocket.recv(BUFF_SIZE)
    #     if not data:
    #         print("No data")
            
    #     data = json.loads(data) #convert string to json object
    #     policy_id = data['privPoliId']
    #     server_address = self.init_forwarding(policy_id)
        
    #     print("Create a socket with server \n")
    #     # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        

    # When reverse proxy receives the setup message, it creates 
    # a message switch table that records the server id, its
    # privacy policy and the port number the server is listening
    def handle_server_setup(self, message):
        print("Handling server setup...")
        print('Received setup message from server id {0}, privacy policy {1}, port {2}'\
            .format(message['id'], message['privPolyId'], message['listenport']))
        
        server_id = message['id']
        policy_id = message['privPolyId']
        server_port = message['listenport']
        
        if policy_id in self.switch_table:
            print("Policy exists. Find and update policy")
            self.switch_table[policy_id].append([server_id,server_port, True])
            print(self.switch_table)
        else:
            print("Policy does not exist. Inserting new entry")
            self.switch_table[policy_id] = [[server_id,server_port, True]]
            print(self.switch_table)
            
        ack = {
            'Status': 'Success'
            }
        return ack


    def handle_client_connection(self, message):
        print("Handling client connection ... ")
        print("Received a data message from client id {0}, privacy policy {1}, payload: {2}"\
            .format(message['srcid'], message['privPoliId'], message['payload']))
        
        # Look up requested privacy policy in switch table
        policy_id = message['privPoliId']
        if policy_id in self.switch_table:
            print("Policy exists. Connect to the server and send message")
            servers = self.switch_table[policy_id]
   
            for server in servers:
                if server[2] == True:
                    serverPort = server[1]
                    print("Connect to server", server)
                    print("Forwarding a data messageto server id {0}, payload: {1}"\
                                .format(server[0], message['payload']))
                    #Create a socket connection to this server, get response and update the switch table.
                    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server[2] = False
                    try:
                        serverSocket.connect((self.host,serverPort))
                    except socket.error as e:
                        print(str(e))
            
                    while True:
                        
                        message = json.dumps(message)
                            
                        serverSocket.sendall(bytes(message,encoding="utf-8"))
                        # message received from server
                        response = serverSocket.recv(1024)
                        response = json.loads(response)
                        
                        print("Received a data message from server id {0}, payload: {1}"\
                            .format(response['srcid'], response['payload']))
                        # data = data.decode("utf-8")
                        # return response
                        
                    serverSocket.close()
                    server[2] = True
                    break
                else:
                    print("Server is busy. Please wait.")
        else:
            print("Policy does not exst.")
            response = {'Error': 'No server currently serving this privacy policy'}
        
        return response


    def handle_server_connection(self,message):
        print('Received a data message from server id {0}, payload {1}'\
            .format(message['id'], message['payload']))
        
    
    def init_forwarding(self, policy_id):
        # look up the message switch table for the servers
        # with requested privacy policy
        servers = self.switch.get(policy_id)
        
        
# parse commandline arguments
# initialize the parser
parser = argparse.ArgumentParser(description='Process arguments.')

# add arguments
parser.add_argument('-port', type=int, help='port number of reverse proxy')

# parse
args = parser.parse_args()

proxy = ReverseProxy(args.port)