import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(("0.0.0.0", 514))

print("listenning on UDP...")

while True:
    data, addr = s.recvfrom(1024)
    print(data.decode())
