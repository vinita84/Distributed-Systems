import message_protocol
import pickle
import time, random
import os
from socket import *

class Client(object):
    def __init__(self, port, host, hosts, ports, outfile, cid, consistency):
        self.portList = ports
        self.hostList = hosts
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.localTimestamp = 0
        self.cid = cid
        self.outfile = outfile
        self.msg = None
        self.consistency = consistency
        return

    def cleanup(self):
        print(" deleting the file")
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        return

    def start_process(self):
        for i in range(0, 20):
            print("running for i=",i)
            self.send_set()
            n = random.randint(0, 8)
            time.sleep(n)
            self.send_get()
        return

    def send_set(self):
        send_msg = message_protocol.Message_protocol(self.cid, 'set', self.localTimestamp + self.cid * 0.1)
        send_msg.msg_body = time.time()//60+self.cid * 0.1 #str(send_msg.local_timestamp)+"::"+str(time.time())  #saving a combination of local and global timestamp
        self.localTimestamp += 1
        n = random.randint(0, len(self.portList)-1)
        serverName = self.hostList[n]
        serverPort = self.portList[n]
        print("CLIENT::", self.cid, " sending packet:", send_msg.prettyprint(), " by pid:", self.cid, " to:", serverPort)
        soc = socket(AF_INET, SOCK_STREAM)
        soc.connect((serverName, int(serverPort)))
        sendpacket = pickle.dumps(send_msg)
        soc.send(sendpacket)
        msg = pickle.loads(soc.recv(1024))
        time.sleep(5)
        # if self.consistency == 'linearizability':
        #     time.sleep(5)  #wait a little more for server as linearizability takes longer time
        print("CLIENT::", self.cid, " Server Response :", msg.prettyprint())
        soc.close()
        if msg.msg_body != "success":
            print("CLIENT::", self.cid, " Error occurred pid:", self.pid)
        return

    def send_get(self):
        send_msg = message_protocol.Message_protocol(self.cid, 'get', self.localTimestamp + self.cid * 0.1)
        send_msg.msg_body = 't'  #this can be set to another key if need  be
        self.localTimestamp += 1
        soc = socket(AF_INET, SOCK_STREAM)
        n = random.randint(0, len(self.portList)-1)
        serverName = self.hostList[n]
        serverPort = self.portList[n]
        print("CLIENT::", self.cid, " sending packet:", send_msg.prettyprint(), " by pid:", self.cid, " to:",
              serverPort)
        soc.connect((serverName, serverPort))
        sendpacket = pickle.dumps(send_msg)
        soc.sendall(sendpacket)
        time.sleep(2)
        if self.consistency == 'eventual':
            time.sleep(5)  #wait a little more for server as linearizability takes longer time
        msg_recv = soc.recv(1024)
        msg_recv = pickle.loads(msg_recv)
        print("CLIENT::", self.cid, " received", msg_recv.prettyprint())
        msg_file = open(self.outfile, 'a')
        msg_file.write(str(msg_recv.msg_body)+"\n")
        time.sleep(5)
        msg_file.close()
        soc.close()
        return





