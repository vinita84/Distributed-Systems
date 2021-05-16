# import configparser
# import process
# import os
#
# class EventualDriver(object):
#     def __init__(self):
#         self.processports = []
#         self.replicaports = []
#         self.processhosts = []
#         self.replicahosts = []
#         self.consistency = 'sequential'
#         # self.num_processes = 0
#         return
#
#     def config_cluster(self):
#         config = configparser.ConfigParser()
#         config.read('config.ini')
#         # self.num_processes = config.getint('DEFAULT', 'num_processes')
#         # self.num_replicas = config.getint('DEFAULT', 'num_replicas')
#         self.processports = list(map(str.strip, config['DEFAULT']['process_port_numbers'].split(',')))
#         self.replicaports = list(map(str.strip, config['DEFAULT']['replicas_port_numbers'].split(',')))
#         self.processhosts = list(map(str.strip, config['DEFAULT']['process_host_addresses'].split(',')))
#         self.replicahosts = list(map(str.strip, config['DEFAULT']['replicas_host_addresses'].split(',')))
#         self.consistency = config['DEFAULT']['consistency']
#         return
#
#     def startreplicas(self):
#         print("Starting Replicas on ports:",self.replicaports)
#         for i in range(0, len(self.replicaports)):
#             pid = os.fork()
#             if pid == 0:
#                 port = self.replicaports[i]
#                 host = self.hosts[i].strip()
#                 server1 = process.Process(port, host, self.replicahosts, self.replicaports, 'outfile_' + str(port) + '.txt', i)
#                 server1.startprocess(self.consistency)
#             else:
#                 continue
#
#     def startprocesses(self):
#         print("Starting Processes on ports:",self.processports)
#         for i in range(0, len(self.processports)):
#             pid = os.fork()
#             if pid == 0:
#                 port = self.processports[i]
#                 host = self.hosts[i].strip()
#                 server1 = process.Process(port, host, self.processhosts, self.processports, 'outfile_' + str(port) + '.txt', i)
#                 server1.startprocess(self.consistency)
#             else:
#                 continue
#
#     def start_execution(self):
#         self.startreplicas()
#         self.startprocesses()
#
#
#
#     # d.send_msg(d.ports, msg_types=[("sendtom","A=200",[8000, 12000, 8080]), ("sendtom","A-100=100", [8000, 12000, 8080]), ("sendtom","A*0=0", [8000, 12000, 8080]), ("sendtom","STOP", [8000, 12000, 8080]), ("sendp2p","A=0",[12001]), ("sendp2p","A-100=-100",[12001]), ("sendp2p","A+100=0",[12001])])
