
import configparser
import process
import os

class Driver(object):
    def __init__(self):
        self.ports = []
        self.hosts = []
        self.num_processes = 0
        return

    def config_cluster(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.num_processes = config.getint('DEFAULT', 'num_processes')
        self.ports = list(map(str.strip, config['DEFAULT']['port_numbers'].split(',')))
        self.hosts = list(map(str.strip, config['DEFAULT']['host_addresses'].split(',')))
        return

    def send_msg(self, ports, msg_types):
        print(ports)
        for i in range(0, len(ports)):
            pid = os.fork()
            if pid == 0:
                port = ports[i]
                host = self.hosts[i].strip()
                server1 = process.Process(port, host, self.hosts, ports, 'outfile_'+str(port)+'.txt', i)
                server1.startprocess(msg_types)
            else:
                continue

if __name__ == "__main__":
    d = Driver()
    d.config_cluster()
    d.send_msg(d.ports, msg_types=[("sendtom","A=200",[8000, 12000, 8080]), ("sendtom","A-100=100", [8000, 12000, 8080]), ("sendtom","A*0=0", [8000, 12000, 8080]), ("sendtom","STOP", [8000, 12000, 8080]), ("sendp2p","A=0",[12001]), ("sendp2p","A-100=-100",[12001]), ("sendp2p","A+100=0",[12001])])
