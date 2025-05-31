import random
class enemy:
    def __init__(self):
        self.health = 100
        self.damage = 50

class hero:
    def __init__(self):
        self.health = 100
        self.damage = 50

class game:
    hero = hero()
    enemy = enemy()    
    operators = ["/","*","+","-"]

    while hero.health > 0 and enemy.health > 0:
        num1 = random.randint(1,10)
        num2 = random.randint(1,10)
        op = random.choice(operators)
        if op == "+":   
            heroAnswer = input(f"question to hero what is {num1} {op} {num2}?: ")
            if int(heroAnswer) == num1 + num2:
                enemy.health -= hero.damage
                print(f"enemy hp is {enemy.health} good job")
            else:
                print(f"attack failed enemy hp is {enemy.health}") 
            if (enemy.health <= 0):
                break
            num3 = random.randint(1,10)
            num4 = random.randint(1,10)
            enemyAnswer = input(f"question to hero what is {num3} {op} {num4}?: ")
            if int(enemyAnswer) == num3 + num4:
                hero.health -= enemy.damage
                print(f"you got hurt your hp is: {hero.health} Cerful! ")
            else:
                print(f"attack failed hero hp is {hero.health}") 
        elif op == "-":
            heroAnswer = input(f"question to hero what is {num1} {op} {num2}?: ")
            if int(heroAnswer) == num1 - num2:
                enemy.health -= hero.damage
                print(f"enemy hp is {enemy.health} good job")
            else:
                print(f"attack failed enemy hp is {enemy.health}") 
            if (enemy.health <= 0):
                break
            num3 = random.randint(1,10)
            num4 = random.randint(1,10)
            enemyAnswer = input(f"question to hero what is {num3} {op} {num4}?: ")
            if int(enemyAnswer) == num3 - num4:
                hero.health -= enemy.damage
                print(f"you got hurt your hp is: {hero.health} Cerful! ")
            else:
                print(f"attack failed hero hp is {hero.health}")     
        elif op == "/":
            heroAnswer = input(f"question to hero what is {num1} {op} {num2}?: ")
            if int(heroAnswer) == num1 / num2:
                enemy.health -= hero.damage
                print(f"enemy hp is {enemy.health} good job")
            else:
                print(f"attack failed enemy hp is {enemy.health}") 
            if (enemy.health <= 0):
                break
            num3 = random.randint(1,10)
            num4 = random.randint(1,10)
            enemyAnswer = input(f"question to hero what is {num3} {op} {num4}?: ")
            if int(enemyAnswer) == num3 / num4:
                hero.health -= enemy.damage
                print(f"you got hurt your hp is: {hero.health} Cerful! ")
            else:
                print(f"attack failed hero hp is {hero.health}")     
        elif op == "*":
            heroAnswer = input(f"question to hero what is {num1} {op} {num2}?: ")
            if int(heroAnswer) == num1 * num2:
                enemy.health -= hero.damage
                print(f"enemy hp is {enemy.health} good job")
            else:
                print(f"attack failed enemy hp is {enemy.health}") 
            if (enemy.health <= 0):
                break
            num3 = random.randint(1,10)
            num4 = random.randint(1,10)
            enemyAnswer = input(f"question to hero what is {num3} {op} {num4}?: ")
            if int(enemyAnswer) == num3 * num4:
                hero.health -= enemy.damage
                print(f"you got hurt your hp is: {hero.health} Cerful! ")
            else:
                print(f"attack failed hero hp is {hero.health}")             
                
        
