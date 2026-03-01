"""Snake - Classic snake game 🐍

Controls:
    ← → ↑ ↓   Move snake (or WASD)
    p          Pause
    q          Quit to menu
"""

import random
import time
from collections import deque
from typing import Optional

from blessed import Terminal

# Game constants
MIN_BOARD_WIDTH = 30
MIN_BOARD_HEIGHT = 15
CELL_WIDTH = 2  # Each cell is 2 characters wide for a square look

# Directions as (row_delta, col_delta)
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

# Direction opposites (can't reverse into yourself)
OPPOSITES = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

# Speed settings (seconds between moves)
INITIAL_SPEED = 0.15
MIN_SPEED = 0.05
SPEED_DECREASE_PER_FOOD = 0.002

# Food types
FOOD_NORMAL = "normal"
FOOD_BONUS = "bonus"

FOOD_CHARS = {
    FOOD_NORMAL: "●",
    FOOD_BONUS: "★",
}

FOOD_POINTS = {
    FOOD_NORMAL: 10,
    FOOD_BONUS: 50,
}

BONUS_FOOD_CHANCE = 0.15  # 15% chance of bonus food
BONUS_FOOD_LIFETIME = 30  # Bonus food disappears after 30 ticks


class Food:
    """Represents a food item on the board."""

    def __init__(self, row: int, col: int, food_type: str = FOOD_NORMAL):
        self.row = row
        self.col = col
        self.food_type = food_type
        self.ticks_remaining: Optional[int] = None
        if food_type == FOOD_BONUS:
            self.ticks_remaining = BONUS_FOOD_LIFETIME


class SnakeGame:
    """The Snake game engine."""

    def __init__(self, board_width: int, board_height: int):
        self.board_width = board_width
        self.board_height = board_height

        # Snake starts in the middle going right
        mid_row = board_height // 2
        mid_col = board_width // 2
        self.snake: deque[tuple[int, int]] = deque([
            (mid_row, mid_col),
            (mid_row, mid_col - 1),
            (mid_row, mid_col - 2),
        ])
        self.direction = RIGHT
        self.next_direction = RIGHT

        # Game state
        self.score = 0
        self.high_score = 0
        self.food: list[Food] = []
        self.game_over = False
        self.paused = False
        self.grow_pending = 0

        # Timing
        self.speed = INITIAL_SPEED
        self.last_move_time = time.time()
        self.tick_count = 0

        # Stats
        self.foods_eaten = 0
        self.bonus_eaten = 0
        self.total_moves = 0

        # Place initial food
        self._spawn_food()

    def _get_empty_cells(self) -> list[tuple[int, int]]:
        """Get all empty cells on the board."""
        snake_set = set(self.snake)
        food_set = {(f.row, f.col) for f in self.food}
        occupied = snake_set | food_set
        empty = []
        for r in range(self.board_height):
            for c in range(self.board_width):
                if (r, c) not in occupied:
                    empty.append((r, c))
        return empty

    def _spawn_food(self) -> None:
        """Spawn a new food item on a random empty cell."""
        empty = self._get_empty_cells()
        if not empty:
            return  # Board is full (you basically won!)

        row, col = random.choice(empty)

        # Decide food type
        if random.random() < BONUS_FOOD_CHANCE and self.foods_eaten > 0:
            food_type = FOOD_BONUS
        else:
            food_type = FOOD_NORMAL

        self.food.append(Food(row, col, food_type))

    def set_direction(self, new_direction: tuple[int, int]) -> None:
        """Set the next direction, preventing 180-degree turns."""
        if new_direction != OPPOSITES.get(self.direction):
            self.next_direction = new_direction

    def tick(self) -> bool:
        """Process one game tick. Returns True if state changed."""
        if self.paused or self.game_over:
            return False

        now = time.time()
        if now - self.last_move_time < self.speed:
            return False

        self.last_move_time = now
        self.tick_count += 1
        self.total_moves += 1

        # Apply direction
        self.direction = self.next_direction

        # Calculate new head position
        head_r, head_c = self.snake[0]
        dr, dc = self.direction
        new_r = head_r + dr
        new_c = head_c + dc

        # Check wall collision
        if new_r < 0 or new_r >= self.board_height or new_c < 0 or new_c >= self.board_width:
            self.game_over = True
            return True

        # Check self collision (exclude tail if not growing, as it will move)
        collision_body = set(list(self.snake)[:-1]) if self.grow_pending == 0 else set(self.snake)
        if (new_r, new_c) in collision_body:
            self.game_over = True
            return True

        # Move snake
        self.snake.appendleft((new_r, new_c))

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.snake.pop()

        # Check food collision
        eaten_food = None
        for food in self.food:
            if food.row == new_r and food.col == new_c:
                eaten_food = food
                break

        if eaten_food:
            self.food.remove(eaten_food)
            points = FOOD_POINTS[eaten_food.food_type]
            self.score += points
            self.foods_eaten += 1

            if eaten_food.food_type == FOOD_BONUS:
                self.bonus_eaten += 1
                self.grow_pending += 3  # Bonus food grows more
            else:
                self.grow_pending += 1

            # Speed up
            self.speed = max(MIN_SPEED, self.speed - SPEED_DECREASE_PER_FOOD)

            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score

            # Spawn new food
            self._spawn_food()

        # Update bonus food timers
        expired = []
        for food in self.food:
            if food.ticks_remaining is not None:
                food.ticks_remaining -= 1
                if food.ticks_remaining <= 0:
                    expired.append(food)

        for food in expired:
            self.food.remove(food)
            # Respawn regular food if no food left
            if not self.food:
                self._spawn_food()

        return True


