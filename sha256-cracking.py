import hashlib
import sys
import os

hash = None
wordlist = None

args = " ".join(sys.argv[1:]).replace(" ", "")
for argument in args.split("-"):
    if "=" in argument:
        key, value = argument.split("=", 1)
        if key == 'hash':
            hash = value
        elif key == 'w':
            wordlist = value  
            
if not hash or not wordlist:
    print(f"please Enter the following arguments:\n{sys.argv[0]} -hash = <theHash> -w = <the wordlist>")
else:
    if (not os.path.exists(wordlist)):
        print(f"[!] File not found: {wordlist}")
        sys.exit()
    with open(wordlist, 'r') as f:
        for word in f:
            hashed = hashlib.sha256(word.strip().encode()).hexdigest()
            if hashed == hash:
                print(f"the word \033[92m{word.strip()}\033[0m is the value of the hash")
                sys.exit()
        print("hash not found")

        