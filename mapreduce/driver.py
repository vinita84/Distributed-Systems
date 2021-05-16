''' The driver will:
    * generate data on which inverted_index or word_count operations are to be performed.
    * It will then initialize a Cluster class object giving it number of mappers and reducers
    * It will then run map-reduce(either word_count or inverted_index) for the generated data on the created cluster
    * At the end it destroys all the created clusters
'''
import os
import cluster

def main():
    # Create a Master in a new process
    master_pid = os.fork()
    if master_pid == 0:
        master = cluster.Cluster()
        master.config_cluster()
        data = master.read_data()
        master.run_mapred(data)
        master.destroy_cluster()

if __name__ == "__main__":
    main()
    # os.wait()