def draw_game(term: Terminal, game: SnakeGame, start_x: int, start_y: int) -> None:
    """Render the full game state to the terminal."""
    output = []
    output.append(term.home + term.clear)

    board_pixel_width = game.board_width * CELL_WIDTH + 2  # +2 for borders
    sidebar_width = 22

    # Title
    title = "🐍  S N A K E  🐍"
    title_x = start_x + (board_pixel_width // 2) - len(title) // 2 + 2
    output.append(
        term.move_xy(title_x, start_y)
        + term.bold + term.green + title + term.normal
    )

    board_y = start_y + 2
    board_x = start_x + 2

    # Draw board border
    top_border = "╔" + "══" * game.board_width + "╗"
    output.append(
        term.move_xy(board_x, board_y)
        + term.white + top_border + term.normal
    )

    for r in range(game.board_height):
        # Left border
        output.append(
            term.move_xy(board_x, board_y + 1 + r)
            + term.white + "║" + term.normal
        )
        # Empty cells
        for c in range(game.board_width):
            px = board_x + 1 + c * CELL_WIDTH
            py = board_y + 1 + r
            output.append(term.move_xy(px, py) + "  ")
        # Right border
        output.append(
            term.move_xy(board_x + 1 + game.board_width * CELL_WIDTH, board_y + 1 + r)
            + term.white + "║" + term.normal
        )

    bottom_border = "╚" + "══" * game.board_width + "╝"
    output.append(
        term.move_xy(board_x, board_y + game.board_height + 1)
        + term.white + bottom_border + term.normal
    )

    # Draw food
    for food in game.food:
        px = board_x + 1 + food.col * CELL_WIDTH
        py = board_y + 1 + food.row
        char = FOOD_CHARS[food.food_type]

        if food.food_type == FOOD_BONUS:
            # Blinking effect for bonus food
            if food.ticks_remaining is not None and food.ticks_remaining < 10:
                if game.tick_count % 2 == 0:
                    color = term.bright_yellow
                else:
                    color = term.dim + term.yellow
            else:
                color = term.bright_yellow + term.bold
            output.append(
                term.move_xy(px, py) + color + char + " " + term.normal
            )
        else:
            output.append(
                term.move_xy(px, py) + term.bright_red + term.bold + char + " " + term.normal
            )

    # Draw snake
    snake_list = list(game.snake)
    for i, (r, c) in enumerate(snake_list):
        px = board_x + 1 + c * CELL_WIDTH
        py = board_y + 1 + r

        if i == 0:
            # Head
            # Choose head character based on direction
            if game.direction == UP:
                head = "▲ "
            elif game.direction == DOWN:
                head = "▼ "
            elif game.direction == LEFT:
                head = " ◀"
            else:
                head = "▶ "
            output.append(
                term.move_xy(px, py)
                + term.bold + term.bright_green + head + term.normal
            )
        else:
            # Body - gradient from bright to dim green
            if i < len(snake_list) * 0.3:
                color = term.bright_green + term.bold
            elif i < len(snake_list) * 0.7:
                color = term.green
            else:
                color = term.green + term.dim
            output.append(
                term.move_xy(px, py) + color + "██" + term.normal
            )

    # Sidebar
    sidebar_x = board_x + board_pixel_width + 3
    sidebar_y = board_y

    # Score box
    output.append(
        term.move_xy(sidebar_x, sidebar_y)
        + term.bold + term.white + "┌──────────────────┐" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 1)
        + term.bold + term.white + "│" + term.normal
        + term.bold + term.green + "     S C O R E     " + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    # Hack: recalculate with padding to fit inside the box
    score_display = f"{game.score}"
    score_line = score_display.center(18)
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 2)
        + term.bold + term.white + "│" + term.normal
        + term.bright_white + term.bold + score_line + term.normal
        + term.bold + term.white + " │" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 3)
        + term.bold + term.white + "└──────────────────┘" + term.normal
    )

    # High score
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 5)
        + term.dim + f"  Best: {game.high_score}" + term.normal
    )

    # Snake length
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 7)
        + term.bold + term.yellow + f"  Length: {len(game.snake)}" + term.normal
    )

    # Foods eaten
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 9)
        + term.bold + term.red + f"  Eaten: {game.foods_eaten}" + term.normal
    )

    # Speed indicator
    speed_pct = int((1 - (game.speed - MIN_SPEED) / (INITIAL_SPEED - MIN_SPEED)) * 100)
    speed_pct = max(0, min(100, speed_pct))
    bar_len = 10
    filled = int(bar_len * speed_pct / 100)
    speed_bar = "█" * filled + "░" * (bar_len - filled)
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 11)
        + term.bold + term.cyan + f"  Speed:" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 12)
        + term.cyan + f"  [{speed_bar}]" + term.normal
    )

    # Controls
    controls_y = sidebar_y + 14
    output.append(
        term.move_xy(sidebar_x, controls_y)
        + term.dim + "  ← → ↑ ↓  Move" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 1)
        + term.dim + "  W A S D   Move" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 2)
        + term.dim + "    p       Pause" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 3)
        + term.dim + "    q       Quit" + term.normal
    )

    # Pause overlay
    if game.paused:
        pause_text = "  ⏸  P A U S E D  ⏸  "
        px = start_x + (board_pixel_width + sidebar_width) // 2 - len(pause_text) // 2 + 2
        py = start_y + game.board_height // 2 + 2
        output.append(
            term.move_xy(px, py)
            + term.bold + term.black_on_yellow + pause_text + term.normal
        )
        resume_text = "  Press P to resume  "
        output.append(
            term.move_xy(px, py + 1)
            + term.dim + resume_text + term.normal
        )

    # Game over overlay
    if game.game_over:
        overlay_width = 28
        total = board_pixel_width + sidebar_width
        ox = start_x + (total - overlay_width) // 2 + 2
        oy = start_y + game.board_height // 2

        lines = [
            "                            ",
            "    G A M E   O V E R !     ",
            "                            ",
            f"  Score: {game.score:<18} ",
            f"  Length: {len(game.snake):<17} ",
            f"  Foods: {game.foods_eaten:<17} ",
            "                            ",
            "  r: Restart  q: Quit Menu  ",
            "                            ",
        ]

        for i, line in enumerate(lines):
            # Pad or trim to overlay_width
            display_line = line[:overlay_width].ljust(overlay_width)
            output.append(
                term.move_xy(ox, oy + i)
                + term.bold + term.white_on_red + display_line + term.normal
            )

    # Write everything at once
    print("".join(output), end="", flush=True)


