import random

class SnakeEnv:
    def __init__(self, grid_width=10, grid_height=10):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reset()

    def reset(self):
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)
        self.food = self._random_food()
        self.done = False
        self.score = 0
        return self._get_state()

    def _random_food(self):
        while True:
            pos = (random.randint(0, self.grid_width-1), random.randint(0, self.grid_height-1))
            if pos not in self.snake:
                return pos

    def step(self, action):
        if self.done:
            return self._get_state(), 0, True

        # Action: 0=Up, 1=Down, 2=Left, 3=Right
        dirs = [ (0,-1), (0,1), (-1,0), (1,0) ]
        new_direction = dirs[action]
        # Disallow 180-degree turns (they would lead to instant self-collision)
        if (new_direction[0] == -self.direction[0] and
            new_direction[1] == -self.direction[1]):
            new_direction = self.direction

        self.direction = new_direction

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # -------- Collision checks --------
        # 1. Wall collision
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.done = True
            return self._get_state(), -1, True

        # 2. Self-collision
        #    Moving into the current tail square is safe *unless* we are eating
        ate_food = (new_head == self.food)
        body_to_check = self.snake if ate_food else self.snake[:-1]
        if new_head in body_to_check:
            self.done = True
            return self._get_state(), -1, True

        # -------- State update --------
        self.snake.insert(0, new_head)

        if ate_food:
            self.food = self._random_food()
            self.score += 1
            reward = 1
        else:
            # Remove tail when not eating
            self.snake.pop()
            reward = 0

        return self._get_state(), reward, False

    def _get_state(self):
        head = self.snake[0]
        food = self.food
        # Discretize state (could be improved!)
        state = (
            head[0], head[1], food[0], food[1],
            self.direction[0], self.direction[1]
        )
        return state

    def get_score(self):
        return self.score

    def get_state_vector(self):
        """
        Returns a vector encoding of the state for neural networks:
        [head_x_norm, head_y_norm, food_x_norm, food_y_norm, dir_x, dir_y, danger_left, danger_straight, danger_right]
        All positions are normalized to [0,1]. Danger flags are 0/1.
        """
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        dir_x, dir_y = self.direction
        grid_w, grid_h = self.grid_width, self.grid_height

        # Normalized positions
        head_x_norm = head_x / (grid_w - 1)
        head_y_norm = head_y / (grid_h - 1)
        food_x_norm = food_x / (grid_w - 1)
        food_y_norm = food_y / (grid_h - 1)

        # Danger flags (left, straight, right)
        dirs = [(0,-1), (1,0), (0,1), (-1,0)] # Up, Right, Down, Left
        idx = dirs.index(self.direction)
        left = dirs[(idx-1)%4]
        right = dirs[(idx+1)%4]
        straight = self.direction

        def danger(offset):
            x, y = self.snake[0][0] + offset[0], self.snake[0][1] + offset[1]
            if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
                return 1.0
            if (x, y) in self.snake:
                return 1.0
            return 0.0

        danger_left = danger(left)
        danger_straight = danger(straight)
        danger_right = danger(right)

        return [
            head_x_norm, head_y_norm,
            food_x_norm, food_y_norm,
            float(dir_x), float(dir_y),
            danger_left, danger_straight, danger_right
        ]
