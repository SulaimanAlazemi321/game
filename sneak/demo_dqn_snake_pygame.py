import pygame, time
from snake_env import SnakeEnv
from dqn_agent import DQNAgent
import torch

CELL = 24
GRID = 30
MODEL_PATH = "dqn_snake_final.pt"

# Set up environment and agent
env = SnakeEnv(GRID, GRID)
state_dim = len(env.get_state_vector())
n_actions = 4
agent = DQNAgent(state_dim, n_actions, device='cuda')
agent.load(MODEL_PATH)
agent.epsilon = 0.0  # Always greedy for demo

pygame.init()
screen = pygame.display.set_mode((GRID*CELL, GRID*CELL))
pygame.display.set_caption("DQN Snake Demo (GPU-trained)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28, bold=True)

state = env.reset()
state_vec = env.get_state_vector()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    action = agent.select_action(state_vec)
    _, _, done = env.step(action)
    state_vec = env.get_state_vector()

    # draw
    screen.fill((20,20,20))
    # Draw snake
    for i, (x,y) in enumerate(env.snake):
        color = (0,180,0) if i > 0 else (0,255,0)  # Head brighter
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
    clock.tick(18)

    if done:
        time.sleep(1)
        state = env.reset()
        state_vec = env.get_state_vector()

pygame.quit() 