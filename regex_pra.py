import re

# must me escaped with back-slash 
# . ^ $ * + ? { } [ ] \ | ( )


numbers= '341-214-512-1123' \
         '412-215-555-9999'



text = "pqfdaciatriadwpqfmdkalw123ldfpdafgkskak"


with open('re_data.txt', "r") as f:
    contents = f.read()
    

pattern = re.compile(r"[a-zA-z0-9.-]+@[a-zA-Z-]+\.[a-zA-Z]+")


matches = re.finditer(pattern, contents)

for match in matches:
    print(match.group(0))
    

