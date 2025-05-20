import random

life = 10  # Start with 10 life points
left = "left"
right = "right"

while life > 0:
    move = input("You're in the forest. Choose a direction (left/right): ").lower()
    if move == left or move == right:
        damage = random.randint(1, 6)
        life -= damage
        print(f"You moved {move} and lost {damage} life. Remaining life: {life}")
    else:
        print("That’s not a valid direction.")
        
print("You have no life left. Game over.")
