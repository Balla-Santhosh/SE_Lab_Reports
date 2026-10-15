"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.
"""

import random

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import (
    GRID_COLS, GRID_ROWS, GOAL_ROW, ROAD_ROWS, START_ROW, CELL_SIZE, WIDTH, HEIGHT,
)

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]   # one entry per road row, alternating direction

MAX_LIVES = 3
HIT_DURATION_MS = 500
TIME_LIMIT_MS = 30000


class GameEngine:
    def __init__(self):
        self._build_entities()

    def _build_entities(self):
        self.lives = MAX_LIVES
        self.score = 0
        self.state = "playing"      # "playing", "hit", "game_over", or "won"
        self.hit_until = 0
        self._start_attempt()

        start_col = GRID_COLS // 2
        self.frog = Frog(
            col=start_col, row=START_ROW,
            start_col=start_col, start_row=START_ROW,
            cols=GRID_COLS, start_row_limit=START_ROW,
        )
        frog_x_range = (start_col * CELL_SIZE, start_col * CELL_SIZE + CELL_SIZE)

        self.vehicles = []
        for i, row in enumerate(ROAD_ROWS):
            speed = LANE_SPEEDS[i % len(LANE_SPEEDS)]
            vehicle_width = 40 if i % 2 == 0 else 70   # mix of cars and wider trucks
            spacing = 300
            count = 2

            # Try a few random phases and keep the first one that doesn't
            # already overlap the frog's starting column.
            for _attempt in range(20):
                phase = random.randint(0, spacing - 1)
                positions = []
                safe = True
                for n in range(count):
                    offset = phase + n * spacing
                    x = offset if speed > 0 else WIDTH - offset - vehicle_width
                    positions.append(x)
                    if not (x + vehicle_width <= frog_x_range[0] or x >= frog_x_range[1]):
                        safe = False
                if safe:
                    break

            for x in positions:
                self.vehicles.append(Vehicle(x=x, row=row, width=vehicle_width,
                                              height=CELL_SIZE - 8, speed=speed))

    def _start_attempt(self):
        """Start (or restart) the 30-second clock for a new attempt."""
        self.attempt_start = pygame.time.get_ticks()
        self.time_left_ms = TIME_LIMIT_MS

    def _lose_life(self):
        """Shared by collisions and timeouts: costs a life, then hit effect or game over."""
        self.lives -= 1
        if self.lives <= 0:
            self.state = "game_over"
        else:
            self.state = "hit"
            self.hit_until = pygame.time.get_ticks() + HIT_DURATION_MS

    def handle_keydown(self, key):
        if key == pygame.K_r:
            self._build_entities()
            return
        if self.state != "playing":
            return          # no movement during the hit effect, after game over, or after a win
        if key == pygame.K_UP:
            self.frog.move(0, -1)
        elif key == pygame.K_DOWN:
            self.frog.move(0, 1)
        elif key == pygame.K_LEFT:
            self.frog.move(-1, 0)
        elif key == pygame.K_RIGHT:
            self.frog.move(1, 0)

    def update(self):
        if self.state in ("game_over", "won"):
            return

        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        if self.state == "hit":
            if pygame.time.get_ticks() >= self.hit_until:
                self.frog.reset()
                self.state = "playing"
                self._start_attempt()      # fresh 30 seconds for the new attempt
            return

        # state == "playing"
        if check_collision(self.frog, self.vehicles):
            self._lose_life()
            return

        if self.frog.row == GOAL_ROW:      # checked before the timer: a win counts at any time left
            self.score += 100
            self.state = "won"
            return

        elapsed = pygame.time.get_ticks() - self.attempt_start
        self.time_left_ms = max(0, TIME_LIMIT_MS - elapsed)
        if self.time_left_ms <= 0:
            self._lose_life()              # timeout is a real failure, same as a hit

    def draw(self, surface, font):
        from game import renderer
        frog_color = renderer.COLOR_HIT if self.state in ("hit", "game_over") else renderer.COLOR_FROG
        renderer.draw_scene(surface, self.frog, self.vehicles, frog_color)
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 10))
        renderer.draw_text(surface, font, f"Time: {self.time_left_ms // 1000 + (1 if self.time_left_ms % 1000 else 0)}s",
                           (WIDTH // 2 - 40, 10))
        renderer.draw_text(surface, font, f"Score: {self.score}", (WIDTH - 130, 10))
        renderer.draw_text(surface, font, "Arrow keys to move. R to restart.", (10, HEIGHT - 24))
        if self.state == "game_over":
            renderer.draw_banner(surface, font, "Game Over - press R to restart")
        elif self.state == "won":
            renderer.draw_banner(surface, font, "You Won! - press R to restart")