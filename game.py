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


if __name__ == "__main__":
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()

        # break if game over
        if game_over == True:
            break

    print(f"Final Score: {score}")
    pygame.quit()
