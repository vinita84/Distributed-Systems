import math
import threading
from socket import *
import pickle
import time
import os, glob
import message_protocol


class Replica(object):
    def __init__(self, port, host, hosts, ports, outfile, pid, consistency):
        self.portList = ports
        self.hostList = hosts
        self.port = port
        self.host = host
        self.tom_ack_count = 0
        self.read_tom_ack_count = 0
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        # self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serverSocket.bind((host, int(port)))
        self.kv_store = {'t':time.time()//60}
        self.recTomQ = {}
        self.localTimestamp = 0
        self.pid = pid
        self.outfile = outfile
        self.lock = threading.Lock()
        self.getmsgQ = []
        self.setmsgQ = []
        self.consistency = consistency
        return

    def startlistening(self):
        self.serverSocket.listen(1)
        print('The server is ready to receive')
        while 1:
            connectionsocket, addr = self.serverSocket.accept()
            print("Replica::", self.pid," is listening..")
            msg = connectionsocket.recv(1024)
            msg = pickle.loads(msg)
            if msg.msg_type == "get":
                self.getmsgQ.append(msg)
                t = threading.Thread(target=self.getdata, args=(msg.msg_body, connectionsocket))
                t.start()
            elif msg.msg_type == "set":
                self.setmsgQ.append(msg)
                t = threading.Thread(target=self.writedata, args=(msg, connectionsocket))
                t.start()
            elif msg.msg_type == "tom":
                t = threading.Thread(target=self.recTom(msg, connectionsocket))
                t.start()
        return


    def cleanup(self):
        filepattern = "*_outfile_" + str(self.port) + ".txt"
        files = glob.glob(filepattern)
        for file in files:
            if len(files) > 0:
                if os.path.exists(file):
                    os.remove(file)
            else:
                break
        return

    def getdata(self, msg, connectionsocket):
        if self.consistency == "sequential" or self.consistency == "eventual":
            resp = message_protocol.Message_protocol(self.pid, 'get_resp', '')
            if msg in self.kv_store:
                resp.msg_body = self.kv_store[msg]
            else:
                resp.msg_body = "Variable not found in KV store"
            resp.local_timestamp = self.localTimestamp + self.pid * 0.1
            self.localTimestamp += 1
            connectionsocket.send(pickle.dumps(resp))
            connectionsocket.close()

        elif self.consistency == "linearizability":
            self.lock.acquire()
            self.getmsgQ.pop()
            resp = message_protocol.Message_protocol(self.pid, 'get_resp', '')
            if msg in self.kv_store:
                self.sendTom(msg)
                while self.tom_ack_count != len(self.portList):
                    time.sleep(3)
                self.tom_ack_count = 0
                resp.msg_body = self.kv_store[msg]
                connectionsocket.send(pickle.dumps(resp))
                connectionsocket.close()
                self.lock.release()
        return

    def writedata(self, msg, connectionsocket):
        self.lock.acquire()
        if self.setmsgQ[0].msg_id == msg.msg_id:
            self.setmsgQ.pop()
        resp = message_protocol.Message_protocol(self.pid, 'set_ack', '')
        # Sending TOM
        if self.consistency == "sequential" or self.consistency == "linearizability":
            self.sendTom(msg.msg_body)
            while self.tom_ack_count != len(self.portList):
                time.sleep(3)

        self.kv_store['t'] = msg.msg_body
        self.tom_ack_count = 0
        self.kv_store['t'] = msg.msg_body
        print("Replica::", self.pid, " updated the KV store with value:", msg.msg_body)
        if self.kv_store['t'] == msg.msg_body:
            resp.msg_body = "success"
        else:
            resp.msg_body = "fail"
        connectionsocket.send(pickle.dumps(resp))
        connectionsocket.close()
        self.lock.release()
        return

    def recTom(self, msg, connectionsocket):
        resp = message_protocol.Message_protocol(self.pid, 'tom_ack', '')
        # msg_body will be get in case of linearizability
        if msg.msg_body == 'get':
            resp.msg_body = self.kv_store['t']
        else:
            resp.msg_body = 'None'
        print("Replica::", self.pid, " sent tom_ack", resp.prettyprint())
        connectionsocket.send(pickle.dumps(resp))
        connectionsocket.close()
        if msg.msg_body == 'set':
            if msg.local_timestamp not in self.recTomQ:
                self.recTomQ[msg.local_timestamp] = msg.msg_body
                resp.msg_body = "success"
            else:
                resp.msg_body = "fail"
            while len(self.recTomQ):
                min_time = min(self.recTomQ.keys())
                self.kv_store['t'] = self.recTomQ[min_time]
                self.recTomQ.pop(min_time)
        return

    def sendTom(self, msg):
        tom_msg = message_protocol.Message_protocol(self.pid, 'tom', self.localTimestamp + self.pid * 0.1)
        tom_msg.msg_body = msg
        self.localTimestamp += 1
        for num in range(0, len(self.portList)):
            soc = socket(AF_INET, SOCK_STREAM)
            print("Replica::",self.pid," sending TOM:", tom_msg.prettyprint(), " to:", self.portList[num])
            soc.connect((self.hostList[num], self.portList[num]))
            sendpacket = pickle.dumps(tom_msg)
            soc.send(sendpacket)
            time.sleep(2)
            msg_recv = pickle.loads(soc.recv(1024))
            print("Replica::",self.pid," recvd msg:", msg_recv.prettyprint())
            if msg_recv.msg_type == 'tom_ack':
                if msg_recv.msg_body == 'None':
                    self.tom_ack_count += 1
                elif msg_recv.msg_body != 'None':
                    # self.read_tom_ack_count += 1
                    self.tom_ack_count += 1
                    val = math.modf(msg_recv.msg_body)[1]
                    if val>self.kv_store['t']:
                        self.kv_store['t'] = msg_recv.msg_body
            soc.close()
        return

    def execMsg(self):
        msg_file = open(type + "_" + self.outfile, 'a')
        while len(self.recTomQ):
            time_arr = self.recTomQ.keys()
            min_time = min(time_arr)
            min_msg = self.recTomQ[min_time]
            self.recTomQ.pop(min_time)
            msg_file.write(min_msg + "\n")
        return
