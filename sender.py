import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(100000):
    s.sendto(f"{i}".encode(), ("192.168.182.1", 9001))
s.close()