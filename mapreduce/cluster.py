# Master is a library consisting of one class called Cluster, for now. It will initiate a cluster whenever its object is created.
# The cluster will have properties like number of mappers, number of reducers to start a cluster.
# It will have other operations (like run_mapred, destroy_cluster etc.) in the form of functions calls.

import dill
import os, signal
import time
import configparser
import server
import importlib


class Cluster:
    def __init__(self):
        self.num_mappers = 0
        self.num_reducers = 0
        self.serverport = 0
        self.serverhost = 0
        self.finishedmappers = 0
        self.finishedreducers = 0
        self.filenames = []
        self.mapper_function = ''
        self.reducer_function = ''
        return

    def config_cluster(self):
        config = configparser.ConfigParser()
        config.read('mapreduce.ini')
        self.filenames = config['DEFAULT']['file_names']
        self.serverport = config.getint('DEFAULT', 'server_port')
        self.hostname = config['DEFAULT']['host']
        self.num_mappers = config.getint('DEFAULT', 'num_map')
        self.num_reducers = config.getint('DEFAULT', 'num_red')
        self.mapper_function = config['DEFAULT']['mapper_function_name']
        self.mapperclass = config['DEFAULT']['mapper_class']
        self.reducer_function = config['DEFAULT']['reducer_function_name']
        self.reducerclass = config['DEFAULT']['reducer_class']
        return

    def run_mapred(self, input_data):
        lines = input_data #.split("\n")
        chunk = len(lines)//self.num_mappers
        self.mapper_function = dill.dumps(getattr(__import__(self.mapperclass), self.mapper_function))
        self.reducer_function = dill.dumps(getattr(__import__(self.reducerclass), self.reducer_function))
        # Start the KV store server
        server_pid = os.fork()
        if server_pid == 0:
            self.myserver = server.Server(self.serverport, self.serverhost)
            self.myserver.connectclient()
        else:
            # spawn mappers
            for i in range(0, self.num_mappers):
                #TODO: find a way to fork processes on different physical nodes
                if (i+1)*chunk < len(lines):
                    mapper_input = lines[i*chunk:(i+1)*chunk]
                else:
                    mapper_input = lines[i * chunk:]
                mapper_pid = os.fork()
                # forked += 1
                if mapper_pid == 0:
                    run_mapper = dill.loads(self.mapper_function)
                    self.finishedmappers += run_mapper(chunk*i, mapper_input, self.serverport, self.serverhost)
            while 1:
                # Barrier for the mappers to finish
                if self.finishedmappers == self.num_mappers:
                    print("All mappers are done. Starting reducers")
                    for r in range(0, self.num_reducers):
                        reducer_pid = os.fork()
                        if reducer_pid == 0:
                            run_reducer = dill.loads(self.reducer_function)
                            self.finishedreducers += run_reducer(r, self.serverport, self.serverhost, self.num_reducers)
                # Reset number of finished mappers after spawning all reducers
                self.finishedmappers = 0
                if self.finishedreducers == self.num_reducers:
                    break
        time.sleep(15)
        return

    def read_data(self):
        data = []
        for afile in self.filenames.split(','):
            afile = afile.strip()
            f = open(afile, "r", encoding='utf-8-sig')
            data.append(f.read())
            f.close()
        return data

    def destroy_cluster(self):
        # os.killpg(os.getpid(), signal.SIGTERM)
        pass