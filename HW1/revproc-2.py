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
import multiprocessing
import select
import time
import random
from itertools import cycle

BUFF_SIZE = 1024

def round_robin(iter):
    # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
    return next(iter)

class ReverseProxy(object):
    def __init__(self, port):
        super().__init__()
        self.flow_tabl = dict()
        self.sockets = list()
        
        self.algorithm = 'round-robin'
        self.switch_table = {}
        self.host = ''
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
            
        self.socket.listen(10) #max connections
        print("Reverse proxy is listening on port {0}".format(self.port))
        
        self.sockets.append(self.socket)

    def run(self):
        while True:
            read_list, write_list, exception_list = select.select(self.sockets, [], [])
            for sock in read_list:
                
                #new connection
                if sock == self.socket:
                    self.on_accept()
                    break
                # incoming message from a client socket
                else:
                    try:
                        # In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(4096) # buffer size: 2^n
                        if data:
                            self.on_recv(sock, data)
                        else:
                            self.on_close(sock)
                            break
                    except:
                        sock.on_close(sock)
                        break
                    
    def on_accept(self):
        client_socket, client_addr = self.socket.accept()
        print("Connected to {0}:{1}".format(client_addr[0],client_addr[1]))

        data = client_socket.recv(BUFF_SIZE)
        data = json.loads(data)
        policy_id = data['privPolyId'] if 'privPolyId' in data else data['privPoliId']
        if data['type'] == 1:
            self.switch_table[policy_id] = [data]
        
        else:
            # select a server that forwards packets to
            server_ip, server_port = self.select_server(self.switch_table[policy_id], self.algorithm)

            # init a server-side socket
            ss_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                ss_socket.connect((server_ip, server_port))
                print("Connected to server side socket {0}:{1}".format(server_ip, server_port))
                # print 'server connected: %s <==> %s' % (ss_socket.getsockname(),(socket.gethostbyname(server_ip), server_port))
            except:
                print("Can't establish connection with remote server, err: {0}".format(sys.exc_info()[0]))
                # print "Closing connection with client socket %s" % (client_addr,)
                client_socket.close()
                return

            self.sockets.append(client_socket)
            self.sockets.append(ss_socket)

            self.flow_table[client_socket] = ss_socket
            self.flow_table[ss_socket] = client_socket

    def on_recv(self, sock, data):
        # print 'recving packets: %-20s ==> %-20s, data: %s' % (sock.getpeername(), sock.getsockname(), [data])
        print("Receiving packets {0}".format(data))
        # data can be modified before forwarding to server
        # lots of add-on features can be added here
        remote_socket = self.flow_table[sock]
        remote_socket.send(data)
        print("Sending packet {0}".format(data))
        # print 'sending packets: %-20s ==> %-20s, data: %s' % (remote_socket.getsockname(), remote_socket.getpeername(), [data])

    def on_close(self, sock):
        # print 'client %s has disconnected' % (sock.getpeername(),)
        # print '='*41+'flow end'+'='*40

        ss_socket = self.flow_table[sock]

        self.sockets.remove(sock)
        self.sockets.remove(ss_socket)

        sock.close()  # close connection with client
        ss_socket.close()  # close connection with server

        del self.flow_table[sock]
        del self.flow_table[ss_socket]
    
    def select_server(self, server_list, algorithm):
        print(server_list)
        if algorithm == 'random':
            return random.choice(server_list)
        elif algorithm == 'round-robin':
            return round_robin(cycle(self.switch_table))
        else:
            raise Exception('unknown algorithm: %s' % algorithm)

    def listen(self):
        
        while True:
            conn, addr = self.socket.accept()
            
            print("Connected to {0}:{1}".format(addr[0], addr[1]))
            
            setupThread = threading.Thread(target=self.handle_server_setup(conn))
            # setupThread.start()
            
            clientThread = threading.Thread(target=self.handle_client_connection(conn))
            # clientThread.start()
            #reverse proxy forks a thread and pass the connection
            # socket to this thread
            # self.handle_client_connection(client_conn, client_addr)
            # start_new_thread(self.multi_thread, (conn,))  
            # start_new_thread(self.handle_connection,(conn,))
            
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
    def handle_server_setup(self, conn):
        message = conn.recv(BUFF_SIZE)
        message = json.loads(message) #convert string to json object
        
        if message['type'] == 1:
            print("Handling server setup...")
            print('Received setup message from server id {0}, privacy policy {1}, port {2}'\
                .format(message['id'], message['privPolyId'], message['listenport']))
            
            server_id = message['id']
            policy_id = message['privPolyId']
            server_port = message['listenport']
            server = [server_id,server_port, True]
            
            server = {
                'policy': message['privPolyId'],
                'port': message['listenport'],
                'id': message['id'],
                'active': True
            }
            
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
            conn.close()


    def handle_client_connection(self, conn):
        
        message = conn.recv(BUFF_SIZE)
        message = json.loads(message) #convert string to json object
        
        if message['type'] == 0:
            print("Handling client connection ... ")
            print("Received a data message from client id {0}, privacy policy {1}, payload: {2}"\
                .format(message['srcid'], message['privPoliId'], message['payload']))
            
            # Look up requested privacy policy in switch table
            policy_id = message['privPoliId']
            if policy_id in self.switch_table:
                servers = self.switch_table[policy_id]
    
                for idx, serverInfo in enumerate(servers):
                    if serverInfo['active'] == False:
                        send = False
                        continue
                        # if idx == len(servers) - 1:
                        #     r = Timer(2.0, self.forward_message, (message, servers,conn,policy_id))
                        #     r.start()
                        # else: 
                        #     print("Server is busy. Please wait.")
                        #     continue
                    
                    else:
                        print("Policy exists. Connect to the server and send message")
                        
                        serverPort = serverInfo['port']
                        print("Connect to server", serverInfo)
                        
                        serverInfo['active'] = False
                        self.switch_table[policy_id][idx] = serverInfo
                        print(self.switch_table)
                        print("Forwarding a data message from client id {0} to server id {1}, payload: {2}"\
                                    .format(message['srcid'], serverInfo['id'], message['payload']))
                        
                        
                        server = serverSocket(conn, self.host, self.host, serverInfo['port'])
                        # self.activeServers.append(server)
                        server.start()
                        
                        # #Create a socket connection to this server, get response and update the switch table.
                        # serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        
                        # check_socket_open = serverSocket.connect_ex((self.host, serverPort))
                        # # try:
                        # #     serverSocket.connect((self.host,serverPort))
                        # # except socket.error as e:
                        # #     print(str(e))
                
                        # if check_socket_open == 0:
                        #     print("Port is open")
                        # else:
                        #     print("Port is not open. Create new connection to server.")
                        #     # try:
                        #     serverSocket.connect((self.host,serverPort))
                        #     # except socket.error as e:
                        #     #     print(str(e))
                                
                        # while True:
                            
                        #     message = json.dumps(message)
                                
                        #     serverSocket.sendall(bytes(message,encoding="utf-8"))
                        #     # message received from server
                        #     response = serverSocket.recv(1024)
                        #     response = json.loads(response)
                            
                        #     if response:
                        #         print("Received a data message from server id {0}, payload: {1}"\
                        #             .format(response['srcid'], response['payload']))
                            
                        #         print("Forwarding a data message to client {0}, payload: {1}"\
                        #             .format(response['destid'], response['payload']))
                        #         response= json.dumps(response)
                        #         conn.sendall(bytes(response, encoding="utf-8"))

                                
                        #         server[2]=True
                        #         self.switch_table[policy_id][idx] = server
                        #         print(self.switch_table)
                            
                            
                        # serverSocket.close()
                        # self.switch_table[policy_id].remove(server)
                        # print(server)
                        break
            else:
                print("Policy does not exist.")
                response = {'Error': 'No server currently serving this privacy policy'}
                response= json.dumps(response)
                conn.sendall(bytes(response, encoding="utf-8"))
        

    def handle_connection(self,conn):
        server = serverSocket(conn, self.host, self.host, 12347)
        # self.activeServers.append(server)
        server.start()

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
                            .format(message['srcid'], server['id'], message['payload']))
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

