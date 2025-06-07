import yaml
import random

with open("data.yaml", "rt") as f:
    data = yaml.safe_load(f)


def game():
    if data["game"]["mode"] == "single": 
        correct_number = random.randint(data["game"]["min_number"],data["game"]["max_number"])
        for i in range(data["game"]["guesses"]):
            user_guess = input("Please enter your guess: ")
            if int(user_guess) > int(correct_number): 
                print("too high")
            elif int(user_guess) < int(correct_number): 
                print("too low")
            elif int(user_guess) == int(correct_number) :
                print(f"good job the currect number was {correct_number} you got it in {i} guess")
                exit()
        print(f"you lost the correct number was {correct_number}")


game()