import torch
import random
import os.path
import json
import numpy as np
from collections import deque
from game import SnakeGame, Direction, Point
from model import Linear_QNet, QTrainer
from plotter import plot

# const
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self, file_name="n_games.json") -> None:
        # declaring variables to use (Deep) Q Learning
        self.model = Linear_QNet(
            12, 256, 3
        )  # 11 for amount of states, 3 for move action

        self.data = {
            "n_games": 0,
            "record": 0,
            "total_score": 0,
        }

        self.file_name = os.path.join(self.model.model_folder_path, file_name)
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as f:
                data = json.load(f)
                self.n_games = data["n_games"]
                self.record = data["record"]
                self.total_score = data["total_score"]
        else:
            self.n_games = 0
            self.record = 0
            self.total_score = 0

        self.memory = deque(maxlen=MAX_MEMORY)  # if exceed max memory then popleft()
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate must be < than 1

        self.trainer = QTrainer(self.model, LR, self.gamma)

    def get_state(self, game):
        head = game.snake[0]

        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        over_80percent = game.calculate_accessible_area_percentage()

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # If percentage of empty space left is > 80% then be True
            over_80percent,
            # Danger straight
            (dir_r and game.is_collision(point_r))
            or (dir_l and game.is_collision(point_l))
            or (dir_u and game.is_collision(point_u))
            or (dir_d and game.is_collision(point_d)),
            # Danger right
            (dir_u and game.is_collision(point_r))
            or (dir_d and game.is_collision(point_l))
            or (dir_l and game.is_collision(point_u))
            or (dir_r and game.is_collision(point_d)),
            # Danger left
            (dir_d and game.is_collision(point_r))
            or (dir_u and game.is_collision(point_l))
            or (dir_r and game.is_collision(point_u))
            or (dir_l and game.is_collision(point_d)),
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            # Food location
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y,  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as f:
                data = json.load(f)
            data["n_games"] = self.n_games
            data["record"] = self.record
            data["total_score"] = self.total_score
            with open(self.file_name, "w") as f:
                json.dump(data, f)
        else:
            with open(self.file_name, "w") as f:
                json.dump(self.data, f)
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)  # returns list of tuples
        else:
            sample = self.memory

        states, actions, rewards, next_states, dones = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration/exploitation
        self.epsilon = 80 - self.n_games  # play with this
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    agent = Agent()
    game = SnakeGame()
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory (replay memory / experience replay)
            game.reset()
            agent.n_games += 1

            agent.train_long_memory()

            if score > agent.record:
                agent.record = score
                agent.model.save()

            print(f"Game {agent.n_games}, Score {score}, Record: {agent.record}")

            plot_scores.append(score)
            agent.total_score += score
            mean_score = agent.total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, agent.n_games)


if __name__ == "__main__":
    train()
