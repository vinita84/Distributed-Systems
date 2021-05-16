
import configparser
import client
import replica
import os, time

class Driver(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.processports = list(map(int, config.get("DEFAULT", "process_port_numbers").split(" ")))
        print(self.processports)
        self.replicaports = list(map(int, config.get("DEFAULT", "replica_port_numbers").split(" ")))
        self.processhosts = list(map(str.strip, config['DEFAULT']['process_host_addresses'].split(',')))
        self.replicahosts = list(map(str.strip, config['DEFAULT']['replicas_host_addresses'].split(',')))
        self.consistency = config.get("DEFAULT", "consistency")
        return

    def start_replicas(self):
        print("Starting Replicas on ports:", self.replicaports)
        for i in range(0, len(self.replicaports)):
            pid = os.fork()
            if pid == 0:
                port = self.replicaports[i]
                host = self.replicahosts[i].strip()
                replica_obj = replica.Replica(port, host, self.replicahosts, self.replicaports, 'outfile_' + str(port) + '.txt', i, self.consistency)
                replica_obj.startlistening()
                break
            else:
                continue

    def start_processes(self):
        for j in range(0, len(self.processports)):
            time.sleep(3)
            pid = os.fork()
            if pid == 0:
                port = self.processports[j]
                host = self.processhosts[j].strip()
                client_obj = client.Client(port, host, self.replicahosts, self.replicaports, 'outfile_' + str(os.getpid()) + '.txt', j, self.consistency)
                client_obj.start_process()
                break
            else:
                time.sleep(5)
                continue
        time.sleep(10)
        print("start processes is exiting")
        return

    def start_execution(self):
        self.start_replicas()
        self.start_processes()
        print("start_execution is exiting")
        return