def play_snake(term: Terminal) -> None:
    """Main Snake game loop."""
    # Calculate board size based on terminal dimensions
    max_board_w = (term.width - 30) // CELL_WIDTH - 2  # Leave room for sidebar
    max_board_h = term.height - 6  # Leave room for title and borders

    board_width = max(MIN_BOARD_WIDTH, min(max_board_w, 40))
    board_height = max(MIN_BOARD_HEIGHT, min(max_board_h, 20))

    game = SnakeGame(board_width, board_height)

    # Center the game
    board_pixel_width = board_width * CELL_WIDTH + 2
    sidebar_width = 22
    total_width = board_pixel_width + sidebar_width + 6
    start_x = max(0, (term.width - total_width) // 2)
    start_y = max(0, (term.height - board_height - 4) // 2)

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game, start_x, start_y)

        while True:
            # Handle input with short timeout for smooth gameplay
            key = term.inkey(timeout=0.02)

            if key:
                if key == "q" or key.name == "KEY_ESCAPE":
                    return  # Back to menu

                if game.game_over:
                    if key == "r":
                        game = SnakeGame(board_width, board_height)
                        draw_game(term, game, start_x, start_y)
                    continue

                if key == "p":
                    game.paused = not game.paused
                    if not game.paused:
                        game.last_move_time = time.time()  # Reset timer on unpause
                    draw_game(term, game, start_x, start_y)
                    continue

                if game.paused:
                    continue

                # Direction input
                if key.name == "KEY_UP" or key == "w":
                    game.set_direction(UP)
                elif key.name == "KEY_DOWN" or key == "s":
                    game.set_direction(DOWN)
                elif key.name == "KEY_LEFT" or key == "a":
                    game.set_direction(LEFT)
                elif key.name == "KEY_RIGHT" or key == "d":
                    game.set_direction(RIGHT)

            # Process game tick
            if not game.game_over and not game.paused:
                if game.tick():
                    draw_game(term, game, start_x, start_y)
