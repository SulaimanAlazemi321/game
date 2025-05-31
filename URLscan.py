import argparse
import sys
from urllib.parse import urlparse
import tldextract
import re
from colorama import init, Fore, Style
from threading import Thread

#taking arguments from the user 
parser = argparse.ArgumentParser()
parser.add_argument("-u", help="example <https://google.com>")
parser.add_argument("-URL", help="file of URLs")
args = parser.parse_args()


#array of TOP-LEVEL-DOMAIN
trusted_tlds = [
    ".com", ".org", ".net", ".edu", ".gov", ".mil", ".int",
    ".uk", ".de", ".ca", ".jp", ".au", ".fr", ".it", ".us", ".ch", ".nl",
    ".tech", ".dev", ".io", ".app", ".xyz"
]

# sentative key-words
keywords = r"(login|verify|secure|banking)"

# 2 arrays to store good and bad url
malicious_URL = []
trusted_URL = []

# if non of the arguments is set it will exit 
if(not args.u and not args.URL):
    print("please provide at least 1 agrument:  \n >> -u=<https://google.com> \n >> -URL=<List-of-url.txt>")
    sys.exit()

# function to do the url scanning and adding it to the arrays
def scanning(url):
    parsed = urlparse(url)
    domain = tldextract.extract(url)
    if any(char.isdigit() for char in domain.domain + domain.subdomain):
        malicious_URL.append((url, "Contains digits in domain or subdomain"))
    elif ("." + domain.suffix not in trusted_tlds):
        malicious_URL.append((url, "Untrusted TLD"))
    elif re.search(keywords, url, re.IGNORECASE):
        malicious_URL.append((url, "Contains suspicious keyword"))
    elif len(url) > 100:
        malicious_URL.append((url, "URL too long"))
    elif len(re.findall(r"%[0-9A-Fa-f]{2}", url)) > 3:
        malicious_URL.append((url, "Too many encoded characters"))
    else:
        trusted_URL.append(url)

# if the -u argument is set it will exectute this command 
if(args.u):
    scanning(args.u)

#if the -URL argument is set it will execute this command 
if args.URL:
    threads = []
    try:
        with open(args.URL, "r") as f:
            for uri in f:
                url = uri.strip()
                t = Thread(target=scanning, args=(url,)) # using Thread to make the scanning faster 
                t.start()
                threads.append(t)
        for t in threads:
            t.join()
    except FileNotFoundError as e: # checking if the file exists
        print(e)

init(autoreset=True) # resting colors 

#outputing the arrays with styiling it 
for ma, reason in malicious_URL:
        
    print(f"⚠️ Suspicious: {Fore.RED}{ma} {Style.RESET_ALL}- Reason: {reason}")

for tu in trusted_URL:
    print(f"✅ Safe: {Style.BRIGHT} {Fore.GREEN}{tu}")