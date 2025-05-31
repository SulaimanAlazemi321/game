import os
import random
import pickle
from collections import defaultdict
from typing import Tuple, List

# The grid size should match the main game. These will be overwritten by practice.py when imported there,
# but we provide sane defaults for standalone training.
GRID_WIDTH = 40
GRID_HEIGHT = 30

# Actions are relative to the current heading: 0 = straight, 1 = right turn, 2 = left turn
ACTIONS = (0, 1, 2)
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # R, D, L, U

def turn(current_dir: Tuple[int, int], action: int) -> Tuple[int, int]:
    """Return the new absolute direction after taking a relative action."""
    idx = DIRECTIONS.index(current_dir)
    if action == 0:  # straight
        return current_dir
    elif action == 1:  # right turn
        return DIRECTIONS[(idx + 1) % 4]
    else:  # left turn
        return DIRECTIONS[(idx - 1) % 4]


def danger_ahead(snake: List[Tuple[int, int]], obstacles, direction: Tuple[int, int]) -> bool:
    head_x, head_y = snake[0]
    nx, ny = head_x + direction[0], head_y + direction[1]
    return (
        nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT or (nx, ny) in snake or (nx, ny) in obstacles
    )


def food_direction(head: Tuple[int, int], food: Tuple[int, int]) -> Tuple[int, int]:
    return (int(food[0] > head[0]) - int(food[0] < head[0]), int(food[1] > head[1]) - int(food[1] < head[1]))


class QLearningAgent:
    """Tabular Q-learning agent for Snake."""

    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, model_path="qtable.pkl"):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model_path = model_path
        self.q = defaultdict(lambda: [0.0, 0.0, 0.0])  # state -> action values
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.q = pickle.load(f)
                    self.epsilon = self.epsilon_min  # start exploiting immediately after loading
            except Exception:
                pass

    def _state_key(self, state_tuple):
        return tuple(state_tuple)

    def get_action(self, state):
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        key = self._state_key(state)
        values = self.q[key]
        max_val = max(values)
        best_actions = [a for a, v in enumerate(values) if v == max_val]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done=False):
        key = self._state_key(state)
        next_key = self._state_key(next_state)
        predict = self.q[key][action]
        target = reward + (0 if done else self.gamma * max(self.q[next_key]))
        self.q[key][action] += self.alpha * (target - predict)
        if done and self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self):
        with open(self.model_path, "wb") as f:
            pickle.dump(self.q, f)

    # ------------- state representation helpers -------------
    def build_state(self, snake, food, obstacles, direction):
        head = snake[0]
        left_dir = turn(direction, 2)
        right_dir = turn(direction, 1)

        state = [
            danger_ahead(snake, obstacles, direction),  # danger straight
            danger_ahead(snake, obstacles, right_dir),  # danger right
            danger_ahead(snake, obstacles, left_dir),  # danger left
            direction == (1, 0),  # moving right
            direction == (0, 1),  # moving down
            direction == (-1, 0),  # moving left
            direction == (0, -1),  # moving up
        ]

        fx, fy = food_direction(head, food)
        state.extend([fx == -1, fx == 1, fy == -1, fy == 1])  # food left/right/up/down
        return tuple(int(x) for x in state) 