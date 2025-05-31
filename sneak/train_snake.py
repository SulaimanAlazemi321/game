from snake_env import SnakeEnv
#from q_learning_agent import QLearningAgent
from dqn_agent import DQNAgent
import numpy as np


# --------------------------------------------------
# Hyper-parameters
# --------------------------------------------------
GRID_SIZE = 20     # Width and height of the square grid
N_ENVS   = 400      # More parallel environments
EPISODES = 10_000   # Total training episodes (DQN learns faster)

# DQN-specific
BATCH_SIZE = 4096
BUFFER_SIZE = 1_000_000


# --------------------------------------------------
# Environment & agent setup
# --------------------------------------------------
envs  = [SnakeEnv(GRID_SIZE, GRID_SIZE) for _ in range(N_ENVS)]
state_dim = len(envs[0].get_state_vector())
n_actions = 4
agent = DQNAgent(state_dim, n_actions, batch_size=BATCH_SIZE, buffer_size=BUFFER_SIZE, device='cuda', hidden_dim=512, train_loops=4)


# --------------------------------------------------
# Training loop (DQN)
# --------------------------------------------------
for episode in range(EPISODES):
    states     = [env.reset() for env in envs]
    state_vecs = [env.get_state_vector() for env in envs]
    done_flags = [False] * N_ENVS
    total_reward = 0
    steps = 0
    max_steps = 200  # Faster episodes for debugging

    print(f"Starting episode {episode}")
    while not all(done_flags) and steps < max_steps:
        actions = [agent.select_action(state_vecs[i]) if not done_flags[i] else 0 for i in range(N_ENVS)]
        for i, env in enumerate(envs):
            if done_flags[i]:
                continue
            next_state, reward, done = env.step(actions[i])
            next_state_vec = env.get_state_vector()
            agent.store(state_vecs[i], actions[i], reward, next_state_vec, done)
            state_vecs[i] = next_state_vec
            done_flags[i] = done
            total_reward += reward
        agent.train_step()
        steps += 1
        if steps % 20 == 0:
            print(f"  Step {steps}: {sum(done_flags)} of {N_ENVS} environments done.")
    print(f"Episode {episode} finished after {steps} steps. All done: {all(done_flags)}")

    if episode % 100 == 0:
        mean_score = np.mean([env.get_score() for env in envs])
        print(f"Episode {episode:5d} | ε = {agent.epsilon:.3f} | mean score = {mean_score:.2f}")
    if episode % 1000 == 0 and episode > 0:
        agent.save(f"dqn_snake_ep{episode}.pt")

# Save final model
agent.save("dqn_snake_final.pt")
