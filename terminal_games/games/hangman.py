"""Hangman - Guess the word before the hangman is drawn! 🪢

Controls:
    A-Z       Guess a letter
    R         Restart with a new word
    Q / ESC   Quit to menu
"""

from __future__ import annotations

import random
import string
from functools import lru_cache
from typing import Literal

from blessed import Terminal

from terminal_games.data import common_words

MAX_WRONG = 6
MIN_WORD_LEN = 4
MAX_WORD_LEN = 10
GuessResult = Literal["hit", "miss", "already", "ignored"]
GameState = Literal["playing", "won", "lost"]


@lru_cache(maxsize=1)
def _word_pool() -> tuple[str, ...]:
    """Hangman word pool: common English words, 4–10 letters.

    Drawn from the bundled common-words list so every puzzle word is
    something a player can plausibly recognize. Length-filtered so the
    word fits on screen and is neither trivially short nor unfair.
    """
    return tuple(
        w for w in common_words()
        if MIN_WORD_LEN <= len(w) <= MAX_WORD_LEN
    )

# Seven progressive stages of the gallows. Each stage is a list of 7 lines
# of equal visible width (11 chars). Stage 0 = empty, Stage 6 = full hang.
GALLOWS_STAGES: tuple[tuple[str, ...], ...] = (
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │        ",
        "  │        ",
        "  │        ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │        ",
        "  │        ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │     │  ",
        "  │        ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │    /│  ",
        "  │        ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │    /│\\ ",
        "  │        ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │    /│\\ ",
        "  │    /   ",
        "  │        ",
        "══╧════════",
    ),
    (
        "  ┌─────┐  ",
        "  │     │  ",
        "  │     O  ",
        "  │    /│\\ ",
        "  │    / \\ ",
        "  │        ",
        "══╧════════",
    ),
)
GALLOWS_WIDTH = 11
GALLOWS_HEIGHT = 7


class HangmanGame:
    """Hangman game engine — pure logic, no rendering."""

    def __init__(self) -> None:
        self.target: str = ""
        self.guessed: set[str] = set()
        self.wrong_count: int = 0
        self.state: GameState = "playing"
        self.last_result: GuessResult = "ignored"
        self.reset()

    def reset(self) -> None:
        self.target = random.choice(_word_pool())
        self.guessed = set()
        self.wrong_count = 0
        self.state = "playing"
        self.last_result = "ignored"

    def guess(self, letter: str) -> GuessResult:
        if self.state != "playing":
            self.last_result = "ignored"
            return "ignored"
        if not letter or len(letter) != 1 or not letter.isalpha():
            self.last_result = "ignored"
            return "ignored"
        letter = letter.lower()

        if letter in self.guessed:
            self.last_result = "already"
            return "already"

        self.guessed.add(letter)

        if letter in self.target:
            if all(c in self.guessed for c in self.target):
                self.state = "won"
            self.last_result = "hit"
            return "hit"

        self.wrong_count += 1
        if self.wrong_count >= MAX_WRONG:
            self.state = "lost"
        self.last_result = "miss"
        return "miss"

    def display_word(self, reveal: bool = False) -> str:
        """Render the target with unguessed letters replaced by underscores."""
        return " ".join(
            c.upper() if (reveal or c in self.guessed) else "_"
            for c in self.target
        )


