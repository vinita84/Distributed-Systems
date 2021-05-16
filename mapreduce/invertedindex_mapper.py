import pickle
import zmq
import time


def process_chunk(doc_id, input_data, serverport, serverhost):
    f = open("mapreduce_faulty_chunks_mapper.err", "ab")

    for l in range (0,len(input_data)):
        lines = input_data[l].split("\n")
        chunk = len(lines)//1
        for line in range(0, len(lines), chunk):
            if chunk+line < len(lines):
                curr_chunk = lines[line:chunk+line]
            else:
                curr_chunk = lines[line:]
            response = run_mapper(doc_id+l, curr_chunk, serverport, serverhost)
            if not response:
                pickle.dump(curr_chunk,f)
    return 1


def run_mapper(doc_id, lines, serverport, serverhost):
    invertedindex = {}
    context = zmq.Context()
    php = "tcp://" + str(serverhost) + ":" + str(serverport)
    s = context.socket(zmq.REQ)
    s.connect(php)
    found_docid = 0
    for line in lines:

        line = line.strip()
        words = line.split(" ")
        for word in words:
            # print('%s\t%s' % (word, 1))
            if word in invertedindex:
                found_docid = 0
                for i in range(0, len(invertedindex[word])):
                    [d,c] = invertedindex[word][i]
                    if d == doc_id:
                        invertedindex[word][i][1] = c+1
                        found_docid = 1
                        break
                if not found_docid:
                    invertedindex[word].append([doc_id, 1])
                # invertedindex[word] = [[i, j + 1] if (j == doc_id) else [i, j] for [i, j] in invertedindex[word]]
            else:
                invertedindex[word] = [[doc_id, 1]]

    # send the result to the KV store
    sendpacket = pickle.dumps((invertedindex, "INTERMEDIATE"))
    s.send(sendpacket)

    time.sleep(10)
    serverresponse = pickle.loads(s.recv())
    context.destroy()
    if serverresponse:
        return 1
    return 0



