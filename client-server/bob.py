from socket import *
import sys
import getopt

def run_bob(argv):
    sendpacket = ''.encode()
    serverName = '127.0.0.1'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    key = value = ''

    # parse arguments
    short_options = "k:v:"
    long_options = ["key=", "value="]
    try:
        arguments, values = getopt.getopt(argv, short_options, long_options)
    except getopt.error as err:
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-k", "--key"):
            key = current_value
        elif current_argument in ("-v", "--value"):
            value = current_value

    clientSocket.connect((serverName,serverPort))
    if key == 'QUIT':
        sendpacket = ('QUIT').encode()
    elif len(value)>0:
        sendpacket = ('STORE ' + key +"="+ value).encode()
    elif len(value)==0:
        sendpacket = ('GET ' + key).encode()

    clientSocket.sendall(sendpacket)
    # if serverresponse != 'Server Stopping..':
    serverresponse = clientSocket.recv(1024)
    print ("Server Response in Bob:", serverresponse)
    clientSocket.close()
    return

if __name__ == '__main__':
    run_bob(sys.argv[1:])





