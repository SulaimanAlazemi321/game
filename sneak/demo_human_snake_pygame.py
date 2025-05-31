import pygame, time
from snake_env import SnakeEnv

CELL = 30
GRID = 20  # Should match the large training grid size!

env = SnakeEnv(GRID, GRID)

pygame.init()
screen = pygame.display.set_mode((GRID*CELL, GRID*CELL))
pygame.display.set_caption("Human Snake Demo (Large Grid)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)

direction = (1, 0)  # Start moving right
state = env.reset()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                direction = (0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                direction = (0, 1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                direction = (1, 0)

    # Map direction to action index
    dirs = [(0,-1), (0,1), (-1,0), (1,0)]
    if direction in dirs:
        action = dirs.index(direction)
    else:
        action = 3  # Default to right

    state, _, done = env.step(action)

    # draw
    screen.fill((30,30,30))
    # Draw snake
    for i, (x,y) in enumerate(env.snake):
        color = (0,200,0) if i > 0 else (0,255,0)  # Head brighter
        pygame.draw.rect(screen, color, (x*CELL, y*CELL, CELL, CELL))
        pygame.draw.rect(screen, (10,50,10), (x*CELL, y*CELL, CELL, CELL), 2)
    # Draw food
    fx, fy = env.food
    pygame.draw.rect(screen, (255,50,50), (fx*CELL, fy*CELL, CELL, CELL))
    pygame.draw.rect(screen, (120,0,0), (fx*CELL, fy*CELL, CELL, CELL), 2)
    # Draw score
    score_surf = font.render(f"Score: {env.get_score()}", True, (255,255,255))
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()
    clock.tick(20)

    if done:
        time.sleep(1)
        state = env.reset()
        direction = (1, 0)

pygame.quit() 