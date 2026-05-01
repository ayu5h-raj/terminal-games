"""Wordle - Guess the 5-letter word in 6 tries! 📝

Modes:
    Random     - new word each round, ``r`` to play again
    Daily      - one puzzle per day, deterministic by date, locks once solved

Controls:
    A-Z         Type letter
    ENTER       Submit guess
    BACKSPACE   Delete last letter
    R           (Random mode only) Restart with a new word
    Q / ESC     Quit to menu
"""

from __future__ import annotations

import json
import random
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal

from blessed import Terminal

from terminal_games.data import wordle_answers, wordle_valid_guesses

WORD_LENGTH = 5
MAX_GUESSES = 6
CELL_WIDTH = 5
ROW_GAP = 1
COL_GAP = 1

# Daily #1 corresponds to this date. Choose a stable epoch in the past so
# all current/future puzzle numbers are positive integers.
DAILY_EPOCH = date(2024, 1, 1)

DAILY_STATE_FILENAME = "wordle_daily.json"


def _daily_state_path() -> Path:
    """Computed lazily so an unset ``$HOME`` only breaks daily mode, not import."""
    return Path.home() / ".terminal_games" / DAILY_STATE_FILENAME

LetterStatus = Literal["correct", "present", "absent"]


@lru_cache(maxsize=1)
def _answer_pool() -> tuple[str, ...]:
    """Curated Wordle answer pool. Sorted for stable daily-mode indexing."""
    return tuple(sorted(wordle_answers()))


@lru_cache(maxsize=1)
def _valid_guesses() -> frozenset[str]:
    """Words accepted as guesses — exactly the original Wordle valid set.

    Matches NYT Wordle's behavior: only the curated 12,963 answers +
    allowed-guesses are accepted, not every entry in a broader English
    dictionary (which contains non-words like ``abdom``/``abdal``).
    """
    return wordle_valid_guesses() | frozenset(_answer_pool())


KEYBOARD_ROWS: tuple[str, ...] = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
STATUS_PRIORITY: dict[str, int] = {"correct": 3, "present": 2, "absent": 1}


def daily_number(today: date | None = None) -> int:
    """Return the 1-indexed daily puzzle number for ``today``."""
    if today is None:
        today = date.today()
    return (today - DAILY_EPOCH).days + 1


def daily_target(today: date | None = None) -> str:
    """Deterministically pick today's answer from the sorted pool.

    Stability rests on three invariants — all three must hold for a given
    date to map to the same word forever:
        1. ``words_wordle_answers.txt`` is append-only (no removals, sort
           order preserved).
        2. ``BLOCKLIST`` in ``scripts/build_wordle_answers.py`` never grows.
        3. CPython's ``random.Random(seed).choice`` stays stable across
           Python releases (informally true for many years, not formally
           guaranteed by the stdlib).
    """
    if today is None:
        today = date.today()
    pool = _answer_pool()
    return random.Random(today.toordinal()).choice(pool)


def _load_daily_state() -> dict | None:
    """Read the persisted daily state. Returns ``None`` for any failure
    mode — missing file, unreadable, malformed JSON, or wrong shape."""
    path = _daily_state_path()
    if not path.exists():
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _save_daily_state(
    game: WordleGame, puzzle_number: int, *, today: date
) -> None:
    """Persist daily state. Best-effort — write failures are swallowed."""
    try:
        path = _daily_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "date": today.isoformat(),
            "puzzle_number": puzzle_number,
            "target": game.target,
            "guesses": list(game.guesses),
            "state": game.state,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass


