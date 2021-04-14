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
import select
import time
import random
import math
import multiprocessing


BUFF_SIZE = 4096

class ReverseProxy(object):
    def __init__(self, port):
        super().__init__()

        self.host = ''
        self.port = port

        self.servers = []
        self.activeServers = [] # Servers currently processing a job
        self.listenSocket = None # Socket for incoming connections
        self.cleanThread = None # Cleans up completed servers
        self.terminate = False # Changes to True when the application terminate
        self.addServer()
        # self.run()
    # Create messages switching table
    def addServer(self):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
            
        s.listen(1)
        while True:
            conn, addr = s.accept()
            
            print("Connected to {0}:{1}".format(addr[0], addr[1]))
            
            #reverse proxy forks a thread and pass the connection
            # socket to this thread
            # self.handle_client_connection(client_conn, client_addr)
            # start_new_thread(self.multi_thread, (conn,))  
            
            data = conn.recv(BUFF_SIZE)
            if not data:
                print('Connection disconnected.')
                break
            #lock released on exit
            # print_lock.release()
            # break
        

            data = json.loads(data) #convert string to json object
            
            self.servers.append({
                'policy': data['privPolyId'],
                'port': data['listenport'],
                'id': data['id']
            })

        s.close()
        print(self.servers)
        # self.servers.append({
        #     'policy': message['privPolyId'],
        #     'port': message['listenport'],
        #     'id': message['id']
        # })
        

    def run(self):
        # signal.signal(signal.SIGTERM, self.closeWorkers)
        while True:
            try:
                listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except:
                    pass
                
                listenSocket.bind((self.host,self.port))
                self.listenSocket = listenSocket
                break
            
            except Exception as e:
                print("Failed to bind to {0}:{1}".format(self.host, self.port))
                time.sleep(5)
                
        listenSocket.listen(5)
        print("Reverse Proxy is listening on port {0}".format(self.port))
        
        # Create thread that will cleanup completed tasks
        self.cleanupThread = cleanupThread = threading.Thread(target=self.cleanup)
        cleanupThread.start()

        # Create thread that will retry failed tasks
        retryThread = threading.Thread(target=self.retryFailedServers)
        retryThread.start()
        
        
        try:
            while self.terminate is False:
                for serverInfo in self.servers:
                    if self.terminate is True:
                        break
                    try:
                        (clientConnection, clientAddr) = listenSocket.accept()
                    except:
                        print("Cannot bind to {0}:{1}".format(self.host, self.port))
                        
                        if self.terminate is False:
                            # Exception did not come from termination process, wait fo 3s and continue
                            time.sleep(3)
                            continue
                        
                        raise #if termination did come from termination process, so abort
                    
                
                    server = serverSocket(clientConnection, clientAddr, serverInfo['port'])
                    self.activeServers.append(server)
                    server.start()
        except Exception as e:
            print("Error. Shutting down servers on {0}:{1}".format(self.host, self.port))
            self.closeServers()
            return
        
        self.closeServers()
    
    
    def cleanup(self):
        time.sleep(3) 
        while self.terminate is False:
            currentServer = self.activeServers[:]
            for server in currentServer:
                server.join(.02)
                if server.is_alive() == False: #Completed
                    self.activeServers.remove(server)
            time.sleep(2)
            
               
    def closeServers(self):
        self.terminate = True
        time.sleep(1)
        
        try:
            self.listenSocket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.listenSocket.close()
        except:
            pass
        
        if not self.activeServers:
            self.cleanThread and self.cleanThread.join(3)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            sys.exit(0)

        for server in self.activeServers:
            try:
                server.terminate()
                os.kill(server.pid, signal.SIGTERM)
            except:
                pass
        time.sleep(1)
        
        remainingServers = []
        for server in self.activeServers:
            server.join(.03)
            if server.is_alive() is True: # Still running
                remainingServers.append(server)

        if len(remainingServers) > 0:
            # One last chance to complete, then we kill
            time.sleep(1)
            for pumpkinWorker in remainingServers:
                pumpkinWorker.join(.2)

        self.cleanThread and self.cleanThread.join(2)

        signal.signal(signal.SIGTERM, signal.SIG_DFL)

        sys.exit(0)
        
    def retryFailedServers(self):
        time.sleep(2)
        successfulRuns = 0
        
        while self.terminate is False:
            currentServers = self.activeServers[:]
            
            for server in currentServers:
                if server.failedToConnect.value == 1:
                    successfulRuns = -1
                    print("Fail to connect to server \n")
                    numServers = len(self.servers)
                    
                    if numServers > 1:
                        nextServerInfo = None
                        while (nextServerInfo is None) or server.serverPort == nextServerInfo['port']:
                            nextServerInfo = self.servers[random.randint(0, numServers-1)]
                    else:
                        # In this case, we have no option but to try on the same host.
                        nextServerInfo = self.servers[0]
                        
                    print("Retrying request from {0}:{1} on {1}:{3}"\
                        .format(server.clientAddr, server.serverAddr, server.serverPort,nextServerInfo['id']))

                    nextServer = serverSocket(server.clientSocket, server.clientAddr, nextServerInfo['id'], nextServerInfo['port'])
                    
                    nextServer.start()
                    self.activeServers.append(nextServer)
                    server.failedToConnect.value = 0
            successfulRuns += 1
            
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
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        
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
        
        signal.signal(signal.SIGTERM, self.closeConnection)
        
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

    # globalIsTerminating = False
    
    # def handleSigTerm(*args):
    #     global listeners
    #     global globalIsTerminating

    #     if globalIsTerminating is True:
    #         return # Already terminating
    #     globalIsTerminating = True
    #     print('Caught signal, shutting down listeners...\n')
    #     for listener in listeners:
    #         try:
    #             os.kill(listener.pid, signal.SIGTERM)
    #         except:
    #             pass
    #     print('Sent signal to children, waiting up to 4 seconds then trying to clean up\n')
    #     time.sleep(1)
    #     startTime = time.time()
    #     remainingListeners = listeners
    #     remainingListeners2 = []
    #     for listener in remainingListeners:
    #         print('Waiting on %d...\n' %(listener.pid,))
    #         listener.join(.05)
    #         if listener.is_alive() is True:
    #             remainingListeners2.append(listener)
    #     remainingListeners = remainingListeners2
    #     print('Remaining (%d) listeners are: %s\n' %(len(remainingListeners), [listener.pid for listener in remainingListeners]))

    #     afterJoinTime = time.time()

    #     if remainingListeners:
    #         delta = afterJoinTime - startTime
    #         remainingSleep = int(6.0 - math.floor(afterJoinTime - startTime))
    #         if remainingSleep > 0:
    #             anyAlive = False
    #             # If we still have time left, see if we are just done or if there are children to clean up using remaining time allotment
    #             if threading.activeCount() > 1 or len(multiprocessing.active_children()) > 0:
    #                 print('Listener closed in %1.2f seconds. Waiting up to %d seconds before terminating.\n' %(delta, remainingSleep))
    #                 thisThread = threading.current_thread()
    #                 for i in range(remainingSleep):
    #                     allThreads = threading.enumerate()
    #                     anyAlive = False
    #                     for thread in allThreads:
    #                         if thread is thisThread or thread.name == 'MainThread':
    #                             continue
    #                         thread.join(.05)
    #                         if thread.is_alive() == True:
    #                             anyAlive = True

    #                     allChildren = multiprocessing.active_children()
    #                     for child in allChildren:
    #                         child.join(.05)
    #                         if child.is_alive() == True:
    #                             anyAlive = True
    #                     if anyAlive is False:
    #                         break
    #                     time.sleep(1)

    #             if anyAlive is True:
    #                 print('Could not kill in time.\n')
    #             else:
    #                 print('Shutdown successful after %1.2f seconds.\n' %( time.time() - startTime))

    #         else:
    #             print('Listener timed out in closing, exiting uncleanly.\n')
    #             time.sleep(.05) # Why not? :P

    #     print('exiting...\n')
    #     signal.signal(signal.SIGTERM, signal.SIG_DFL)
    #     signal.signal(signal.SIGINT, signal.SIG_DFL)
    #     sys.exit(0)
    #     os.kill(os.getpid(), signal.SIGTERM)
    #     return 0
    # # END handleSigTerm




