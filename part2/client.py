import socket
import sys

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    domain = input()
    s.sendto(domain.encode("utf-8"), (SERVER_IP, SERVER_PORT))
    data, addr = s.recvfrom(1024)
    response_string = data.decode("utf-8")
    print(response_string)

s.close()