# Class to handles the server-side of processing a request
class serverSocket(multiprocessing.Process):
    def __init__(self, clientSocket, clientAddr, serverAddr, serverPort):
        multiprocessing.Process.__init__(self)
        
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        
        self.serverAddr = serverAddr
        self.serverPort = serverPort
        
        self.serverSocker = None
        
        self.failedToConnect = multiprocessing.Value('i',0)
        
        print("In server socket ...")
        self.run()
        
        
    # Close reverse proxy socket and exit
    def closeConnection(self):
        try:
            self.serverSocket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.serverSocket.close()
        except:
            pass
        try:
            self.clientSocket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.clientSocket.close()
        except:
            pass
        # signal.signal(signal.SIGTERM, signal.SIG_DFL)
        
        sys.exit(0)
        
    def run(self):
        serverSocket = self.serverSocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket = self.clientSocket
        
        try:
            serverSocket.connect((self.serverAddr,self.serverPort))
        except:
            print("Cannot connect to server {0}:{1}".format(self.serverAddr, self.serverPort))
            self.failedToConnect.value = 1
            time.sleep(5)
            return
        
        # signal.signal(signal.SIGTERM, self.closeConnection)
        
        try:
            dataToClient = b''
            dataFromClient = b''
            
            while True:
                waitingToWrite = []
                
                if dataToClient:
                    waitingToWrite.append(clientSocket)
                if dataFromClient:
                    waitingToWrite.append(serverSocket)
                    
                try:
                    (hasDataForRead, readyForWrite, hasError) = select.select([clientSocket,serverSocket], waitingToWrite, [clientSocket,serverSocket], .3)
                except KeyboardInterrupt:
                    break
                
                print(readyForWrite)
                if hasError:
                    break
                
                if clientSocket in hasDataForRead:
                    nextData = clientSocket.recv(BUFF_SIZE)
                    
                    if not nextData:
                        break
                    
                    dataFromClient += nextData
                    
                if serverSocket in hasDataForRead:
                    nextData = serverSocket.recv(BUFF_SIZE)
                    if not nextData:
                        break
                    dataFromClient += nextData
                
                if serverSocket in readyForWrite:
                    while dataFromClient:
                        serverSocket.send(dataFromClient[:BUFF_SIZE])
                        dataFromClient = dataFromClient[BUFF_SIZE:]

                if clientSocket in readyForWrite:
                    while dataToClient:
                        clientSocket.send(dataToClient[:BUFF_SIZE])
                        dataToClient = dataToClient[BUFF_SIZE:]
                
                print(dataFromClient)
                print(dataToClient)
        except Exception as e:
            print("Error on {0}:{1}".format(self.serverAddr, self.serverPort))
        
        self.closeConnection()
        
if __name__ == '__main__':
    # parse commandline arguments
    # initialize the parser
    parser = argparse.ArgumentParser(description='Process arguments.')

    # add arguments
    parser.add_argument('-port', type=int, help='port number of reverse proxy')

    # parse
    args = parser.parse_args()

    proxy = ReverseProxy(args.port)
    proxy.run()