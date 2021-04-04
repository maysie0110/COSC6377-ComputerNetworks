# import socket programming library
import socket
import sys
import argparse
import json
import hashlib
import signal
import select

class Server(object):
    def __init__(self,args):
        super().__init__()
        # Shutdown on Ctrl+C
        # signal.signal(signal.SIGINT, self.shutdown)

        self.host = '127.0.0.1' # localhost
        self.port = args.listen #arbitrary non-privileged port
        self.revproc = args.revproc #well-known port on which the reverse proxy is running
        self.server_id = args.id
        self.policy_id = args.pp


        print('Server runing with id', self.server_id)
        print('Server serving privacy policy', self.policy_id)

        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #Bind before connect
        # self.socket.bind((self.host, self.port))
        # self.socket.connect((self.host, self.revproc))

        self.connect_to_proxy()
        self.listen()

    def connect_to_proxy(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #  # connect to reverse proxy
        self.socket.connect((self.host,self.revproc))
        print("Connecting to the reverse proxy on port", self.revproc)

        # set up message
        message = {
            "type": 1, # 1 is a connection setup message from a server
            "id": self.server_id, # id of the server
            "privPolyId": self.policy_id, # privacy policy of the server
            "listenport": self.port # port on which the server is listening
        }

        # while True:
        #convert dictionary into string
        message = json.dumps(message)

        # # sent message to reverse proxy
        self.socket.sendall(bytes(message,encoding="utf-8"))

        # message received from server
        data = self.socket.recv(1024)
        print(data)
        # data = data.decode("utf-8")

        # #close connection
        # self.socket.shutdown(socket.SHUT_RDWR)
        # self.socket.close()


    def listen(self):

        # self.socket.listen(1)
        # print("Sever is listening on {0}".format(self.port))
        # while True:
        #     conn, addr = self.socket.accept()

        #     print("Connected to {0}:{1}".format(addr[0], addr[1]))
        #     receive = conn.recv(1024)
        #     receive = json.loads(receive) #convert string to json object

        #     if not receive:
        #         break

        #     print("Received a message from client {0}, payload: {1}".format(receive['srcid'],receive['payload']))
        #     # compute SHA1 hash of message
        #     hash_object = hashlib.sha1(receive['payload'].encode())
        #     hex_dig = hash_object.hexdigest()
        #     # print(hex_dig)

        #     ack = {
        #         "type": 2,
        #         "srcid": self.server_id,
        #         "destid": receive["srcid"],
        #         "payloadsize": receive["payloadsize"],
        #         "payload": hex_dig
        #     }

        #     #convert dictionary into string
        #     ack = json.dumps(ack)
        #     conn.sendall(bytes(ack, encoding="utf-8"))
        #     print("Sending a response to client {0}, payload: {1}".format(receive['srcid'],hex_dig))

        # self.socket.close()

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.serverSocket.setsockopt(socket.)
        try:
            self.serverSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))

        self.serverSocket.listen(1)
        print("Sever is listening on {0}".format(self.port))
        while True:
            conn, addr = self.serverSocket.accept()

            print("Connected to {0}:{1}".format(addr[0], addr[1]))
            receive = conn.recv(1024)
            receive = json.loads(receive) #convert string to json object

            if not receive:
                break

            print("Received a message from client {0}, payload: {1}".format(receive['srcid'],receive['payload']))
            # compute SHA1 hash of message
            hash_object = hashlib.sha1(receive['payload'].encode())
            hex_dig = hash_object.hexdigest()
            # print(hex_dig)

            ack = {
                "type": 2,
                "srcid": self.server_id,
                "destid": receive["srcid"],
                "payloadsize": receive["payloadsize"],
                "payload": hex_dig
            }

            #convert dictionary into string
            ack = json.dumps(ack)
            conn.sendall(bytes(ack, encoding="utf-8"))
            print("Sending a response to client {0}, payload: {1}".format(receive['srcid'],hex_dig))

        self.serverSocket.close()

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
server = Server(args)

# def main():
#     # parse commandline arguments
#     # initialize the parser
#     parser = argparse.ArgumentParser(description='Process arguments.')

#     # add arguments
#     parser.add_argument('-id', type=int, help='id for the server')
#     parser.add_argument('-pp', type=str, help='privacy policy id number for the server')
#     parser.add_argument('-listen', type=int, help='port on which the server listens for messages')
#     parser.add_argument('-revproc', type=int, help='reverse proxy port')

#     # parse
#     args = parser.parse_args()

#     print('Server runing with id', args.id)
#     print('Server serving privacy policy', args.pp)

#     host = '127.0.0.1' # localhost
#     port = args.listen #arbitrary non-privileged port
#     revproc = args.revproc #well-known port on which the reverse proxy is running
#     server_id = args.id
#     policy_id = args.pp

#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # s.bind((host,port))
#     # # print('Socket is binded to port ', port)

#     # #enable a server to accept connection, putting the socket into listening mode
#     # #it specifies the number of unaccpeted connections that the system will allow before
#     # # refusing new connections
#     # s.listen(1)
#     # print("Server is listening on port ", port)

#     # while True:
#     #     #establish connection with client
#     #     conn, addr = s.accept()

#     #     print('Connected by ', addr)

#     #     while True:
#     #         receive = conn.recv(1024)
#     #         # receive = receive.decode("utf-8")
#     #         receive = json.loads(receive) #convert string to json object

#     #         if not receive:
#     #             break

#     #         # compute SHA1 hash of message
#     #         hash_object = hashlib.sha1(receive['payload'].encode())
#     #         hex_dig = hash_object.hexdigest()
#     #         print(hex_dig)

#     #         ack = {
#     #             "type": 2,
#     #             "srcid": 999,
#     #             "destid": receive["srcid"],
#     #             "payloadsize": 999,
#     #             "payload": hex_dig
#     #         }

#     #         #convert dictionary into string
#     #         ack = json.dumps(ack)
#     #         conn.sendall(bytes(ack, encoding="utf-8"))

#     # s.close()

#     # connect to reverse proxy
#     s.connect((host,revproc))
#     print("Connecting to the reverse proxy on port", revproc)

#     # set up message
#     message = {
#         "type": 1, # 1 is a connection setup message from a server
#         "id": server_id, # id of the server
#         "privPolyId": policy_id, # privacy policy of the server
#         "listenport": port # port on which the server is listening
#     }

#     #convert dictionary into string
#     message = json.dumps(message)
#     while True:
#         # sent message to server
#         # s.send(message.encode('ascii'))
#         s.sendall(bytes(message,encoding="utf-8"))

#         # message received from server
#         data = s.recv(1024)
#         data = data.decode("utf-8")

#         # print recevied message
#         print('Received', repr(data))

#         # ask if the client wamts to continue
#         # ans = input('\nDo you want to continue (y/n): ')
#         # if ans == 'y':
#         #     continue
#         # else:
#         #     break

#     #close connection
#     s.close()

# if __name__ == '__main__':
#     main()
