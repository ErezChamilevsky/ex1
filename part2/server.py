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

    return mappings


# Answering the query
def resolve_domain(domain_query, mappings):

    if domain_query in mappings:
        ip_info, record_type = mappings[domain_query]
        return f"{domain_query},{ip_info},{record_type}"

    ####### starting adjustment####
    best_ns_match = None
    longest_match_length = -1

    # Iterate over all mappings to find the longest matching NS record
    for domain, (ip_info, record_type) in mappings.items():
        if record_type == "NS":
            is_match = False
            ns_match_domain = ""

            # Case 1: Zone entry starts with a dot (e.g., '.co.il')
            if domain.startswith("."):
                ns_suffix = domain[1:]
                # Check if the query ends with the suffix and is not the suffix itself
                if domain_query.endswith(ns_suffix) and domain_query != ns_suffix:
                    # Ensure the match is a full domain component (e.g., mail.google.co.il matches co.il, but not gco.il)
                    if domain_query == ns_suffix or domain_query.endswith(
                        "." + ns_suffix
                    ):
                        is_match = True
                        ns_match_domain = ns_suffix

            # Case 2: Zone entry does not start with a dot (e.g., 'co.il')
            elif domain_query.endswith("." + domain):
                is_match = True
                ns_match_domain = domain

            if is_match:
                # Check if this is the longest match found so far
                current_match_length = len(ns_match_domain)
                if current_match_length > longest_match_length:
                    longest_match_length = current_match_length
                    # Store the information for the longest match
                    response_domain = ns_match_domain + "."
                    best_ns_match = f"{response_domain},{ip_info},{record_type}"

    # If a valid NS match was found, return the result for the longest one
    if best_ns_match:
        return best_ns_match

    ##### ending adjustment ####
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
