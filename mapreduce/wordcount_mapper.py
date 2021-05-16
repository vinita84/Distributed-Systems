import sys
import pickle
from socket import *
import zmq
import time




def process_chunk(doc_id, input_data, serverport, serverhost):
    f = open("mapreduce_faulty_chunks_mapper.err", "ab")
    for lines in input_data:
        lines = lines.split("\n")
        chunk = len(lines)
        for line in range(0, len(lines), chunk):
            if chunk+line < len(lines):
                curr_chunk = lines[line:chunk+line]
            else:
                curr_chunk = lines[line:]
            response = run_mapper(curr_chunk, serverport, serverhost)
            if not response:
                pickle.dump(curr_chunk,f)
    return 1


def run_mapper(lines, serverport, serverhost):
    word_count_dict = {}
    context = zmq.Context()
    php = "tcp://" + str(serverhost) + ":" + str(serverport)
    s = context.socket(zmq.REQ)
    s.connect(php)
    for line in lines:
        line = line.strip()
        words = line.split(" ")
        for word in words:
            # print('%s\t%s' % (word, 1))
            if word in word_count_dict:
                word_count_dict[word] += 1
            else:
                word_count_dict[word] = 1

    # send the result to the KV store
    sendpacket = pickle.dumps((word_count_dict, "INTERMEDIATE"))
    s.send(sendpacket)

    time.sleep(10)
    serverresponse = pickle.loads(s.recv())
    context.destroy()
    if serverresponse:
        return 1
    return 0



