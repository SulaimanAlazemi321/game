import random
from colorama import init, Fore, Style
class Player:
   def __init__(self):
      self.__health = 100
      self.__damage = 40
   
   @property
   def health(self):
      return self.__health
   
   
   @property
   def damage(self):
      return self.__damage
   
   @health.setter
   def health(self, health):
      self.__health = health

   
   @damage.setter
   def damage(self, damage):
      self.__damage = damage

class Game:
   def __init__(self):
      self.player1 = Player()
      self.player2 = Player(  )
      self.operators = ["*" , "/", "-", "+"]

   
   def helper_Question(self,num1,num2,op, answer):
        if(op == "+"):
           return num1 + num2 == answer
        elif(op == "-"):
           return num1 - num2 == answer
        elif(op == "*"):
           return num1 * num2 == answer
        elif(op == "/"):
           return round(num1 / num2, 1) == answer
        else:
           return "nothing happen"

   def generate_question(self):
        self.op = random.choice(self.operators)
        self.num1 = random.randint(1,10)
        self.num2 = random.randint(1,10)

   def question(self):
      while True:
        self.generate_question()
        player1Answer = float(input(f"\nQuestion to player1: \nWhat is {self.num1} {self.op} {self.num2}? "))
        if self.helper_Question(self.num1, self.num2, self.op.strip(), player1Answer):
           self.player2.health -= self.player1.damage
           if self.player2.health <= 0:
              print("player2 is dead")
              break
           print(f"correct Answer you hit the player2 with {Fore.RED}{Style.BRIGHT}{self.player1.damage}{Style.RESET_ALL} damage \nplayer2 HP -> {Fore.GREEN}{Style.BRIGHT}{self.player2.health}{Style.RESET_ALL}")
        else:
         print(f"Wrong Answer \nplayer2 HP ->  {Fore.GREEN}{Style.BRIGHT}{self.player2.health}{Style.RESET_ALL}")

        self.generate_question()
        player2Answer = float(input(f"\nQuestion to player2: \nWhat is {self.num1} {self.op} {self.num2}? "))
        if self.helper_Question(self.num1, self.num2, self.op.strip(), player2Answer):
           self.player1.health -= self.player2.damage
           if self.player1.health <= 0:
              print("player1 is dead")
              break
           print(f"correct Answer you hit the player1 with{Fore.RED}{Style.BRIGHT} {self.player2.damage} {Style.RESET_ALL}damage \nplayer1 HP -> {Fore.GREEN}{Style.BRIGHT}{self.player1.health} {Style.RESET_ALL}")
        else:
         print(f"Wrong Answer \nplayer1 HP -> {Fore.GREEN}{Style.BRIGHT}{self.player1.health}{Style.RESET_ALL}") 

try:      
   game1 = Game()
   game1.question()
except ArithmeticError as e:
   print(f"error -> {e}")
   game1.question()
except Exception as e:  
   print(f"error -> {e}")
   game1.question()
except KeyboardInterrupt as e:
   print(f"\nexisting...")




      