def draw_game(term: Terminal, game: HangmanGame) -> None:
    """Render the full Hangman screen."""
    output: list[str] = [term.home + term.clear]

    # Layout: title / status / gallows / word / alphabet / controls / reveal
    word_display = game.display_word(reveal=(game.state == "lost"))
    word_width = len(word_display)

    # Total visible block width is roughly the alphabet (~25 chars) — center
    # everything around the terminal midpoint independently.
    block_height = 1 + 1 + 1 + GALLOWS_HEIGHT + 2 + 2 + 2 + 1
    start_y = max(1, (term.height - block_height) // 2)

    # Title
    title = "🪢  H A N G M A N  🪢"
    title_x = max(0, (term.width - len(title)) // 2)
    output.append(term.move_xy(title_x, start_y) + term.bold + term.bright_yellow + title + term.normal)

    # Status
    status_y = start_y + 2
    if game.state == "playing":
        status = f"Misses: {game.wrong_count} / {MAX_WRONG}"
        status_color = term.bright_white
    elif game.state == "won":
        status = "🎉  You saved the stickman!"
        status_color = term.bright_green
    else:
        status = "💀  You lost — the stickman is hanged."
        status_color = term.bright_red
    sx = max(0, (term.width - len(status)) // 2)
    output.append(term.move_xy(sx, status_y) + term.bold + status_color + status + term.normal)

    # Gallows
    gallows = GALLOWS_STAGES[min(game.wrong_count, MAX_WRONG)]
    gallows_y = status_y + 2
    gx = max(0, (term.width - GALLOWS_WIDTH) // 2)
    gallows_color = term.bright_red if game.state == "lost" else term.bright_white
    for i, line in enumerate(gallows):
        output.append(term.move_xy(gx, gallows_y + i) + gallows_color + line + term.normal)

    # Word display
    word_y = gallows_y + GALLOWS_HEIGHT + 1
    wx = max(0, (term.width - word_width) // 2)
    if game.state == "lost":
        word_color = term.bold + term.bright_red
    elif game.state == "won":
        word_color = term.bold + term.bright_green
    else:
        word_color = term.bold + term.bright_cyan
    output.append(term.move_xy(wx, word_y) + word_color + word_display + term.normal)

    # Alphabet
    alphabet_y = word_y + 2
    row1 = string.ascii_lowercase[:13]
    row2 = string.ascii_lowercase[13:]
    row_width = len(row1) * 2 - 1  # "A B C ... M" — letter + space
    for ri, row in enumerate((row1, row2)):
        rx = max(0, (term.width - row_width) // 2)
        ry = alphabet_y + ri
        for ki, ch in enumerate(row):
            cx = rx + ki * 2
            if ch in game.guessed:
                if ch in game.target:
                    style = term.bold + term.bright_green
                else:
                    style = term.bold + term.bright_red
            else:
                style = term.dim + term.white
            output.append(term.move_xy(cx, ry) + style + ch.upper() + term.normal)

    # Controls / reveal
    controls_y = alphabet_y + 2 + 1
    if game.state == "playing":
        if game.last_result == "already":
            note = "(already guessed)"
            output.append(
                term.move_xy(max(0, (term.width - len(note)) // 2), controls_y - 1)
                + term.dim + term.bright_yellow + note + term.normal
            )
        controls = "A-Z guess  •  ESC quit to menu"
    else:
        controls = "r: new word  •  q/ESC: quit to menu"
    cx = max(0, (term.width - len(controls)) // 2)
    output.append(term.move_xy(cx, controls_y) + term.dim + controls + term.normal)

    # Word reveal box on game over
    if game.state in ("won", "lost"):
        reveal = f"Word: {game.target.upper()}"
        rx = max(0, (term.width - len(reveal) - 2) // 2)
        ry = controls_y + 2
        if game.state == "won":
            output.append(term.move_xy(rx, ry) + term.bold + term.black_on_bright_green + f" {reveal} " + term.normal)
        else:
            output.append(term.move_xy(rx, ry) + term.bold + term.white_on_red + f" {reveal} " + term.normal)

    print("".join(output), end="", flush=True)


def play_hangman(term: Terminal) -> None:
    """Main Hangman loop."""
    game = HangmanGame()

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_game(term, game)

        while True:
            key = term.inkey(timeout=None)

            # ESC always quits to menu, regardless of state.
            if key.name == "KEY_ESCAPE":
                return

            # 'q' and 'r' are commands only when the round is over —
            # during play they're valid letters to guess.
            if game.state != "playing":
                if key == "q":
                    return
                if key == "r":
                    game.reset()
                    draw_game(term, game)
                continue

            ks = str(key)
            if len(ks) == 1 and ks.isalpha():
                game.guess(ks)
                draw_game(term, game)
                continue
