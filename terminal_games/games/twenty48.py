"""2048 - Slide and merge tiles to reach 2048! 🎯

Controls:
    ← → ↑ ↓   Slide tiles (or WASD)
    r          Restart game
    q          Quit to menu
"""

import random
from typing import Optional

from blessed import Terminal

# Board size
BOARD_SIZE = 4
CELL_WIDTH = 8  # Characters wide per cell
CELL_HEIGHT = 3  # Lines tall per cell

# Tile colors — background colors for each tile value
TILE_STYLES = {
    0: ("black", "bright_black"),       # empty
    2: ("black", "white"),
    4: ("black", "bright_white"),
    8: ("white", "bright_yellow"),
    16: ("white", "yellow"),
    32: ("white", "bright_red"),
    64: ("white", "red"),
    128: ("black", "bright_cyan"),
    256: ("black", "cyan"),
    512: ("black", "bright_green"),
    1024: ("black", "green"),
    2048: ("black", "bright_magenta"),
    4096: ("white", "magenta"),
    8192: ("white", "blue"),
}

# Winning tile
WIN_TILE = 2048


class Game2048:
    """The 2048 game engine."""

    def __init__(self):
        self.board: list[list[int]] = [
            [0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.won = False
        self.keep_playing = False  # Continue after reaching 2048
        self.moves = 0

        # Spawn two initial tiles
        self._spawn_tile()
        self._spawn_tile()

    @property
    def highest_tile(self) -> int:
        """Get the highest tile value on the board."""
        return max(max(row) for row in self.board)

    def _get_empty_cells(self) -> list[tuple[int, int]]:
        """Get all empty cell positions."""
        empty = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 0:
                    empty.append((r, c))
        return empty

    def _spawn_tile(self) -> None:
        """Spawn a new tile (90% chance of 2, 10% chance of 4) on a random empty cell."""
        empty = self._get_empty_cells()
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

    def _slide_row_left(self, row: list[int]) -> tuple[list[int], int]:
        """Slide a single row to the left, merging tiles. Returns (new_row, points_scored)."""
        # Remove zeros
        non_zero = [x for x in row if x != 0]
        score = 0

        # Merge adjacent equal tiles
        merged: list[int] = []
        skip = False
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_val = non_zero[i] * 2
                merged.append(merged_val)
                score += merged_val
                skip = True
            else:
                merged.append(non_zero[i])

        # Pad with zeros
        while len(merged) < BOARD_SIZE:
            merged.append(0)

        return merged, score

    def _rotate_board_clockwise(self) -> None:
        """Rotate the board 90 degrees clockwise."""
        self.board = [
            [self.board[BOARD_SIZE - 1 - c][r] for c in range(BOARD_SIZE)]
            for r in range(BOARD_SIZE)
        ]

    def _rotate_board_counter_clockwise(self) -> None:
        """Rotate the board 90 degrees counter-clockwise."""
        self.board = [
            [self.board[c][BOARD_SIZE - 1 - r] for c in range(BOARD_SIZE)]
            for r in range(BOARD_SIZE)
        ]

    def move(self, direction: str) -> bool:
        """
        Execute a move in the given direction.
        Returns True if the board changed (valid move).
        Direction: 'left', 'right', 'up', 'down'
        """
        if self.game_over:
            return False

        # Save board state to check if move changed anything
        old_board = [row[:] for row in self.board]

        # Rotate board so we always slide left, then rotate back
        if direction == "right":
            # Rotate 180 degrees
            self._rotate_board_clockwise()
            self._rotate_board_clockwise()
        elif direction == "up":
            self._rotate_board_counter_clockwise()
        elif direction == "down":
            self._rotate_board_clockwise()

        # Slide all rows left
        total_score = 0
        for r in range(BOARD_SIZE):
            new_row, points = self._slide_row_left(self.board[r])
            self.board[r] = new_row
            total_score += points

        # Rotate back
        if direction == "right":
            self._rotate_board_clockwise()
            self._rotate_board_clockwise()
        elif direction == "up":
            self._rotate_board_clockwise()
        elif direction == "down":
            self._rotate_board_counter_clockwise()

        # Check if board changed
        if self.board == old_board:
            return False  # Invalid move, nothing changed

        # Update score
        self.score += total_score
        if self.score > self.best_score:
            self.best_score = self.score

        self.moves += 1

        # Spawn a new tile
        self._spawn_tile()

        # Check win condition
        if not self.won and not self.keep_playing:
            if self.highest_tile >= WIN_TILE:
                self.won = True

        # Check game over
        if not self._has_valid_moves():
            self.game_over = True

        return True

    def _has_valid_moves(self) -> bool:
        """Check if any valid moves remain."""
        # Check for empty cells
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 0:
                    return True

        # Check for adjacent equal tiles (horizontal)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE - 1):
                if self.board[r][c] == self.board[r][c + 1]:
                    return True

        # Check for adjacent equal tiles (vertical)
        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == self.board[r + 1][c]:
                    return True

        return False

    def continue_playing(self) -> None:
        """Continue playing after reaching 2048."""
        self.won = False
        self.keep_playing = True


def get_tile_style(term: Terminal, value: int) -> tuple[str, str]:
    """Get foreground and background styling for a tile value."""
    fg_name, bg_name = TILE_STYLES.get(value, ("white", "bright_magenta"))

    fg = getattr(term, fg_name, term.white)
    bg_attr = f"on_{bg_name}"
    bg = getattr(term, bg_attr, term.on_bright_black)

    return fg, bg


def format_tile_text(value: int) -> str:
    """Format the tile number to fit within CELL_WIDTH."""
    if value == 0:
        return " " * CELL_WIDTH
    text = str(value)
    return text.center(CELL_WIDTH)


def draw_game(term: Terminal, game: Game2048) -> None:
    """Render the full game state to the terminal."""
    output = []
    output.append(term.home + term.clear)

    # Calculate board dimensions
    board_pixel_width = BOARD_SIZE * CELL_WIDTH + BOARD_SIZE + 1  # cells + borders
    board_pixel_height = BOARD_SIZE * CELL_HEIGHT + BOARD_SIZE + 1

    # Center everything
    total_width = board_pixel_width + 2
    start_x = max(0, (term.width - total_width) // 2)
    start_y = max(0, (term.height - board_pixel_height - 10) // 2)

    # Title
    title = "🎯  2 0 4 8  🎯"
    title_x = start_x + (total_width - len(title)) // 2
    output.append(
        term.move_xy(title_x, start_y)
        + term.bold + term.bright_yellow + title + term.normal
    )

    # Score section
    score_y = start_y + 2

    # Score box
    score_box_width = (board_pixel_width - 2) // 2
    best_box_x = start_x + 1 + score_box_width + 2

    # Score
    score_label = "SCORE"
    score_val = str(game.score)
    output.append(
        term.move_xy(start_x + 1, score_y)
        + term.bold + term.white + "┌" + "─" * score_box_width + "┐" + term.normal
    )
    output.append(
        term.move_xy(start_x + 1, score_y + 1)
        + term.bold + term.white + "│" + term.normal
        + term.dim + score_label.center(score_box_width) + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(start_x + 1, score_y + 2)
        + term.bold + term.white + "│" + term.normal
        + term.bold + term.bright_white + score_val.center(score_box_width) + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(start_x + 1, score_y + 3)
        + term.bold + term.white + "└" + "─" * score_box_width + "┘" + term.normal
    )

    # Best score
    best_label = "BEST"
    best_val = str(game.best_score)
    output.append(
        term.move_xy(best_box_x, score_y)
        + term.bold + term.white + "┌" + "─" * score_box_width + "┐" + term.normal
    )
    output.append(
        term.move_xy(best_box_x, score_y + 1)
        + term.bold + term.white + "│" + term.normal
        + term.dim + best_label.center(score_box_width) + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(best_box_x, score_y + 2)
        + term.bold + term.white + "│" + term.normal
        + term.bold + term.bright_yellow + best_val.center(score_box_width) + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(best_box_x, score_y + 3)
        + term.bold + term.white + "└" + "─" * score_box_width + "┘" + term.normal
    )

    # Board
    board_y = score_y + 5
    board_x = start_x + 1

    # Draw the grid
    for r in range(BOARD_SIZE):
        cell_top_y = board_y + r * (CELL_HEIGHT + 1)

        # Horizontal separator
        separator = "+"
        for c in range(BOARD_SIZE):
            separator += "─" * CELL_WIDTH + "+"
        output.append(
            term.move_xy(board_x, cell_top_y)
            + term.bright_black + separator + term.normal
        )

        # Cell rows
        for line in range(CELL_HEIGHT):
            row_y = cell_top_y + 1 + line
            output.append(
                term.move_xy(board_x, row_y)
                + term.bright_black + "│" + term.normal
            )

            for c in range(BOARD_SIZE):
                value = game.board[r][c]
                fg, bg = get_tile_style(term, value)
                px = board_x + 1 + c * (CELL_WIDTH + 1)

                if line == CELL_HEIGHT // 2:
                    # Middle line — show the number
                    tile_text = format_tile_text(value)
                    if value == 0:
                        output.append(
                            term.move_xy(px, row_y)
                            + term.on_bright_black + " " * CELL_WIDTH + term.normal
                        )
                    else:
                        output.append(
                            term.move_xy(px, row_y)
                            + fg + bg + term.bold + tile_text + term.normal
                        )
                else:
                    # Top/bottom line — just background color
                    if value == 0:
                        output.append(
                            term.move_xy(px, row_y)
                            + term.on_bright_black + " " * CELL_WIDTH + term.normal
                        )
                    else:
                        output.append(
                            term.move_xy(px, row_y)
                            + bg + " " * CELL_WIDTH + term.normal
                        )

                output.append(
                    term.bright_black + "│" + term.normal
                )

    # Bottom border
    bottom_y = board_y + BOARD_SIZE * (CELL_HEIGHT + 1)
    bottom_separator = "+"
    for c in range(BOARD_SIZE):
        bottom_separator += "─" * CELL_WIDTH + "+"
    output.append(
        term.move_xy(board_x, bottom_y)
        + term.bright_black + bottom_separator + term.normal
    )

    # Stats
    stats_y = bottom_y + 2
    moves_text = f"Moves: {game.moves}"
    highest_text = f"Highest: {game.highest_tile}"
    output.append(
        term.move_xy(board_x, stats_y)
        + term.dim + moves_text + term.normal
    )
    output.append(
        term.move_xy(board_x + board_pixel_width - len(highest_text), stats_y)
        + term.dim + highest_text + term.normal
    )

    # Controls
    controls_y = stats_y + 2
    output.append(
        term.move_xy(board_x, controls_y)
        + term.dim + "← → ↑ ↓  Slide tiles" + term.normal
    )
    output.append(
        term.move_xy(board_x, controls_y + 1)
        + term.dim + "W A S D   Slide tiles" + term.normal
    )
    output.append(
        term.move_xy(board_x, controls_y + 2)
        + term.dim + "   r      Restart" + term.normal
    )
    output.append(
        term.move_xy(board_x, controls_y + 3)
        + term.dim + "   q      Quit" + term.normal
    )

    # Win overlay
    if game.won and not game.keep_playing:
        overlay_width = 34
        ox = start_x + (total_width - overlay_width) // 2
        oy = board_y + (board_pixel_height // 2) - 3

        lines = [
            "                                  ",
            "   🎉  Y O U   R E A C H E D     ",
            "          2 0 4 8 !               ",
            "                                  ",
            "   c: Keep Playing   r: Restart   ",
            "          q: Quit Menu            ",
            "                                  ",
        ]

        for i, line in enumerate(lines):
            display_line = line[:overlay_width].ljust(overlay_width)
            output.append(
                term.move_xy(ox, oy + i)
                + term.bold + term.black_on_bright_yellow + display_line + term.normal
            )

    # Game over overlay
    if game.game_over:
        overlay_width = 34
        ox = start_x + (total_width - overlay_width) // 2
        oy = board_y + (board_pixel_height // 2) - 4

        lines = [
            "                                  ",
            "      G A M E   O V E R !        ",
            "                                  ",
            f"   Score: {game.score:<23} ",
            f"   Best:  {game.best_score:<23} ",
            f"   Moves: {game.moves:<23} ",
            f"   Best Tile: {game.highest_tile:<19} ",
            "                                  ",
            "     r: Restart   q: Quit Menu    ",
            "                                  ",
        ]

        for i, line in enumerate(lines):
            display_line = line[:overlay_width].ljust(overlay_width)
            output.append(
                term.move_xy(ox, oy + i)
                + term.bold + term.white_on_red + display_line + term.normal
            )

    # Write everything at once
    print("".join(output), end="", flush=True)


def play_twenty48(term: Terminal) -> None:
    """Main 2048 game loop."""
    game = Game2048()

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game)

        while True:
            key = term.inkey(timeout=None)

            if key == "q" or key.name == "KEY_ESCAPE":
                return  # Back to menu

            if key == "r":
                best = game.best_score
                game = Game2048()
                game.best_score = best
                draw_game(term, game)
                continue

            # Handle win screen
            if game.won and not game.keep_playing:
                if key == "c":
                    game.continue_playing()
                    draw_game(term, game)
                continue

            if game.game_over:
                continue

            # Direction input
            moved = False
            if key.name == "KEY_LEFT" or key == "a":
                moved = game.move("left")
            elif key.name == "KEY_RIGHT" or key == "d":
                moved = game.move("right")
            elif key.name == "KEY_UP" or key == "w":
                moved = game.move("up")
            elif key.name == "KEY_DOWN" or key == "s":
                moved = game.move("down")

            if moved:
                draw_game(term, game)
