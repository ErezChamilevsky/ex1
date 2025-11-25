import socket
import sys

# getting the port and ip of the server
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

# binding to the udp
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# extract IP from server response to return only the IP part
def extract_ip(response_string):
    response_string = response_string.strip()
    if response_string == "non-existent domain":
        return response_string
    parts = response_string.split(",")
    if len(parts) == 3:
        ip = parts[1]
        return ip
    return "timed-out"

# main loop of the client - getting user input, sending it to server and get from server
while True:
    domain = input()
    s.sendto(domain.encode("utf-8"), (SERVER_IP, SERVER_PORT))
    data, addr = s.recvfrom(1024)
    response_string = data.decode("utf-8")
    print(extract_ip(response_string))

s.close()
