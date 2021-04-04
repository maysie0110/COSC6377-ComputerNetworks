# Reverse proxy with load balancer

import socket

#import thread module
from _thread import *
import threading

import sys
import argparse
import json

#create a lock objected
print_lock = threading.Lock()

#thread function for multi-threading
def multi_thread(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print('Bye')
            
            #lock released on exit
            # print_lock.release()
            # break
        

        data = json.loads(data) #convert string to json object
        
        if(data['type'] == 1):
            handle_server_connection(data)
        elif(data['type'] == 0):
            handle_client_connection(data)
        # # reverse the given string from client
        # data = data[::-1]
  
        # # send back reversed string to client
        # conn.send(data)
  
    # connection closed
    conn.close()

# Connection to a client
# When the reverse proxy receives message of type 0,
# it looks up in its message switching table for servers 
# serving the requested privacy policy
# Select the servers, connects to the correct port number,
# sends the message to that port
# Gets response from the server and sends it back to client
def handle_client_connection(message):
    print("Received a data message from client id {0}, privacy policy {1}, payload: {2}"\
        .format(message['srcid'], message['privPoliId'],message['payload']))

# When reverse proxy receives the setup message, it creates 
# a message switch table that records the server id, its
# privacy policy and the port number the server is listening
def handle_server_connection(message):
    print('Received setup message from server id {0}, privacy policy {1}, port {2}'\
        .format(message['id'], message['privPolyId'], message['listenport']))
    
    switch_table = []


def main():
    # parse commandline arguments
    # initialize the parser
    parser = argparse.ArgumentParser(description='Process arguments.')
    
    # add arguments
    parser.add_argument('-port', type=int, help='port number of reverse proxy')
    
    # parse
    args = parser.parse_args()
    
    
    host = '' #symbolic name meaning all available interfaces
    port = args.port # well-known port 
    
    # Create socket and bind the socket to a host and a port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    print('Running the reverse proxy on port', port)
    
    # Enable a server to accept connection
    # Reverse proxy listens for incomring connections from clients and servers
    # it specifies the number of unaccpeted connections that the system 
    # will allow before refusing new connections
    s.listen(5)
    print("Reverse proxy is listening")
    
    while True:
        # establish connection with servers
        server_conn, server_addr = s.accept()
        
        # print('Connected by: ', server_addr[0], ':', server_addr[1])
        

        # receive = server_conn.recv(1024)
        # receive = json.loads(receive) #convert string to json object
    
        # if not receive:
        #     break
        
        # handle_server_connection(receive)
        
        
        # lock acquired by client
        # print_lock.acquire()
        print('Connected by: ', server_addr[0], ':', server_addr[1])
        
        #start a new thread to handle new connection
        start_new_thread(multi_thread, (server_conn,))  
    s.close()
    
if __name__ == '__main__':
    main()