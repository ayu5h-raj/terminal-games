"""Tetris - Classic falling blocks game 🧱

Controls:
    ← →     Move piece left/right
    ↓       Soft drop
    ↑       Rotate piece
    Space   Hard drop
    p       Pause
    q       Quit to menu
"""

import random
import time
from typing import Optional

from blessed import Terminal

# Board dimensions
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_WIDTH = 2  # Each cell is 2 characters wide for a square look

# Tetromino shapes defined as (row, col) offsets for each rotation state
# fmt: off
TETROMINOES = {
    "I": [
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (1, 0), (2, 0), (3, 0)],
    ],
    "O": [
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
    ],
    "T": [
        [(0, 0), (0, 1), (0, 2), (1, 1)],
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
        [(0, 0), (1, 0), (2, 0), (1, -1)],
    ],
    "S": [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
    ],
    "Z": [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)],
    ],
    "L": [
        [(0, 0), (0, 1), (0, 2), (1, 0)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
    ],
    "J": [
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(2, 0), (0, 1), (1, 1), (2, 1)],
    ],
}
# fmt: on

# Colors for each piece type
PIECE_COLORS = {
    "I": "cyan",
    "O": "yellow",
    "T": "magenta",
    "S": "green",
    "Z": "red",
    "L": "orange",  # Will fallback to bright yellow
    "J": "blue",
}

# Scoring system (NES-style)
SCORE_TABLE = {
    0: 0,
    1: 100,
    2: 300,
    3: 500,
    4: 800,  # Tetris!
}

# Lines needed per level
LINES_PER_LEVEL = 10


class Piece:
    """Represents the currently active Tetris piece."""

    def __init__(self, shape_name: str):
        self.shape_name = shape_name
        self.rotation = 0
        self.row = 0
        self.col = BOARD_WIDTH // 2 - 1

    @property
    def blocks(self) -> list[tuple[int, int]]:
        """Get the current block positions as (row, col) on the board."""
        offsets = TETROMINOES[self.shape_name][self.rotation]
        return [(self.row + dr, self.col + dc) for dr, dc in offsets]

    def get_blocks_at(self, rotation: int, row: int, col: int) -> list[tuple[int, int]]:
        """Get block positions for a specific rotation and position."""
        offsets = TETROMINOES[self.shape_name][rotation]
        return [(row + dr, col + dc) for dr, dc in offsets]


