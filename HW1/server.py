# import socket programming library
import socket
import sys
import argparse
import json
import hashlib

def main():
    # parse commandline arguments
    # initialize the parser
    parser = argparse.ArgumentParser(description='Process arguments.')
    
    # add arguments
    parser.add_argument('-id', type=int, help='id for the server')
    parser.add_argument('-pp', type=str, help='privacy policy id number for the server')
    parser.add_argument('-listen', type=int, help='port on which the server listens for messages')
    parser.add_argument('-revproc', type=int, help='reverse proxy port')
    
    # parse
    args = parser.parse_args()
    
    
    host = '' #symbolic name meaning all available interfaces
    port = args.listen #arbitrary non-privileged port
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    print('Socket is binded to port ', port)
    
    #enable a server to accept connection, putting the socket into listening mode
    #it specifies the number of unaccpeted connections that the system will allow before 
    # refusing new connections
    s.listen(1)
    print("socket is listening")
    
    while True:
        #establish connection with client
        conn, addr = s.accept()
        
        print('Connected by ', addr)
        
        while True:
            receive = conn.recv(1024)
            # receive = receive.decode("utf-8")
            receive = json.loads(receive) #convert string to json object
            
            if not receive:
                break
            
            # compute SHA1 hash of message
            hash_object = hashlib.sha1(receive['payload'].encode())
            hex_dig = hash_object.hexdigest()
            print(hex_dig)
            
            ack = {
                "type": 2,
                "srcid": 999,
                "destid": receive["srcid"],
                "payloadsize": 999,
                "payload": hex_dig
            }
            
            #convert dictionary into string 
            ack = json.dumps(ack)
            conn.sendall(bytes(ack, encoding="utf-8"))
            
    s.close()
    
    
    
if __name__ == '__main__':
    main()
    