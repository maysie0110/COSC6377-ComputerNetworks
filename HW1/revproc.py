# Reverse proxy with load balancer

import socket

#import thread module
from _thread import *
import threading

import sys
import argparse

#create a lock objected
print_lock = threading.Lock()

#thread function for multi-threading
def threaded(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print('Bye')
            
            #lock released on exit
            print_lock.release()
            break
        
        # reverse the given string from client
        data = data[::-1]
  
        # send back reversed string to client
        conn.send(data)
  
    # connection closed
    conn.close()

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
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    print('Socket is binded to port ', port)
    
    #enable a server to accept connection, putting the socket into listening mode
    #it specifies the number of unaccpeted connections that the system will allow before 
    # refusing new connections
    s.listen(5)
    print("socket is listening")
    
    while True:
        #establish connection with client
        conn, addr = s.accept()
        
        # lock acquired by client
        print('Connected by: ', addr[0], ':', addr[1])
        
        #start a new thread and return its identifier
        start_new_thread(threaded, conn)
    s.close()
    
if __name__ == '__main__':
    main()