class TetrisGame:
    """The Tetris game engine."""

    def __init__(self):
        self.board: list[list[Optional[str]]] = [
            [None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
        ]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False

        # Piece bag (7-bag randomizer for fair piece distribution)
        self.bag: list[str] = []
        self.current_piece = self._new_piece()
        self.next_piece = self._new_piece()

        # Timing
        self.last_drop_time = time.time()
        self.drop_interval = self._calc_drop_interval()

        # Stats
        self.total_pieces = 0
        self.tetris_count = 0

    def _fill_bag(self) -> None:
        """Fill the piece bag with one of each tetromino, shuffled."""
        self.bag = list(TETROMINOES.keys())
        random.shuffle(self.bag)

    def _new_piece(self) -> Piece:
        """Get a new piece from the bag."""
        if not self.bag:
            self._fill_bag()
        shape = self.bag.pop()
        return Piece(shape)

    def _calc_drop_interval(self) -> float:
        """Calculate drop speed based on level. Gets faster each level."""
        # NES-inspired speed curve
        return max(0.05, 0.8 - (self.level - 1) * 0.07)

    def is_valid_position(self, blocks: list[tuple[int, int]]) -> bool:
        """Check if a list of block positions is valid (in bounds and not colliding)."""
        for r, c in blocks:
            if c < 0 or c >= BOARD_WIDTH:
                return False
            if r >= BOARD_HEIGHT:
                return False
            if r < 0:
                continue  # Allow blocks above the board
            if self.board[r][c] is not None:
                return False
        return True

    def move(self, d_row: int, d_col: int) -> bool:
        """Try to move the current piece. Returns True if successful."""
        new_blocks = [
            (r + d_row, c + d_col) for r, c in self.current_piece.blocks
        ]
        if self.is_valid_position(new_blocks):
            self.current_piece.row += d_row
            self.current_piece.col += d_col
            return True
        return False

    def rotate(self) -> bool:
        """Try to rotate the current piece. Implements wall kicks."""
        piece = self.current_piece
        new_rotation = (piece.rotation + 1) % 4

        # Try normal rotation
        new_blocks = piece.get_blocks_at(new_rotation, piece.row, piece.col)
        if self.is_valid_position(new_blocks):
            piece.rotation = new_rotation
            return True

        # Wall kick: try shifting left, right, up
        for d_col, d_row in [(1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0)]:
            kicked_blocks = piece.get_blocks_at(
                new_rotation, piece.row + d_row, piece.col + d_col
            )
            if self.is_valid_position(kicked_blocks):
                piece.rotation = new_rotation
                piece.row += d_row
                piece.col += d_col
                return True

        return False

    def hard_drop(self) -> int:
        """Drop the piece all the way down instantly. Returns rows dropped."""
        rows = 0
        while self.move(1, 0):
            rows += 1
        self.score += rows * 2  # Bonus points for hard drop
        self.lock_piece()
        return rows

    def lock_piece(self) -> None:
        """Lock the current piece onto the board and spawn next piece."""
        for r, c in self.current_piece.blocks:
            if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
                self.board[r][c] = self.current_piece.shape_name

        self.total_pieces += 1

        # Clear completed lines
        lines = self._clear_lines()
        self.lines_cleared += lines

        if lines == 4:
            self.tetris_count += 1

        # Update score
        self.score += SCORE_TABLE.get(lines, 0) * self.level

        # Level up
        new_level = self.lines_cleared // LINES_PER_LEVEL + 1
        if new_level > self.level:
            self.level = new_level
            self.drop_interval = self._calc_drop_interval()

        # Spawn next piece
        self.current_piece = self.next_piece
        self.next_piece = self._new_piece()

        # Check game over
        if not self.is_valid_position(self.current_piece.blocks):
            self.game_over = True

        self.last_drop_time = time.time()

    def _clear_lines(self) -> int:
        """Remove completed lines and return count."""
        lines_to_clear = []
        for r in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.board[r]):
                lines_to_clear.append(r)

        for r in lines_to_clear:
            del self.board[r]
            self.board.insert(0, [None for _ in range(BOARD_WIDTH)])

        return len(lines_to_clear)

    def tick(self) -> bool:
        """Process a game tick (gravity). Returns True if piece was locked."""
        if self.paused or self.game_over:
            return False

        now = time.time()
        if now - self.last_drop_time >= self.drop_interval:
            self.last_drop_time = now
            if not self.move(1, 0):
                self.lock_piece()
                return True
        return False

    def get_ghost_blocks(self) -> list[tuple[int, int]]:
        """Get the position where the piece would land (ghost piece)."""
        piece = self.current_piece
        ghost_row = piece.row
        while True:
            new_blocks = piece.get_blocks_at(
                piece.rotation, ghost_row + 1, piece.col
            )
            if self.is_valid_position(new_blocks):
                ghost_row += 1
            else:
                break
        return piece.get_blocks_at(piece.rotation, ghost_row, piece.col)


def get_color(term: Terminal, shape_name: str) -> str:
    """Get the terminal color for a piece type."""
    colors = {
        "I": term.cyan,
        "O": term.yellow,
        "T": term.magenta,
        "S": term.green,
        "Z": term.red,
        "L": term.bright_yellow,
        "J": term.blue,
    }
    return colors.get(shape_name, term.white)


def draw_block(term: Terminal, y: int, x: int, shape_name: str, ghost: bool = False) -> str:
    """Draw a single block at the given terminal position."""
    color = get_color(term, shape_name)
    if ghost:
        return term.move_xy(x, y) + color + "▪▪" + term.normal
    else:
        return term.move_xy(x, y) + color + term.bold + "██" + term.normal


