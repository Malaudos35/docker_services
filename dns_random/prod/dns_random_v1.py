import socket
import random
import struct
from datetime import datetime
from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, QTYPE, A

### SIMPLE DNS LIAR ###
# Send random ip :)
# Take advantage of wasting the bot's time 

# Configuration du serveur DNS
DNS_PORT = 53
DNS_IP = '0.0.0.0'

# Fichiers de log
LOG_FILE = 'dns_queries.log'

def generate_random_ip():
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def log_dns_query(client_ip, url):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}; {client_ip}; {url}\n")

def handle_dns_request(data, client_address):
    try:
        request = DNSRecord.parse(data)

        # Log the client IP and requested URL
        for question in request.questions:
            log_dns_query(client_address[0], str(question.qname))

        # Generate a random IP address
        random_ip = generate_random_ip()

        # Create a DNS response with the random IP
        response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        response.add_answer(RR(question.qname, QTYPE.A, rdata=A(random_ip), ttl=60))

        return response.pack()
    except Exception as e:
        print(f"Error handling DNS request: {e}")
        return None

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((DNS_IP, DNS_PORT))

    print(f"DNS server listening on {DNS_IP}:{DNS_PORT}")

    while True:
        try:
            data, client_address = sock.recvfrom(512)
            response = handle_dns_request(data, client_address)
            if response:
                sock.sendto(response, client_address)
        except Exception as e:
            print(f"Error in main loop: {e}")

if __name__ == '__main__':
    main()
