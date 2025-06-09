class Enemy:
    type_enemy: str = "zombie"
    attack_enemy: int = 10
    health_enemy: int = 100

    def enemyTalk(self):
        print(f"hello I'm {self.type_enemy}")
    
    def enemyAttack(self): 
        print(f"enemy is attacking with {self.attack_enemy} damge")

    def enemWalk(self):
        print(f"the enemy {self.type_enemy} is walking to you... ")

        