def draw_game(term: Terminal, game: TetrisGame) -> None:
    """Render the full game state to the terminal."""
    # Calculate positioning to center the game
    board_pixel_width = BOARD_WIDTH * CELL_WIDTH + 2  # +2 for borders
    sidebar_width = 20
    total_width = board_pixel_width + sidebar_width + 4
    start_x = max(0, (term.width - total_width) // 2)
    start_y = max(0, (term.height - BOARD_HEIGHT - 4) // 2)

    output = []
    output.append(term.home + term.clear)

    # Title
    title = "🧱  T E T R I S  🧱"
    title_x = start_x + (board_pixel_width // 2) - len(title) // 2 + 4
    output.append(term.move_xy(title_x, start_y) + term.bold + term.cyan + title + term.normal)

    board_y = start_y + 2
    board_x = start_x + 2

    # Draw board border
    top_border = "╔" + "══" * BOARD_WIDTH + "╗"
    output.append(term.move_xy(board_x, board_y) + term.white + top_border + term.normal)

    for r in range(BOARD_HEIGHT):
        output.append(
            term.move_xy(board_x, board_y + 1 + r)
            + term.white + "║" + term.normal
        )
        output.append(
            term.move_xy(board_x + 1 + BOARD_WIDTH * CELL_WIDTH, board_y + 1 + r)
            + term.white + "║" + term.normal
        )

    bottom_border = "╚" + "══" * BOARD_WIDTH + "╝"
    output.append(
        term.move_xy(board_x, board_y + BOARD_HEIGHT + 1)
        + term.white + bottom_border + term.normal
    )

    # Draw locked blocks on board
    for r in range(BOARD_HEIGHT):
        for c in range(BOARD_WIDTH):
            cell = game.board[r][c]
            px = board_x + 1 + c * CELL_WIDTH
            py = board_y + 1 + r
            if cell is not None:
                output.append(draw_block(term, py, px, cell))
            else:
                output.append(term.move_xy(px, py) + "  ")

    # Draw ghost piece
    if not game.game_over and not game.paused:
        ghost_blocks = game.get_ghost_blocks()
        current_blocks_set = set(game.current_piece.blocks)
        for r, c in ghost_blocks:
            if (r, c) not in current_blocks_set and 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
                px = board_x + 1 + c * CELL_WIDTH
                py = board_y + 1 + r
                output.append(draw_block(term, py, px, game.current_piece.shape_name, ghost=True))

    # Draw current piece
    if not game.game_over:
        for r, c in game.current_piece.blocks:
            if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
                px = board_x + 1 + c * CELL_WIDTH
                py = board_y + 1 + r
                output.append(draw_block(term, py, px, game.current_piece.shape_name))

    # Sidebar
    sidebar_x = board_x + board_pixel_width + 3
    sidebar_y = board_y

    # Score
    output.append(
        term.move_xy(sidebar_x, sidebar_y)
        + term.bold + term.white + "┌─────────────────┐" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 1)
        + term.bold + term.white + "│" + term.normal
        + term.bold + term.cyan + "    S C O R E    " + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    score_str = f"{game.score:>12}"
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 2)
        + term.bold + term.white + "│" + term.normal
        + term.bright_white + f"  {score_str}     "
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 3)
        + term.bold + term.white + "└─────────────────┘" + term.normal
    )

    # Level
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 5)
        + term.bold + term.yellow + f"  Level: {game.level}" + term.normal
    )

    # Lines
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 7)
        + term.bold + term.green + f"  Lines: {game.lines_cleared}" + term.normal
    )

    # Next piece preview
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 9)
        + term.bold + term.white + "┌─────────────────┐" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 10)
        + term.bold + term.white + "│" + term.normal
        + term.dim + "      NEXT       " + term.normal
        + term.bold + term.white + "│" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 11)
        + term.bold + term.white + "│                 │" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 12)
        + term.bold + term.white + "│                 │" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 13)
        + term.bold + term.white + "│                 │" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 14)
        + term.bold + term.white + "│                 │" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, sidebar_y + 15)
        + term.bold + term.white + "└─────────────────┘" + term.normal
    )

    # Draw next piece inside the preview box
    next_offsets = TETROMINOES[game.next_piece.shape_name][0]
    # Center the preview
    min_c = min(c for _, c in next_offsets)
    max_c = max(c for _, c in next_offsets)
    min_r = min(r for r, _ in next_offsets)
    max_r = max(r for r, _ in next_offsets)
    piece_w = (max_c - min_c + 1) * CELL_WIDTH
    piece_h = max_r - min_r + 1
    preview_center_x = sidebar_x + 1 + (17 - piece_w) // 2
    preview_center_y = sidebar_y + 11 + (4 - piece_h) // 2

    for dr, dc in next_offsets:
        px = preview_center_x + (dc - min_c) * CELL_WIDTH
        py = preview_center_y + (dr - min_r)
        output.append(draw_block(term, py, px, game.next_piece.shape_name))

    # Controls
    controls_y = sidebar_y + 17
    output.append(
        term.move_xy(sidebar_x, controls_y)
        + term.dim + "  ← →  Move" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 1)
        + term.dim + "   ↑   Rotate" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 2)
        + term.dim + "   ↓   Soft Drop" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 3)
        + term.dim + " Space  Hard Drop" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 4)
        + term.dim + "   p   Pause" + term.normal
    )
    output.append(
        term.move_xy(sidebar_x, controls_y + 5)
        + term.dim + "   q   Quit" + term.normal
    )

    # Pause overlay
    if game.paused:
        pause_text = "  ⏸  P A U S E D  ⏸  "
        px = start_x + (total_width - len(pause_text)) // 2
        py = start_y + BOARD_HEIGHT // 2 + 2
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
        overlay_width = 26
        ox = start_x + (total_width - overlay_width) // 2
        oy = start_y + BOARD_HEIGHT // 2

        output.append(
            term.move_xy(ox, oy)
            + term.bold + term.white_on_red + "                          " + term.normal
        )
        go_text = "    G A M E   O V E R     "
        output.append(
            term.move_xy(ox, oy + 1)
            + term.bold + term.white_on_red + go_text + term.normal
        )
        output.append(
            term.move_xy(ox, oy + 2)
            + term.bold + term.white_on_red + "                          " + term.normal
        )
        score_text = f"  Final Score: {game.score:<10} "
        output.append(
            term.move_xy(ox, oy + 3)
            + term.bold + term.white_on_red + score_text + term.normal
        )
        output.append(
            term.move_xy(ox, oy + 4)
            + term.bold + term.white_on_red + "                          " + term.normal
        )
        restart_text = " r: Restart  q: Quit Menu "
        output.append(
            term.move_xy(ox, oy + 5)
            + term.bold + term.white_on_red + restart_text + term.normal
        )
        output.append(
            term.move_xy(ox, oy + 6)
            + term.bold + term.white_on_red + "                          " + term.normal
        )

    # Write everything at once to avoid flicker
    print("".join(output), end="", flush=True)


