"""Minesweeper - Classic mine-finding puzzle game 💣

Controls:
    ← → ↑ ↓   Move cursor (or WASD)
    Space/Enter Reveal cell
    f          Flag/unflag cell
    r          Restart game
    q          Quit to menu
"""

import random
import time
from typing import Optional

from blessed import Terminal

# Cell states
HIDDEN = "hidden"
REVEALED = "revealed"
FLAGGED = "flagged"

# Difficulty presets
DIFFICULTIES = {
    "easy": {"width": 9, "height": 9, "mines": 10, "label": "Easy (9×9, 10 mines)"},
    "medium": {"width": 16, "height": 16, "mines": 40, "label": "Medium (16×16, 40 mines)"},
    "hard": {"width": 24, "height": 16, "mines": 70, "label": "Hard (24×16, 70 mines)"},
}

CELL_WIDTH = 3  # Each cell is 3 characters wide for readability

# Number colors (1-8)
NUMBER_COLORS = {
    1: "blue",
    2: "green",
    3: "red",
    4: "bright_blue",
    5: "bright_red",
    6: "cyan",
    7: "magenta",
    8: "white",
}

# Neighbor offsets (8 directions)
NEIGHBORS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


class Cell:
    """Represents a single cell on the Minesweeper board."""

    def __init__(self):
        self.is_mine = False
        self.state = HIDDEN
        self.adjacent_mines = 0


class MinesweeperGame:
    """The Minesweeper game engine."""

    def __init__(self, width: int, height: int, num_mines: int):
        self.width = width
        self.height = height
        self.num_mines = num_mines

        # Create board
        self.board: list[list[Cell]] = [
            [Cell() for _ in range(width)] for _ in range(height)
        ]

        # Cursor position
        self.cursor_row = height // 2
        self.cursor_col = width // 2

        # Game state
        self.game_over = False
        self.won = False
        self.first_click = True  # Mines placed after first click
        self.flags_placed = 0
        self.cells_revealed = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    @property
    def elapsed_time(self) -> int:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time else time.time()
        return int(end - self.start_time)

    @property
    def total_safe_cells(self) -> int:
        """Total number of non-mine cells."""
        return self.width * self.height - self.num_mines

    def _place_mines(self, safe_row: int, safe_col: int) -> None:
        """Place mines randomly, ensuring the first click area is safe."""
        # Create a safe zone around the first click
        safe_zone = set()
        for dr, dc in NEIGHBORS:
            nr, nc = safe_row + dr, safe_col + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                safe_zone.add((nr, nc))
        safe_zone.add((safe_row, safe_col))

        # Get all possible mine positions
        all_positions = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (r, c) not in safe_zone
        ]

        # If not enough positions outside safe zone, reduce safe zone
        if len(all_positions) < self.num_mines:
            all_positions = [
                (r, c)
                for r in range(self.height)
                for c in range(self.width)
                if (r, c) != (safe_row, safe_col)
            ]

        # Place mines
        mine_positions = random.sample(all_positions, min(self.num_mines, len(all_positions)))
        for r, c in mine_positions:
            self.board[r][c].is_mine = True

        # Calculate adjacent mine counts
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c].is_mine:
                    continue
                count = 0
                for dr, dc in NEIGHBORS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if self.board[nr][nc].is_mine:
                            count += 1
                self.board[r][c].adjacent_mines = count

    def move_cursor(self, d_row: int, d_col: int) -> None:
        """Move the cursor by the given delta."""
        new_row = self.cursor_row + d_row
        new_col = self.cursor_col + d_col
        if 0 <= new_row < self.height and 0 <= new_col < self.width:
            self.cursor_row = new_row
            self.cursor_col = new_col

    def reveal(self, row: int, col: int) -> None:
        """Reveal a cell. If it's empty, flood fill."""
        if self.game_over:
            return

        cell = self.board[row][col]

        if cell.state == FLAGGED or cell.state == REVEALED:
            return

        # First click: place mines
        if self.first_click:
            self._place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()

        # Reveal the cell
        cell.state = REVEALED
        self.cells_revealed += 1

        # Hit a mine
        if cell.is_mine:
            self.game_over = True
            self.won = False
            self.end_time = time.time()
            self._reveal_all_mines()
            return

        # Flood fill if empty (0 adjacent mines)
        if cell.adjacent_mines == 0:
            self._flood_fill(row, col)

        # Check win condition
        if self.cells_revealed == self.total_safe_cells:
            self.game_over = True
            self.won = True
            self.end_time = time.time()
            # Auto-flag remaining mines
            for r in range(self.height):
                for c in range(self.width):
                    if self.board[r][c].is_mine and self.board[r][c].state != FLAGGED:
                        self.board[r][c].state = FLAGGED
                        self.flags_placed += 1

    def chord(self, row: int, col: int) -> None:
        """Chord: if a revealed number cell has enough flags around it, reveal remaining neighbors."""
        if self.game_over:
            return

        cell = self.board[row][col]
        if cell.state != REVEALED or cell.adjacent_mines == 0:
            return

        # Count adjacent flags
        flag_count = 0
        hidden_neighbors = []
        for dr, dc in NEIGHBORS:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbor = self.board[nr][nc]
                if neighbor.state == FLAGGED:
                    flag_count += 1
                elif neighbor.state == HIDDEN:
                    hidden_neighbors.append((nr, nc))

        # If flags match the number, reveal all hidden neighbors
        if flag_count == cell.adjacent_mines:
            for nr, nc in hidden_neighbors:
                self.reveal(nr, nc)

    def toggle_flag(self, row: int, col: int) -> None:
        """Toggle flag on a hidden cell."""
        if self.game_over:
            return

        cell = self.board[row][col]
        if cell.state == HIDDEN:
            cell.state = FLAGGED
            self.flags_placed += 1
        elif cell.state == FLAGGED:
            cell.state = HIDDEN
            self.flags_placed -= 1

    def _flood_fill(self, row: int, col: int) -> None:
        """Flood fill to reveal all connected empty cells."""
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            for dr, dc in NEIGHBORS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbor = self.board[nr][nc]
                    if neighbor.state == HIDDEN and not neighbor.is_mine:
                        neighbor.state = REVEALED
                        self.cells_revealed += 1
                        if neighbor.adjacent_mines == 0:
                            stack.append((nr, nc))

    def _reveal_all_mines(self) -> None:
        """Reveal all mines when game is over."""
        for r in range(self.height):
            for c in range(self.width):
                cell = self.board[r][c]
                if cell.is_mine and cell.state != FLAGGED:
                    cell.state = REVEALED


