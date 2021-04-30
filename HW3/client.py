# import socket module
import socket
import hashlib
import sys
import argparse
import json

class Client:
    def __init__(self, args):
        super().__init__()
        
        self.host = 'mptrinh.ddns.net' #local host IP address
        self.revproc = args.revproc #define port on which you want to connect
        self.file = args.pkt
        self.id = args.id
        self.policy_id=''
        #create a new socket
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect()
        
    def connect(self):

        #connect to reverse proxy
        self.socket.connect((self.host, self.revproc))
        print('Socket connected on port ', self.revproc)
        
        # parsing JSON format message
        message = self.json_message()
        
        while True:
            # sent message to server
            # s.send(message.encode('ascii'))
            self.socket.sendall(bytes(message,encoding="utf-8"))
            print("Client id {0}. Sending a message to privacy policy {1} through reverse proxy running on port {2}"\
                .format(self.id, self.policy_id, self.revproc))
                
            # message received from server
            receive= self.socket.recv(1024)
            
            if not receive:
                break
            
            # data = data.decode("utf-8")
            receive = json.loads(receive) #convert string to json object
            
            if 'Error' in receive:
                print('Clien id {0}. Error: {1}'.format(self.id,receive['Error']))
                break
            
            # print recevied message
            print("Client id {0}. Reveiving message from the server {1}, payload: {2}"\
                .format(self.id, receive["srcid"], receive["payload"]))

            # compute SHA1 hash of message
            hash_object = hashlib.sha1(self.payload.encode())
            hex_dig = hash_object.hexdigest()
            
            if(hex_dig == receive['payload']):
                print("Hash matched.")
            
            break
                
        #close connection
        self.socket.close()

    def json_message(self):
        with open('test_payloads/' + self.file + '.json') as f:
            json_data = json.load(f)
            self.policy_id = json_data['privPoliId']
            self.payload = json_data['payload']
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