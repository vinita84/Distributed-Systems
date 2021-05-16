from socket import *

import pickle
import sys
import time
import zmq



def run_reducer(id, serverport, serverhost, number_reducers):
    global_arr = []
   #  f = open("mapreduce_faulty_chunks_reducer.err", "ab")
   #  context = zmq.Context()
   #  php = "tcp://" + str(serverhost) + ":" + str(serverport)
   #  s = context.socket(zmq.REQ)
   #  s.connect(php)
   #
   #  # get corresponding key data from the KV store
   #  sendpacket = pickle.dumps(((id, number_reducers), 'GET'))
   #  s.send(sendpacket)
   #  print("\n sent packet in reducer")
   #  time.sleep(5)
   #  input = pickle.loads(s.recv())
   #  k = None
   #  total = 0
   #
   #  # Perform the reduction
   #  for (key, value) in input:
   #      count = int(value.strip())
   #
   #      if key == k:
   #          total += count
   #      else:
   #          if key:
   #              global_arr.append((key, total))
   #          k = key
   #          total = count
   #  if key:
   #      global_arr.append((key, total))
   #
   #
   #  time.sleep(5)
   #  # Send the result to KV store
   #  sendpacket = pickle.dumps((global_arr, 'FINAL'))
   #  s.send(sendpacket)
   #
   #  time.sleep(5)
   #  serverresponse = pickle.loads(s.recv())
   #  # print("\n server response in reducer id ", id," is:",serverresponse)
   #  # s.close()
   #
   #  if serverresponse:
   #      if id == number_reducers - 1:
   #          s.send(pickle.dumps((0, "STOP")))
   #      time.sleep(5)
   #      context.destroy()
   #  else:
   #      pickle.dump(sendpacket, f)
   #      context.destroy()
   # # TODO: ping the master to say I am done
    time.sleep(5)
    print("Reducer ", id," Finished.")
    return 1



