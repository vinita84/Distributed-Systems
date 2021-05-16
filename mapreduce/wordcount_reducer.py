import pickle
import sys
import time
import zmq


def run_reducer(id, serverport, serverhost, number_reducers):
    global_dict = {}
    f = open("mapreduce_faulty_chunks_reducer.err", "ab")
    context = zmq.Context()
    php = "tcp://" + str(serverhost) + ":" + str(serverport)
    s = context.socket(zmq.REQ)
    s.connect(php)

    # get corresponding key data from the KV store
    sendpacket = pickle.dumps(((id, number_reducers), 'GET'))
    s.send(sendpacket)
    print("Sent packet in reducer")
    time.sleep(5)
    input_dict = pickle.loads(s.recv())

    # Perform the reduction
    for key in input_dict.keys():
        if key in global_dict:
            global_dict[key] += sum(input_dict[key])
        else:
            global_dict[key] = sum(input_dict[key])

    # Send the result to KV store
    time.sleep(5)
    sendpacket = pickle.dumps((global_dict, 'FINAL'))
    s.send(sendpacket)

    time.sleep(5)
    serverresponse = pickle.loads(s.recv())
    if serverresponse:
        if id == number_reducers - 1:
            s.send(pickle.dumps((0, "STOP")))
        time.sleep(5)
        context.destroy()
    else:
        pickle.dump(sendpacket, f)
        context.destroy()
    time.sleep(5)
    print("Reducer ", id," Finished.", serverresponse)
    return 1



