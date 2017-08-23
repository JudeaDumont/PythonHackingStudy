import sys
import socket
import getopt
import threading
import subprocess
target = "192.168.0.4"
port = 9999


def usage():
    print("Attacker Client")
    print()
    print("Usage: AttackerClient.py -t target_host -p port")
    print()
    print("Examples: ")
    print("AttackerClient.py -t 192.168.0.4 -p 9999")
    sys.exit(0)


def client_sender(client_buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))  # connect to our target host
        if len(client_buffer):
            client.send(client_buffer)
            while True:
                recieving_length = 1  # wait for data
                response = ""
                while recieving_length:
                    data = client.recv(4096)
                    recieving_length = len(data)
                    response += data
                    if recieving_length < 4096:
                        break
                print(response,)
                buffer = raw_input("")  # wait for input
                buffer += "\n"
                client.send(buffer)  # send it off
    except Exception, e:
        # port is closed, server refused, peer disconnected, etc.
        print(e)
        print("[*] Exception! Exiting.")
        client.close()


def main():
    global port
    global target
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "target", "port"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    client_buffer = sys.stdin.read()
    client_sender(client_buffer)


main()
