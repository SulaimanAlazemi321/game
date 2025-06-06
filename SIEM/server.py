import socket
import re

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 514))

print("listening on UDP port 514...")

# Improved regex: <PRI>Mon DD HH:MM:SS Host Process[PID]: Message
pattern = re.compile(r'^(<\d+>)([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^\[]+)\[(\d+)\]:\s(.+)$')

print("format: <PRI>Timestamp Host Process[PID]: Message ")

while True:
    data, addr = s.recvfrom(8192)
    if not data:
        break
    print(f"Connected: {addr}")
    # Sometimes multiple messages in one packet; split by lines
    for line in data.decode(errors='ignore').splitlines():
        match = pattern.match(line)
        if match:
            priority = match.group(1)
            timestamp = match.group(2)
            hostname = match.group(3)
            process = match.group(4)
            pid = match.group(5)
            message = match.group(6)
            print(f"------------------\nlog:\nPriority: {priority}\n Timestamp: {timestamp}\n Host: {hostname}\n Process: {process}\n PID: {pid}\n Message: {message}")
        else:
            print(f"Warrninngg unknown match !!!!!!!!!: \n {line}")
