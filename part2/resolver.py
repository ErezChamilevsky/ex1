import socket
import sys
import time

# arguments
MY_PORT = int(sys.argv[1])
PARENT_IP = sys.argv[2]
PARENT_PORT = int(sys.argv[3])
TTL = int(sys.argv[4])

# resolver socket
resolver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
resolver_sock.bind(("", MY_PORT))

cache = {}

# send a query to a server and return its response
def ask_server(ip, port, domain):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    try:
        s.sendto(domain.encode("utf-8"), (ip, port))
        data, _ = s.recvfrom(1024)
        s.close()
        return data.decode("utf-8").strip()
    except socket.timeout:
        s.close()
        return "non-existent domain"

# extract IP and port from the combined argument
def split_ip_port(ip_string):
    if ":" in ip_string:
        ip, port = ip_string.split(":")
        return ip, int(port)
    return ip_string, None

# main loop
while True:
    data, client_addr = resolver_sock.recvfrom(1024)
    domain = data.decode("utf-8").strip()

    # option 1: in cache - check cache
    if domain in cache:
        saved_response, saved_time = cache[domain]
        if time.time() - saved_time <= TTL:
            resolver_sock.sendto(saved_response.encode("utf-8"), client_addr)
            continue
        else:
            del cache[domain]

    # option 2: not in cahche - ask parent and follow NS chain
    current_ip = PARENT_IP
    current_port = PARENT_PORT

    while True:
        response = ask_server(current_ip, current_port, domain)

        # domain doesn't exist
        if response == "non-existent domain":
            resolver_sock.sendto(response.encode("utf-8"), client_addr)
            break
        
        # response format: domain,ip_info,type
        try:
            resp_domain, ip_info, record_type = response.split(",")
        except:
            resolver_sock.sendto("non-existent domain".encode("utf-8"), client_addr)
            break
        
        # case "A"
        if record_type == "A":
            cache[domain] = (response, time.time())
            resolver_sock.sendto(response.encode("utf-8"), client_addr)
            break
        
        # case "NS"
        if record_type == "NS":
            next_ip, next_port = split_ip_port(ip_info)
            
            if next_port is None:
                # NS without port 
                resolver_sock.sendto("non-existent domain".encode("utf-8"), client_addr)
                break
            
            # move on to the next server
            current_ip = next_ip
            current_port = next_port
            continue