def get_number_color(term: Terminal, number: int) -> str:
    """Get terminal color for a mine count number."""
    color_name = NUMBER_COLORS.get(number, "white")
    return getattr(term, color_name, term.white)


def draw_difficulty_menu(term: Terminal) -> Optional[str]:
    """Show difficulty selection menu. Returns difficulty key or None to quit."""
    difficulties = list(DIFFICULTIES.keys())
    selected = 0

    while True:
        output = []
        output.append(term.home + term.clear)

        title = "💣  M I N E S W E E P E R  💣"
        title_x = max(0, (term.width - len(title)) // 2)
        title_y = term.height // 2 - len(difficulties) - 4
        output.append(
            term.move_xy(title_x, title_y)
            + term.bold + term.bright_red + title + term.normal
        )

        subtitle = "Select Difficulty"
        sub_x = max(0, (term.width - len(subtitle)) // 2)
        output.append(
            term.move_xy(sub_x, title_y + 2)
            + term.dim + subtitle + term.normal
        )

        menu_y = title_y + 4
        for i, diff_key in enumerate(difficulties):
            diff = DIFFICULTIES[diff_key]
            label = diff["label"]
            if i == selected:
                line = f"  ▸ {label}  "
                styled = term.bold + term.black_on_white + line + term.normal
            else:
                line = f"    {label}  "
                styled = term.dim + line + term.normal

            x = max(0, (term.width - len(line)) // 2)
            output.append(term.move_xy(x, menu_y + i * 2) + styled)

        controls = "↑/↓ Navigate  •  Enter Select  •  q Back"
        controls_x = max(0, (term.width - len(controls)) // 2)
        output.append(
            term.move_xy(controls_x, menu_y + len(difficulties) * 2 + 2)
            + term.dim + controls + term.normal
        )

        print("".join(output), end="", flush=True)

        key = term.inkey(timeout=None)

        if key.name == "KEY_UP" or key == "k" or key == "w":
            selected = (selected - 1) % len(difficulties)
        elif key.name == "KEY_DOWN" or key == "j" or key == "s":
            selected = (selected + 1) % len(difficulties)
        elif key.name == "KEY_ENTER" or key == "\n" or key == "\r":
            return difficulties[selected]
        elif key == "q" or key.name == "KEY_ESCAPE":
            return None


def draw_game(term: Terminal, game: MinesweeperGame, start_x: int, start_y: int) -> None:
    """Render the full game state to the terminal."""
    output = []
    output.append(term.home + term.clear)

    board_pixel_width = game.width * CELL_WIDTH + 2  # +2 for borders

    # Title
    title = "💣  M I N E S W E E P E R  💣"
    title_x = start_x + (board_pixel_width // 2) - len(title) // 2 + 2
    output.append(
        term.move_xy(title_x, start_y)
        + term.bold + term.bright_red + title + term.normal
    )

    # Status bar (mines remaining, time, smiley)
    mines_remaining = game.num_mines - game.flags_placed
    elapsed = game.elapsed_time

    if game.game_over and game.won:
        face = "😎"
    elif game.game_over:
        face = "💀"
    else:
        face = "🙂"

    status_left = f"💣 {mines_remaining:>3}"
    status_right = f"⏱  {elapsed:>3}s"
    status_center = face

    board_x = start_x + 2
    status_y = start_y + 2

    output.append(
        term.move_xy(board_x + 1, status_y)
        + term.bold + term.red + status_left + term.normal
    )
    center_x = board_x + board_pixel_width // 2 - 1
    output.append(
        term.move_xy(center_x, status_y)
        + status_center
    )
    output.append(
        term.move_xy(board_x + board_pixel_width - len(status_right) - 1, status_y)
        + term.bold + term.yellow + status_right + term.normal
    )

    board_y = status_y + 2

    # Draw board border
    top_border = "╔" + "═══" * game.width + "╗"
    output.append(
        term.move_xy(board_x, board_y)
        + term.white + top_border + term.normal
    )

    for r in range(game.height):
        row_y = board_y + 1 + r
        output.append(
            term.move_xy(board_x, row_y)
            + term.white + "║" + term.normal
        )

        for c in range(game.width):
            cell = game.board[r][c]
            px = board_x + 1 + c * CELL_WIDTH
            is_cursor = (r == game.cursor_row and c == game.cursor_col)

            # Determine cell display
            if cell.state == HIDDEN:
                if is_cursor and not game.game_over:
                    display = term.black_on_bright_white + term.bold + " · " + term.normal
                else:
                    display = term.on_bright_black + " · " + term.normal
            elif cell.state == FLAGGED:
                if is_cursor and not game.game_over:
                    display = term.black_on_bright_white + term.bold + " ⚑ " + term.normal
                elif game.game_over and not cell.is_mine:
                    # Wrong flag
                    display = term.on_red + term.bold + term.white + " ✗ " + term.normal
                else:
                    display = term.on_bright_black + term.bold + term.bright_yellow + " ⚑ " + term.normal
            elif cell.state == REVEALED:
                if cell.is_mine:
                    if r == game.cursor_row and c == game.cursor_col and not game.won:
                        # The mine that was clicked
                        display = term.on_red + term.bold + term.white + " ✹ " + term.normal
                    else:
                        display = term.on_bright_black + term.bold + term.red + " ✹ " + term.normal
                elif cell.adjacent_mines == 0:
                    if is_cursor and not game.game_over:
                        display = term.black_on_bright_white + "   " + term.normal
                    else:
                        display = "   "
                else:
                    num = str(cell.adjacent_mines)
                    color = get_number_color(term, cell.adjacent_mines)
                    if is_cursor and not game.game_over:
                        display = term.black_on_bright_white + term.bold + f" {num} " + term.normal
                    else:
                        display = color + term.bold + f" {num} " + term.normal

            output.append(term.move_xy(px, row_y) + display)

        output.append(
            term.move_xy(board_x + 1 + game.width * CELL_WIDTH, row_y)
            + term.white + "║" + term.normal
        )

    bottom_border = "╚" + "═══" * game.width + "╝"
    output.append(
        term.move_xy(board_x, board_y + game.height + 1)
        + term.white + bottom_border + term.normal
    )

    # Controls section below board
    controls_y = board_y + game.height + 3
    controls = [
        ("← → ↑ ↓", "Move cursor"),
        ("Space/Enter", "Reveal cell"),
        ("f", "Flag/unflag"),
        ("c", "Chord (auto-reveal)"),
        ("r", "Restart"),
        ("q", "Quit to menu"),
    ]

    controls_x = board_x + 2
    for i, (key_str, desc) in enumerate(controls):
        col_offset = (i % 2) * 28
        row_offset = i // 2
        output.append(
            term.move_xy(controls_x + col_offset, controls_y + row_offset)
            + term.bold + term.cyan + f"{key_str:<14}" + term.normal
            + term.dim + desc + term.normal
        )

    # Game over / win overlay
    if game.game_over:
        overlay_width = 32
        ox = start_x + max(0, (board_pixel_width + 4 - overlay_width) // 2)
        oy = start_y + game.height // 2 + 2

        if game.won:
            header_color = term.white_on_green
            lines = [
                "                                ",
                "    🎉  Y O U   W I N !  🎉    ",
                "                                ",
                f"  Time: {game.elapsed_time}s                     "[:32],
                f"  Mines: {game.num_mines}                     "[:32],
                "                                ",
                "  r: Play Again   q: Quit Menu  ",
                "                                ",
            ]
        else:
            header_color = term.white_on_red
            lines = [
                "                                ",
                "    💥  G A M E   O V E R  💥   ",
                "                                ",
                f"  Time: {game.elapsed_time}s                     "[:32],
                f"  Revealed: {game.cells_revealed}/{game.total_safe_cells}               "[:32],
                "                                ",
                "  r: Play Again   q: Quit Menu  ",
                "                                ",
            ]

        for i, line in enumerate(lines):
            display_line = line[:overlay_width].ljust(overlay_width)
            output.append(
                term.move_xy(ox, oy + i)
                + term.bold + header_color + display_line + term.normal
            )

    # Write everything at once
    print("".join(output), end="", flush=True)


def play_minesweeper(term: Terminal) -> None:
    """Main Minesweeper game loop."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        # Show difficulty selection
        difficulty = draw_difficulty_menu(term)
        if difficulty is None:
            return  # Back to main menu

        diff_settings = DIFFICULTIES[difficulty]
        game_width = diff_settings["width"]
        game_height = diff_settings["height"]
        num_mines = diff_settings["mines"]

        game = MinesweeperGame(game_width, game_height, num_mines)

        # Calculate positioning to center the game
        board_pixel_width = game_width * CELL_WIDTH + 2
        start_x = max(0, (term.width - board_pixel_width - 4) // 2)
        start_y = max(0, (term.height - game_height - 10) // 2)

        draw_game(term, game, start_x, start_y)

        last_draw_time = time.time()

        while True:
            # Handle input
            key = term.inkey(timeout=0.5)

            needs_redraw = False

            if key:
                if key == "q" or key.name == "KEY_ESCAPE":
                    return  # Back to menu

                if key == "r":
                    # Restart - go back to difficulty menu
                    difficulty = draw_difficulty_menu(term)
                    if difficulty is None:
                        return
                    diff_settings = DIFFICULTIES[difficulty]
                    game_width = diff_settings["width"]
                    game_height = diff_settings["height"]
                    num_mines = diff_settings["mines"]
                    game = MinesweeperGame(game_width, game_height, num_mines)
                    board_pixel_width = game_width * CELL_WIDTH + 2
                    start_x = max(0, (term.width - board_pixel_width - 4) // 2)
                    start_y = max(0, (term.height - game_height - 10) // 2)
                    needs_redraw = True

                elif not game.game_over:
                    # Cursor movement
                    if key.name == "KEY_UP" or key == "w":
                        game.move_cursor(-1, 0)
                        needs_redraw = True
                    elif key.name == "KEY_DOWN" or key == "s":
                        game.move_cursor(1, 0)
                        needs_redraw = True
                    elif key.name == "KEY_LEFT" or key == "a":
                        game.move_cursor(0, -1)
                        needs_redraw = True
                    elif key.name == "KEY_RIGHT" or key == "d":
                        game.move_cursor(0, 1)
                        needs_redraw = True

                    # Actions
                    elif key == " " or key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                        cell = game.board[game.cursor_row][game.cursor_col]
                        if cell.state == REVEALED and cell.adjacent_mines > 0:
                            game.chord(game.cursor_row, game.cursor_col)
                        else:
                            game.reveal(game.cursor_row, game.cursor_col)
                        needs_redraw = True
                    elif key == "f":
                        game.toggle_flag(game.cursor_row, game.cursor_col)
                        needs_redraw = True
                    elif key == "c":
                        game.chord(game.cursor_row, game.cursor_col)
                        needs_redraw = True

            # Periodic redraw for timer updates
            now = time.time()
            if not game.game_over and game.start_time is not None:
                if now - last_draw_time >= 1.0:
                    needs_redraw = True

            if needs_redraw:
                draw_game(term, game, start_x, start_y)
                last_draw_time = now
