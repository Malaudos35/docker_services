import socket
import random
import struct
from datetime import datetime
from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, QTYPE, A
from ipaddress import ip_address, ip_network
import dns.resolver

### SIMPLE DNS LIAR ###
# Send true ip for localhost 
# Send random ip to other :)
# Take advantage of wasting the bot's time 

# Configuration du serveur DNS
DNS_PORT = 53
DNS_IP = '0.0.0.0'

# Fichiers de log
LOG_FILE = 'dns_queries.log'

# Réseaux IP privés
PRIVATE_NETWORKS = [
    ip_network('127.0.0.0/8'),  # Loopback
    ip_network('10.0.0.0/8'),
    ip_network('172.16.0.0/12'),
    ip_network('192.168.0.0/16'),
]

# Serveur DNS public à utiliser pour la résolution
PUBLIC_DNS_SERVER = '1.1.1.1'

def generate_random_ip():
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def log_dns_query(client_ip, url):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}; {client_ip}; {url}\n")
        
def is_private_ip(client_ip):
    client_ip_obj = ip_address(client_ip)
    for network in PRIVATE_NETWORKS:
        if client_ip_obj in network:
            return True
    return False

def resolve_domain(domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [PUBLIC_DNS_SERVER]
    try:
        answer = resolver.resolve(str(domain), 'A')
        return str(answer[0])  # Retourne la première adresse IP trouvée
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")
        return generate_random_ip()

def handle_dns_request(data, client_address):
    try:
        request = DNSRecord.parse(data)
        client_ip = client_address[0]
        print(client_ip)

        response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

        for question in request.questions:
            if is_private_ip(client_ip):
                print("Private")
                resolved_ip = resolve_domain(question.qname)
                print(resolved_ip)
                response.add_answer(RR(question.qname, QTYPE.A, rdata=A(resolved_ip), ttl=60))
            else:
                print("Random")
                log_dns_query(client_address[0], str(question.qname))
                random_ip = generate_random_ip()
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
