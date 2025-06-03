import re

# must me escaped with back-slash 
# . ^ $ * + ? { } [ ] \ | ( )


numbers= '341-214-512-1123' \
         '412-215-555-9999'



text = "pqfdaciatriadwpqfmdkalw123ldfpdafgkskak"


with open('re_data.txt', "r") as f:
    contents = f.read()
    

pattern =  re.compile(r"(8|9)\d{2}-\d{3}-\d{4}")

matches = re.finditer(pattern, contents)

for match in matches:
    print(match)
    

