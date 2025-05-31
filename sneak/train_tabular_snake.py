from snake_env import SnakeEnv
from q_learning_agent import QLearningAgent
import numpy as np

# --------------------------------------------------
# Hyper-parameters tuned for overnight training
# --------------------------------------------------
GRID_SIZE   = 20      # Larger board for more challenge
N_ENVS      = 500    # Maximize CPU parallelism
EPISODES    = 10_000  # More episodes for better learning
MAX_STEPS   = 20000     # Allow longer games

# Q-learning params (tuned for near-perfection)
ALPHA       = 0.1
GAMMA       = 0.99
EPS_DECAY   = 0.9999
EPS_MIN     = 0.001

# --------------------------------------------------
# Setup
# --------------------------------------------------
print("Initialising environments…")
envs   = [SnakeEnv(GRID_SIZE, GRID_SIZE) for _ in range(N_ENVS)]
agent = QLearningAgent(alpha=ALPHA, gamma=GAMMA, epsilon_decay=EPS_DECAY, epsilon_min=EPS_MIN)

# --------------------------------------------------
# Training loop
# --------------------------------------------------
for episode in range(EPISODES):
    states     = [env.reset() for env in envs]
    done_flags = [False] * N_ENVS
    steps = 0

    while not all(done_flags) and steps < MAX_STEPS:
        actions = [agent.select_action(states[i]) if not done_flags[i] else 0 for i in range(N_ENVS)]
        for i, env in enumerate(envs):
            if done_flags[i]:
                continue
            next_state, reward, done = env.step(actions[i])
            agent.update(states[i], actions[i], reward, next_state, done)
            states[i]   = next_state
            done_flags[i] = done
        steps += 1
    agent.decay_epsilon()

    if episode % 200 == 0:
        mean_score = np.mean([env.get_score() for env in envs])
        print(f"Episode {episode:5d} | ε = {agent.epsilon:.3f} | mean score = {mean_score:.2f}")

print("Training complete. Saving agent…")
agent.save("snake_q_agent_large.pkl")
print("Saved -> snake_q_agent_large.pkl") 