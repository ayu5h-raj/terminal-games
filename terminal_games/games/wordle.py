"""Wordle - Guess the 5-letter word in 6 tries! 📝

Controls:
    A-Z         Type letter
    ENTER       Submit guess
    BACKSPACE   Delete last letter
    R           Restart with a new word
    Q / ESC     Quit to menu
"""

from __future__ import annotations

import random
from functools import lru_cache
from typing import Literal

from blessed import Terminal

from terminal_games.data import common_words, valid_5letter_guesses

WORD_LENGTH = 5
MAX_GUESSES = 6
CELL_WIDTH = 5
ROW_GAP = 1
COL_GAP = 1

LetterStatus = Literal["correct", "present", "absent"]


@lru_cache(maxsize=1)
def _answer_pool() -> tuple[str, ...]:
    """5-letter answer pool, drawn from the common-words dictionary.

    Using common words (not rare dictionary entries) means the target is
    always something a player can plausibly recognize.
    """
    return tuple(w for w in common_words() if len(w) == WORD_LENGTH)


@lru_cache(maxsize=1)
def _valid_guesses() -> frozenset[str]:
    """Accept any 5-letter English word as a valid guess.

    Combines the broad 5-letter dictionary with the answer pool, so
    answers are always also valid as guesses.
    """
    return valid_5letter_guesses() | frozenset(_answer_pool())


# QWERTY layout for the on-screen keyboard.
KEYBOARD_ROWS: tuple[str, ...] = ("qwertyuiop", "asdfghjkl", "zxcvbnm")

# Status priority — used so a letter that's been guessed correctly doesn't
# get "downgraded" to "present" or "absent" by a later guess.
STATUS_PRIORITY: dict[str, int] = {"correct": 3, "present": 2, "absent": 1}


class WordleGame:
    """Wordle game engine — pure logic, no rendering."""

    def __init__(self) -> None:
        self.target: str = ""
        self.guesses: list[str] = []
        self.feedback: list[list[LetterStatus]] = []
        self.current: str = ""
        self.state: Literal["playing", "won", "lost"] = "playing"
        self.letter_status: dict[str, LetterStatus] = {}
        self.flash: str = ""
        self.reset()

    def reset(self) -> None:
        self.target = random.choice(_answer_pool())
        self.guesses = []
        self.feedback = []
        self.current = ""
        self.state = "playing"
        self.letter_status = {}
        self.flash = ""

    def add_letter(self, c: str) -> None:
        if self.state != "playing":
            return
        if len(self.current) >= WORD_LENGTH:
            return
        if not c.isalpha() or len(c) != 1:
            return
        self.current += c.lower()

    def delete_letter(self) -> None:
        if self.state != "playing":
            return
        self.current = self.current[:-1]

    def submit(self) -> tuple[bool, str]:
        """Try to submit the current guess. Returns (success, error)."""
        if self.state != "playing":
            return (False, "")
        if len(self.current) != WORD_LENGTH:
            return (False, "Not enough letters")
        if self.current not in _valid_guesses():
            return (False, "Not in word list")
        if self.current in self.guesses:
            # Official Wordle silently allows duplicates (wastes a guess); we
            # surface a flash so the player can correct without burning a row.
            return (False, "Already guessed")

        feedback = self._evaluate(self.current)
        self.guesses.append(self.current)
        self.feedback.append(feedback)

        for ch, status in zip(self.current, feedback):
            existing = self.letter_status.get(ch)
            if existing is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[existing]:
                self.letter_status[ch] = status

        if self.current == self.target:
            self.state = "won"
        elif len(self.guesses) >= MAX_GUESSES:
            self.state = "lost"

        self.current = ""
        return (True, "")

    def _evaluate(self, guess: str) -> list[LetterStatus]:
        """Wordle-style evaluation that handles duplicate letters correctly.

        Two passes: first mark exact matches and consume those target slots,
        then mark "present" for remaining letters that exist elsewhere in the
        target — but only as many times as they remain in the target.
        """
        result: list[LetterStatus] = ["absent"] * WORD_LENGTH
        target_chars: list[str] = list(self.target)

        # Pass 1: correct positions, consume target slots.
        for i in range(WORD_LENGTH):
            if guess[i] == target_chars[i]:
                result[i] = "correct"
                target_chars[i] = ""

        # Pass 2: present (letter exists elsewhere, still has remaining count).
        for i in range(WORD_LENGTH):
            if result[i] == "correct":
                continue
            if guess[i] in target_chars:
                result[i] = "present"
                target_chars[target_chars.index(guess[i])] = ""

        return result


def _cell_style(term: Terminal, status: LetterStatus | None) -> str:
    if status == "correct":
        return term.bold + term.white_on_green
    if status == "present":
        return term.bold + term.black_on_yellow
    if status == "absent":
        return term.bold + term.white_on_bright_black
    return ""


def _render_cell(term: Terminal, ch: str, status: LetterStatus | None, in_current_row: bool) -> str:
    """Return a CELL_WIDTH-character cell for a tile."""
    label = ch.upper() if ch.strip() else " "
    text = f"  {label}  "
    text = text[:CELL_WIDTH].ljust(CELL_WIDTH)

    if status is not None:
        return _cell_style(term, status) + text + term.normal

    if label != " ":
        return term.bold + term.bright_white + text + term.normal
    if in_current_row:
        return term.bright_black + "  ·  "[:CELL_WIDTH] + term.normal
    return term.bright_black + "  ·  "[:CELL_WIDTH] + term.normal


