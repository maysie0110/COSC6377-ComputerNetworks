# import socket module
import socket

import sys
import argparse
import json

# def arguments_parser():
#     # initialize the parser
#     parser = argparse.ArgumentParser(description='Process arguments.')
    
#     # add arguments
#     parser.add_argument('-id', type=int, help='id for the client')
#     parser.add_argument('-revproc', type=int, help='reverse proxy port')
#     parser.add_argument('-pkt', type=str, help='message filename')
    
#     # parse
#     args = parser.parse_args()
    
#     # access arguments
#     print("Argument values:")
#     print(args.id)
#     print(args.revproc)
#     print(args.pkt)
#     port = args.revproc

class Client:
    def __init__(self, args):
        super().__init__()
        
        self.host = '127.0.0.1' #local host IP address
        self.revproc = args.revproc #define port on which you want to connect
        self.file = args.pkt
        self.policy_id=''
        #create a new socket
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect()
        
    def connect(self):

        #connect to server on local computer
        self.socket.connect((self.host, self.revproc))
        print('Socket connected on port ', self.revproc)
        
        # parsing JSON format message
        message = self.json_message()
        
        while True:
            # sent message to server
            # s.send(message.encode('ascii'))
            self.socket.sendall(bytes(message,encoding="utf-8"))
            print("Sending a message to privacy policy {0} through reverse proxy running on port {1}"\
                .format(self.policy_id, self.revproc))
                
            # message received from server
            receive= self.socket.recv(1024)
            # data = data.decode("utf-8")
            receive = json.loads(receive) #convert string to json object
            
            # print recevied message
            print("Reveiving message from the server {0}, payload: {1}"\
                .format(receive["srcid"], receive["payload"]))

            # ask if the client wamts to continue
            # ans = input('\nDo you want to continue (y/n): ')
            # if ans == 'y':
            #     continue
            # else:
            #     break
                
        #close connection
        self.socket.close()

    def json_message(self):
        with open('test_payloads/' + self.file + '.json') as f:
            json_data = json.load(f)
            self.policy_id = json_data['privPoliId']
            # data ={
            #     'type': json_data['type'],
            #     'srcid': json_data['srcid'],
            #     'privPoliId': json_data['privPoliId'],
            #     'payloadsize': json_data['payloadsize'],
            #     'payload': json_data['payload']
            # }
            data = json.dumps(json_data)
        return data

# parse commandline arguments
# initialize the parser
parser = argparse.ArgumentParser(description='Process arguments.')

# add arguments
parser.add_argument('-id', type=int, help='id for the client')
parser.add_argument('-revproc', type=int, help='reverse proxy port')
parser.add_argument('-pkt', type=str, help='message filename')

# parse
args = parser.parse_args()

client = Client(args)
    
# def main():
    
#     # parse commandline arguments
#     # initialize the parser
#     parser = argparse.ArgumentParser(description='Process arguments.')
    
#     # add arguments
#     parser.add_argument('-id', type=int, help='id for the client')
#     parser.add_argument('-revproc', type=int, help='reverse proxy port')
#     parser.add_argument('-pkt', type=str, help='message filename')
    
#     # parse
#     args = parser.parse_args()
    
#     # access arguments
#     # print("Argument values:")
#     # print(args.id)
#     # print(args.revproc)
#     # print(args.pkt)
    
    
#     host = '127.0.0.1' #local host IP address
#     port = args.revproc #define port on which you want to connect

#     #create a new socket
#     s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#     #connect to server on local computer
#     s.connect((host,port))
#     print('Socket connected on port ', port)
    
#     # parsing JSON format message
#     filename = args.pkt
#     message = json_message(filename)
    
#     while True:
#         # sent message to server
#         # s.send(message.encode('ascii'))
#         s.sendall(bytes(message,encoding="utf-8"))
#         print("Sending a message to privacy policy {0} through reverse proxy running on port {1}"\
#             .format(message['']))
            
#         # message received from server
#         data = s.recv(1024)
#         data = data.decode("utf-8")
        
#         # print recevied message
#         print('Received', repr(data))
        
#         # ask if the client wamts to continue
#         ans = input('\nDo you want to continue (y/n): ')
#         if ans == 'y':
#             continue
#         else:
#             break
        
#     #close connection
#     s.close()

# if __name__ == '__main__':
#     main()
