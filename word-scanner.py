import argparse
from colorama import Style, Fore
import sys
import re
from colorama import Style, Fore

parser = argparse.ArgumentParser()
parser.add_argument("-f", help="file you want to read from", required=True)
parser.add_argument("-w", help="word you want to find", required=True)
args = parser.parse_args()  

with open(args.f, "rt", encoding='utf-8') as f:
    content = f.read()

word = args.w
pattern = re.compile(rf'\b{re.escape(word.strip())}\b')
matches = list(re.finditer(pattern,content))

if not matches:
    print(f"no pattern for the word {word}")
    sys.exit()

try:
        userInput = input(f" the word {Fore.GREEN}{word.strip()}{Style.RESET_ALL} has been mentioned {len(matches)} times would you like to replace it? y/n ")
        if userInput == "y":
            chosenWord = input("please write the new word: ")
            if(len(chosenWord.strip()) < 20):
                    content = re.sub(rf'\b{re.escape(word.strip())}\b', chosenWord.strip(), content)
            else:
                print("the new word is too long, max length in 20")
                sys.exit()
        elif userInput == "n":
            print('exiting...')
            sys.exit()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            sys.exit()
except KeyboardInterrupt as e:
    print("exiting...")
 
