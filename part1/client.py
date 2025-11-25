import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


s.sendto(b'Erez and Shir', ('127.0.0.1', 12345))
data, addr = s.recvfrom(1024)
print(str(data), addr)

s.close()