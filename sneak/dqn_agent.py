import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

# Simple MLP for Q-value approximation
class DQNNet(nn.Module):
    def __init__(self, state_dim, n_actions, hidden_dim=512):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions)
        )
    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, state_dim, n_actions, device=None, gamma=0.99, lr=1e-3, batch_size=64, buffer_size=100_000, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.9995, hidden_dim=512, train_loops=1):
        self.n_actions = n_actions
        self.state_dim = state_dim
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.gamma = gamma
        self.batch_size = batch_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=buffer_size)
        self.policy_net = DQNNet(state_dim, n_actions, hidden_dim=hidden_dim).to(self.device)
        self.target_net = DQNNet(state_dim, n_actions, hidden_dim=hidden_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.steps = 0
        self.update_target_every = 2000
        self.train_loops = train_loops

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_actions)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            qvals = self.policy_net(state)
        return int(torch.argmax(qvals, dim=1).item())

    def store(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def sample(self):
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states), np.array(actions), np.array(rewards, dtype=np.float32), np.array(next_states), np.array(dones, dtype=np.float32))

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return

        for _ in range(self.train_loops):
            states, actions, rewards, next_states, dones = self.sample()
            states      = torch.FloatTensor(states).to(self.device)
            actions     = torch.LongTensor(actions).unsqueeze(1).to(self.device)
            rewards     = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
            next_states = torch.FloatTensor(next_states).to(self.device)
            dones       = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

            q_values = self.policy_net(states).gather(1, actions)
            with torch.no_grad():
                q_next = self.target_net(next_states).max(1, keepdim=True)[0]
                q_target = rewards + self.gamma * q_next * (1 - dones)
            loss = nn.functional.mse_loss(q_values, q_target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path):
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path):
        self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict()) 