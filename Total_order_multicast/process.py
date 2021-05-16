import threading
from socket import *
import pickle
import zmq
import time
import json
import os, glob

class Process(object):
    def __init__(self, port, host, hosts, ports, outfile, pid):
        self.portList = ports
        self.hostList = hosts
        self.port = port
        self.host = host
        self.context = zmq.Context()
        self.p = "tcp://" + str(host) + ":" + str(port)
        # self.p_send = "tcp://" + str(host) + ":" + str(8088)
        self.soc_recv = self.context.socket(zmq.REP)
        self.soc_send = self.context.socket(zmq.REQ)
        self.sendValue = ''
        self.recTomQ = {}
        self.recAckQ = {}
        self.localTimestamp = 0
        self.pid = pid
        self.outfile = outfile
        self.lock = threading.Lock()
        self.msg = {'sender_id': '',
                    'msg_type': '',
                    'timestamp': '',
                    'msg': ''}
        return

    def startlistening(self):
        soc_recv = self.context.socket(zmq.REP)
        soc_recv.bind(self.p)
        while 1:
            print("Process ", self.pid, " Listening .. on:", self.p)
            # i += 1
            msg_recv = soc_recv.recv()
            msg_recv = pickle.loads(msg_recv)
            ack_msg = {'sender_id': self.pid,
                       'msg_type': 'ACK',
                       'timestamp': '',
                       'msg': 'recieved msg'}
            soc_recv.send(pickle.dumps(ack_msg))
            # self.msg = receivedjson
            print("\n received msg is:", msg_recv)
            if msg_recv["msg_type"] == "recv_TOM":
                self.recTom(msg_recv)
            elif msg_recv["msg_type"] == "recv_P2P":
                self.recp2p(msg_recv)
            elif msg_recv["msg_type"] == "send_TOM":
                self.sendTom()
            elif msg_recv["msg_type"] == "recv_ACK":
                self.recvAck(msg_recv)
            elif msg_recv["msg_type"] == "STOP":
                print("\n Stopping Server ..")
                self.context.destroy()
                break
            # print("\n Continuing to listen")
        # print("\n ====>>> going to destroy")
        self.context.destroy()

    def cleanup(self):
        filepattern = "*_outfile_"+str(self.port)+".txt"
        files = glob.glob(filepattern)
        print("\n  files are:", files)
        for file in files:
            if len(files) > 0:
                if os.path.exists(file):
                    os.remove(file)
            else:
                break
        return

    def startprocess(self, msg_types):
        self.cleanup()
        time.sleep(5)
        t1 = threading.Thread(target=self.startlistening, args=())
        t1.start()
        time.sleep(10)
        if self.pid == 0:
            for sendType, msg, recepients in msg_types:
                if sendType == "sendtom":
                    t = threading.Thread(target=self.sendTom, args=(msg, recepients))
                    t.start()
                elif sendType == "sendp2p":
                    t = threading.Thread(target=self.sendp2p, args=(msg, recepients))
                    t.start()

        # time.sleep(5)
        t1.join()
        return


    def recTom(self, msg_recv):
        recvd_time = msg_recv['timestamp']
        recvd_msg = msg_recv['msg']
        if recvd_time not in self.recTomQ:
            self.recTomQ[recvd_time] = recvd_msg
            # print("\n RECV TOM:", recvd_msg)
        else:
            print("\n Duplicate timestamp! "+recvd_time+" Something very wrong has happened")
        # self.sendAck()
        if recvd_msg == 'STOP':
            self.execMsg("tom")
        return


    def sendTom(self, msg, recepients):
        context_send = zmq.Context()
        # self.soc_send = context.socket(zmq.REQ)
        print("\n reached inside sendTom")
        tom_msg = {'sender_id': self.pid,
                    'msg_type': 'recv_TOM',
                    'timestamp': self.localTimestamp + self.pid*0.1,
                    'msg': msg}
        self.localTimestamp += 1
        json_packet = json.dumps(tom_msg)
        for num in range(0, len(recepients)):
            port = recepients[num]
            p = "tcp://" + str(self.host) + ":" + str(port)
            print("\n sending packet:", json_packet, " by pid:", self.pid, " to:", port)
            soc = context_send.socket(zmq.REQ)
            soc.connect(p)
            sendpacket = pickle.dumps(tom_msg)
            soc.send(sendpacket, flags=zmq.NOBLOCK)  #track=False
            soc.close()
        return

    def sendAck(self):
        ack_msg = {'sender_id': self.pid,
                    'msg_type': 'TOM_ACK',
                    'timestamp': '',
                    'msg': 'recieved TOM'}
        self.soc_recv.send(pickle.dumps(ack_msg))
        return

    def recp2p(self, msg_recv):
        print("/n Message recieved in P2P is:", msg_recv)
        msg_file = open("p2p_" + self.outfile, 'a')
        msg_file.write(msg_recv["msg"] + "\n")
        # self.sendp2p_ack(soc)
        return

    def sendp2p_ack(self, soc):
        ack_msg = {'sender_id': self.pid,
                   'msg_type': 'P2P_ACK',
                   'timestamp': '',
                   'msg': 'recieved P2P'}
        soc.send(pickle.dumps(ack_msg))
        return

    def sendp2p(self, msg, recepients):
        context_send = zmq.Context()
        # self.soc_send = context.socket(zmq.REQ)
        print("\n reached inside sendp2p")
        tom_msg = {'sender_id': self.pid,
                   'msg_type': 'recv_P2P',
                   'timestamp': self.localTimestamp + self.pid * 0.1,
                   'msg': msg}
        self.localTimestamp += 1
        port = recepients[0]
        p = "tcp://" + str(self.host) + ":" + str(port)
        soc_p2p = context_send.socket(zmq.REQ)
        soc_p2p.connect(p)
        print("\n sending packet:", tom_msg, " by pid:", self.pid, " to:", port)
        sendpacket = pickle.dumps(tom_msg)
        soc_p2p.send(sendpacket, flags=zmq.NOBLOCK)  # track=False
        soc_p2p.close()
        return

    def execMsg(self, type):
        msg_file = open(type + "_" + self.outfile, 'a')
        while len(self.recTomQ):
            time_arr = self.recTomQ.keys()
            min_time = min(time_arr)
            min_msg = self.recTomQ[min_time]
            self.recTomQ.pop(min_time)
            msg_file.write(min_msg+"\n")
        return

