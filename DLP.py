import re
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-bw", required=True, help="your name")
parser.add_argument("-f", type=int, help="your age")
args = parser.parse_args()

with open (args.bw, "rt") as f:
    bad_words = f.read()   

with open(args.f, "rt") as f:
    content = f.read()

found = []



pattern = re.compile(r"(\d{3}-\d{3}-\d{4})")
matches = pattern.finditer(content)

for match in matches:
    if match:
        found.append(match.group(1))

for word in bad_words:
    if word.lower() in content.lower():
        found.append(word)


if found:
    print(f"There are bad words: {', '.join(found)}")
else:
    print("There are no bad words.")
