import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font("arial.ttf", 25)
# font = pygame.font.SysFont('arial', 25), this takes longer to load


# inherit using Enum to make it so there will be no type errors,
# i.e "r" or "right" or "R", but only Direction.RIGHT as the only way to type the direction
class Direction(Enum):
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    UP = 4


# reduce errors when storing coords for the snake, i.e using long lists to store coords
Point = namedtuple("Point", "x, y")

# const
BLOCK_SIZE = 20
SPEED = 500

WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN1 = (0, 100, 100)
GREEN2 = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)


class SnakeGame:
    def __init__(self, w=640, h=480) -> None:
        self.w = w
        self.h = h

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Pygame Snake")
        self.clock = pygame.time.Clock()

        self.reset()

    def _draw_grid(self):
        for x in range(0, self.w, BLOCK_SIZE):
            for y in range(0, self.h, BLOCK_SIZE):
                pygame.draw.rect(
                    self.display, BLUE, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE), 1
                )

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def _update_ui(self):
        self.display.fill(BLACK)
        self._draw_grid()

        for point in self.snake:
            pygame.draw.rect(
                self.display,
                GREEN1,
                pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE),
            )
            # draw double squares with different colors to create depth
            pygame.draw.rect(
                self.display, GREEN2, pygame.Rect(point.x + 4, point.y + 4, 12, 12)
            )

        pygame.draw.rect(
            self.display,
            RED,
            pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE),
        )

        text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(text, (0, 0))
        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]

        directions = list(Direction)
        idx = directions.index(self.direction)

        # TODO: why the need to check if snek go straight
        if np.array_equal(action, [1, 0, 0]):
            new_dir = self.direction
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = directions[next_idx]  # turn right r -> d -> l -> u
        else:  # [0, 0, 1]
            prev_idx = (idx - 1) % 4
            new_dir = directions[prev_idx]  # turn left r -> u -> l -> d

        self.direction = new_dir

        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        if self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        if self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        if self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def reset(self):
        # init game state
        self._draw_grid()
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def is_collision(self, point=None):
        if point is None:
            point = self.head
        # hits boundary
        if (
            point.x > self.w - BLOCK_SIZE
            or point.x < 0
            or point.y > self.h - BLOCK_SIZE
            or point.y < 0
        ):
            return True

        # hit self
        if point in self.snake[1:]:
            return True

        return False

    def calculate_accessible_area(self):
        visited = set()
        stack = [self.head]
        accessible_area = 0

        while stack:
            current_point = stack.pop()

            if current_point in visited:
                continue

            visited.add(current_point)
            accessible_area += 1

            # Check neighboring points (up, down, left, right)
            neighbors = [
                Point(current_point.x + BLOCK_SIZE, current_point.y),
                Point(current_point.x - BLOCK_SIZE, current_point.y),
                Point(current_point.x, current_point.y + BLOCK_SIZE),
                Point(current_point.x, current_point.y - BLOCK_SIZE),
            ]

            for neighbor in neighbors:
                if (
                    0 <= neighbor.x < self.w
                    and 0 <= neighbor.y < self.h
                    and neighbor not in visited
                    and neighbor not in self.snake
                ):
                    stack.append(neighbor)

        return accessible_area

    def calculate_accessible_area_percentage(self):
        total_spaces = (self.w / BLOCK_SIZE) * (self.h / BLOCK_SIZE)
        accessible_area = self.calculate_accessible_area()
        percentage = accessible_area / total_spaces
        if percentage > 0.8:
            return 1
        else:
            return 0

    def accessible_area_percentage(self):
        total_spaces = 0
        empty_spaces = 0
        # Check the surrounding 3x3 grid centered around the snake's head
        for i in range(-1, 2):
            for j in range(-1, 2):
                x = self.head.x + i * BLOCK_SIZE
                y = self.head.y + j * BLOCK_SIZE
        if 0 <= x < self.w and 0 <= y < self.h:
            total_spaces += 1
            # Check if the position is empty (not occupied by the snake's body)
            if Point(x, y) not in self.snake:
                empty_spaces += 1
        percentage = empty_spaces / total_spaces
        if percentage > 0.8:
            return 1
        else:
            return 0

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move snake
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update pygame ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and return score
        return reward, game_over, self.score