def draw_game(term: Terminal, game: WordleGame) -> None:
    """Render the full Wordle screen."""
    output: list[str] = [term.home + term.clear]

    grid_width = WORD_LENGTH * CELL_WIDTH + (WORD_LENGTH - 1) * COL_GAP
    grid_height = MAX_GUESSES + (MAX_GUESSES - 1) * ROW_GAP
    keyboard_height = len(KEYBOARD_ROWS)
    total_height = 2 + 1 + grid_height + 2 + keyboard_height + 2

    start_y = max(1, (term.height - total_height) // 2)

    title = "📝  W O R D L E  📝"
    title_x = max(0, (term.width - len(title)) // 2)
    output.append(term.move_xy(title_x, start_y) + term.bold + term.bright_yellow + title + term.normal)

    header_y = start_y + 2
    if game.state == "playing":
        info = f"Guess {len(game.guesses) + 1} of {MAX_GUESSES}"
        info_color = term.bright_white
    elif game.state == "won":
        plural = "try" if len(game.guesses) == 1 else "tries"
        info = f"Solved in {len(game.guesses)} {plural}!"
        info_color = term.bright_green
    else:
        info = "Out of guesses"
        info_color = term.bright_red
    info_x = max(0, (term.width - len(info)) // 2)
    output.append(term.move_xy(info_x, header_y) + term.bold + info_color + info + term.normal)

    grid_x = max(0, (term.width - grid_width) // 2)
    grid_y = header_y + 2
    current_row = len(game.guesses)

    for row in range(MAX_GUESSES):
        row_y = grid_y + row * (1 + ROW_GAP)
        if row < len(game.guesses):
            word = game.guesses[row]
            statuses: list[LetterStatus | None] = list(game.feedback[row])
        elif row == current_row and game.state == "playing":
            word = game.current.ljust(WORD_LENGTH)
            statuses = [None] * WORD_LENGTH
        else:
            word = " " * WORD_LENGTH
            statuses = [None] * WORD_LENGTH

        for col in range(WORD_LENGTH):
            cx = grid_x + col * (CELL_WIDTH + COL_GAP)
            cell = _render_cell(term, word[col], statuses[col], in_current_row=(row == current_row))
            output.append(term.move_xy(cx, row_y) + cell)

    flash_y = grid_y + grid_height + 1
    if game.flash:
        fx = max(0, (term.width - len(game.flash)) // 2)
        output.append(term.move_xy(fx, flash_y) + term.bold + term.bright_red + game.flash + term.normal)

    kb_y = flash_y + 2
    for ri, row_str in enumerate(KEYBOARD_ROWS):
        row_w = len(row_str) * 4 - 1
        rx = max(0, (term.width - row_w) // 2)
        ry = kb_y + ri
        for ki, ch in enumerate(row_str):
            status = game.letter_status.get(ch)
            label = f" {ch.upper()} "
            if status is not None:
                styled = _cell_style(term, status) + label + term.normal
            else:
                styled = term.bold + term.white + label + term.normal
            output.append(term.move_xy(rx + ki * 4, ry) + styled)

    controls_y = kb_y + len(KEYBOARD_ROWS) + 1
    if game.state == "playing":
        controls = "A-Z type  •  ENTER submit  •  ⌫ delete  •  ESC quit"
    else:
        controls = "r: new word  •  q/ESC: quit to menu"
    cx = max(0, (term.width - len(controls)) // 2)
    output.append(term.move_xy(cx, controls_y) + term.dim + controls + term.normal)

    if game.state in ("won", "lost"):
        reveal = f"Word: {game.target.upper()}"
        rx = max(0, (term.width - len(reveal)) // 2)
        ry = controls_y + 2
        if game.state == "won":
            output.append(term.move_xy(rx, ry) + term.bold + term.black_on_bright_green + f" {reveal} " + term.normal)
        else:
            output.append(term.move_xy(rx, ry) + term.bold + term.white_on_red + f" {reveal} " + term.normal)

    print("".join(output), end="", flush=True)


def play_wordle(term: Terminal) -> None:
    """Main Wordle loop."""
    game = WordleGame()

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game)

        while True:
            key = term.inkey(timeout=None)
            had_flash = bool(game.flash)
            if had_flash:
                game.flash = ""

            # ESC always quits to menu, regardless of state.
            if key.name == "KEY_ESCAPE":
                return

            # 'q' and 'r' are commands only when the round is over —
            # during play they're valid letters in your guess.
            if game.state != "playing":
                if key == "q":
                    return
                if key == "r":
                    game.reset()
                    draw_game(term, game)
                    continue
                if had_flash:
                    draw_game(term, game)
                continue

            if key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                ok, err = game.submit()
                if not ok and err:
                    game.flash = err
                draw_game(term, game)
                continue

            if key.name == "KEY_BACKSPACE" or key == "\x7f" or key == "\b":
                game.delete_letter()
                draw_game(term, game)
                continue

            ks = str(key)
            if len(ks) == 1 and ks.isalpha():
                game.add_letter(ks)
                draw_game(term, game)
                continue

            if had_flash:
                draw_game(term, game)