def play_tetris(term: Terminal) -> None:
    """Main Tetris game loop."""
    game = TetrisGame()

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game)

        while True:
            # Handle input with short timeout for smooth gameplay
            key = term.inkey(timeout=0.03)

            if key:
                if key == "q" or key.name == "KEY_ESCAPE":
                    return  # Back to menu

                if game.game_over:
                    if key == "r":
                        game = TetrisGame()
                        draw_game(term, game)
                    continue

                if key == "p":
                    game.paused = not game.paused
                    draw_game(term, game)
                    continue

                if game.paused:
                    continue

                moved = False

                if key.name == "KEY_LEFT" or key == "a":
                    moved = game.move(0, -1)

                elif key.name == "KEY_RIGHT" or key == "d":
                    moved = game.move(0, 1)

                elif key.name == "KEY_DOWN" or key == "s":
                    if game.move(1, 0):
                        game.score += 1  # Soft drop bonus
                        game.last_drop_time = time.time()
                        moved = True

                elif key.name == "KEY_UP" or key == "w":
                    moved = game.rotate()

                elif key == " ":
                    game.hard_drop()
                    moved = True

                if moved:
                    draw_game(term, game)

            # Process gravity
            if not game.game_over and not game.paused:
                if game.tick():
                    draw_game(term, game)
                    continue

                # Redraw periodically for smooth animation
                now = time.time()
                elapsed = now - game.last_drop_time
                if elapsed > 0 and int(elapsed * 30) != int((elapsed - 0.03) * 30):
                    draw_game(term, game)
