import numpy as np
from collections import defaultdict
from functools import partial


def zeros_action(n=4):
    """Factory that returns a zero-initialised Q-vector of length *n*."""
    return np.zeros(n, dtype=np.float32)


class QLearningAgent:
    """Simple tabular Q-learning agent (CPU-only)."""

    def __init__(self,
                 n_actions: int = 4,
                 alpha: float = 0.1,
                 gamma: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.02,
                 epsilon_decay: float = 0.9995):
        self.n_actions = n_actions
        self.q_table = defaultdict(partial(zeros_action, n=self.n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    # --------------------------------------------------
    # Core API
    # --------------------------------------------------
    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_actions)
        return int(np.argmax(self.q_table[state]))

    def update(self, state, action, reward, next_state, done):
        q_sa = self.q_table[state][action]
        q_next = np.max(self.q_table[next_state]) if not done else 0.0
        self.q_table[state][action] += self.alpha * (reward + self.gamma * q_next - q_sa)

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # --------------------------------------------------
    # Persistence helpers
    # --------------------------------------------------
    def save(self, path: str):
        import pickle, pathlib
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str):
        import pickle
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError("Loaded object is not a QLearningAgent instance")
        return obj
