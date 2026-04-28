"""Bundled word lists used by the word-based games.

Loaders are cached so the .txt files are only parsed once per process.
Files are shipped inside the wheel under ``terminal_games/data/`` and
loaded via :mod:`importlib.resources` so they work no matter how the
package is installed (pip, pipx, uvx, brew, source).

See :file:`LICENSES_DATA.md` at the repo root for the source and
license of each bundled list.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files


def _load(filename: str) -> tuple[str, ...]:
    """Read a newline-delimited word list bundled with the package."""
    text = files(__package__).joinpath(filename).read_text(encoding="utf-8")
    return tuple(line.strip() for line in text.splitlines() if line.strip())


@lru_cache(maxsize=1)
def common_words() -> tuple[str, ...]:
    """Top-frequency English words (4–12 letters, lowercase, alphabetic).

    Sourced from `first20hours/google-10000-english` (MIT). Suitable for
    Hangman and as the answer pool for Wordle (filtered to 5 letters).
    """
    return _load("words_common.txt")


@lru_cache(maxsize=1)
def valid_5letter_guesses() -> frozenset[str]:
    """All 5-letter English words from `dwyl/english-words` (Unlicense).

    Used by Wordle to validate guesses so any real 5-letter word is
    accepted, not only words from the smaller answer pool.
    """
    return frozenset(_load("words_5letter_valid.txt"))
