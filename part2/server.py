import socket
import os
import sys

#  Getting the port and file from arguments, making the socket and binding to it
SERVER_PORT = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", SERVER_PORT))
ZONE_FILE = "zone.txt"
ZONE_FILE = sys.argv[2]


# loading the zone file so the server will reply as written in txt file
def load_zone_file(file_path):
    mappings = {}

    if not os.path.exists(file_path):
        print(f"Error in path {file_path}")
        return mappings

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(",")]

                if len(parts) == 3:
                    domain, ip_info, record_type = parts
                    mappings[domain] = (ip_info, record_type)
                else:
                    print(f"Error in data {line.strip()}")

    except Exception as e:
        print(f" {e}")

    print(f"loading zone ended. there are {len(mappings)} lines")
    return mappings


# Answering the query
def resolve_domain(domain_query, mappings):

    if domain_query in mappings:
        ip_info, record_type = mappings[domain_query]
        return f"{domain_query},{ip_info},{record_type}"

    for domain, (ip_info, record_type) in mappings.items():
        if record_type == "NS":
            # --- START OF ADJUSTMENT ---
            # Check if the domain in the zone file starts with a dot.
            if domain.startswith("."):
                # If zone entry is '.co.il', check if query ends with 'co.il'
                ns_suffix = domain[1:]
                if domain_query.endswith(ns_suffix) and domain_query != ns_suffix:
                    # The response domain should be the NS domain exactly as it appears
                    # in the zone file, but we will use the logic that was working
                    # for the previous output format: 'domain.'
                    response_domain = ns_suffix + "."
                    return f"{response_domain},{ip_info},{record_type}"

            # Original logic for domains without a leading dot (e.g., 'co.il')
            elif domain_query.endswith("." + domain):
                response_domain = domain + "."
                return f"{response_domain},{ip_info},{record_type}"

            # --- END OF ADJUSTMENT ---

    return "non-existent domain"


zone_mappings = load_zone_file(ZONE_FILE)


while True:
    # getting data and client address
    data, addr = s.recvfrom(1024)

    # converting to string
    domain_query_bytes = data.strip()
    domain_query = domain_query_bytes.decode("utf-8")

    response_string = resolve_domain(domain_query, zone_mappings)
    response_bytes = response_string.encode("utf-8")
    # sending back to the client
    s.sendto(response_bytes, addr)
