import socket
import re
from urllib.parse import unquote_plus


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 80))
s.listen(1)

print("listening on http://localhost ...")

while True:
    client, address = s.accept()
    print(f"got connection from {address}")
    request = client.recv(1024)

    print("the request start --------------------------------------------")
    print(request.decode())
    print("the request end --------------------------------------------")

    answer = 0
    if b'POST' in request:
        pattern = re.compile(r"input1=([0-9]+)&input2=([0-9]+)")
        matches = pattern.finditer(request.decode())
        for match in matches:
            answer =  int(unquote_plus(match.group(1))) +  int(unquote_plus(match.group(2)))
   
    

    http_request = f'''\
    HTTP/1.1 200 OK
    Content-Type: text/html

   <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
    <form method="post">
    <label> Enter your input: </label> 
    <input type="text"  name="input1" id="input1">
    <input type="text"  name="input2" id="input2"> 
    <input type="submit" name="submit" id="submit">
    </form>
    <h1>{answer}</h1>
</body>
</html>
    '''

    client.sendall(http_request.encode())
    client.close()