class WordleGame:
    """Wordle game engine — pure logic, no rendering."""

    def __init__(self, target: str | None = None) -> None:
        self.target: str = ""
        self.guesses: list[str] = []
        self.feedback: list[list[LetterStatus]] = []
        self.current: str = ""
        self.state: Literal["playing", "won", "lost"] = "playing"
        self.letter_status: dict[str, LetterStatus] = {}
        self.flash: str = ""
        self._fixed_target: str | None = target
        self.reset()

    def reset(self) -> None:
        self.target = self._fixed_target or random.choice(_answer_pool())
        self.guesses = []
        self.feedback = []
        self.current = ""
        self.state = "playing"
        self.letter_status = {}
        self.flash = ""

    def hydrate(self, guesses: list[str]) -> None:
        """Replay a list of past guesses to rebuild board + keyboard state."""
        self.guesses = []
        self.feedback = []
        self.letter_status = {}
        self.current = ""
        self.flash = ""
        self.state = "playing"
        for raw in guesses:
            if not isinstance(raw, str):
                continue
            g = raw.lower()
            if len(g) != WORD_LENGTH or not g.isalpha():
                continue
            feedback = self._evaluate(g)
            self.guesses.append(g)
            self.feedback.append(feedback)
            for ch, status in zip(g, feedback):
                existing = self.letter_status.get(ch)
                if existing is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[existing]:
                    self.letter_status[ch] = status
            if g == self.target:
                self.state = "won"
                return
            if len(self.guesses) >= MAX_GUESSES:
                self.state = "lost"
                return

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
        """Wordle-style evaluation that handles duplicate letters correctly."""
        result: list[LetterStatus] = ["absent"] * WORD_LENGTH
        target_chars: list[str] = list(self.target)

        for i in range(WORD_LENGTH):
            if guess[i] == target_chars[i]:
                result[i] = "correct"
                target_chars[i] = ""

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


def draw_game(
    term: Terminal,
    game: WordleGame,
    *,
    daily: bool = False,
    puzzle_number: int | None = None,
    locked_today: bool = False,
) -> None:
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
        if daily and puzzle_number is not None:
            info = f"Daily #{puzzle_number}  •  Guess {len(game.guesses) + 1} of {MAX_GUESSES}"
        else:
            info = f"Guess {len(game.guesses) + 1} of {MAX_GUESSES}"
        info_color = term.bright_white
    elif game.state == "won":
        plural = "try" if len(game.guesses) == 1 else "tries"
        prefix = f"Daily #{puzzle_number} — " if daily and puzzle_number is not None else ""
        info = f"{prefix}Solved in {len(game.guesses)} {plural}!"
        info_color = term.bright_green
    else:
        prefix = f"Daily #{puzzle_number} — " if daily and puzzle_number is not None else ""
        info = f"{prefix}Out of guesses"
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
    elif daily:
        controls = "Come back tomorrow!  •  q/ESC: quit to menu"
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


def play_wordle(term: Terminal, *, daily: bool = False) -> None:
    """Main Wordle loop. Set ``daily=True`` for the once-a-day deterministic mode."""
    if daily:
        _play_daily(term)
        return

    game = WordleGame()

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game)

        while True:
            key = term.inkey(timeout=None)
            had_flash = bool(game.flash)
            if had_flash:
                game.flash = ""

            if key.name == "KEY_ESCAPE":
                return

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


def play_wordle_daily(term: Terminal) -> None:
    """Convenience entry for the daily mode (used by the menu)."""
    play_wordle(term, daily=True)


def _play_daily(term: Terminal) -> None:
    """Daily-mode loop: deterministic word, resume support, locked when finished."""
    today = date.today()
    puzzle_number = daily_number(today)
    target = daily_target(today)

    game = WordleGame(target=target)

    saved = _load_daily_state()
    if (
        saved
        and saved.get("date") == today.isoformat()
        and saved.get("target") == target
    ):
        prior = saved.get("guesses")
        if isinstance(prior, list):
            game.hydrate(prior)

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game, daily=True, puzzle_number=puzzle_number)

        while True:
            key = term.inkey(timeout=None)
            had_flash = bool(game.flash)
            if had_flash:
                game.flash = ""

            if key.name == "KEY_ESCAPE":
                return

            if game.state != "playing":
                # Locked: only ESC/q exit, no restart, no further input.
                if key == "q":
                    return
                if had_flash:
                    draw_game(term, game, daily=True, puzzle_number=puzzle_number)
                continue

            if key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                ok, err = game.submit()
                if ok:
                    # Stamp the file with the date the puzzle started, not
                    # ``date.today()``, so a midnight rollover mid-puzzle
                    # doesn't silently invalidate the in-progress board.
                    _save_daily_state(game, puzzle_number, today=today)
                elif err:
                    game.flash = err
                draw_game(term, game, daily=True, puzzle_number=puzzle_number)
                continue

            if key.name == "KEY_BACKSPACE" or key == "\x7f" or key == "\b":
                game.delete_letter()
                draw_game(term, game, daily=True, puzzle_number=puzzle_number)
                continue

            ks = str(key)
            if len(ks) == 1 and ks.isalpha():
                game.add_letter(ks)
                draw_game(term, game, daily=True, puzzle_number=puzzle_number)
                continue

            if had_flash:
                draw_game(term, game, daily=True, puzzle_number=puzzle_number)
