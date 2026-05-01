"""Build the bundled Wordle answer + valid-guess lists.

Source: the original Wordle (Josh Wardle, MIT-licensed) word lists,
archived publicly before the NYT acquisition. The two lists are:

  1. ``wordle-answers-alphabetical.txt`` — 2,314 curated answer words.
  2. ``wordle-allowed-guesses.txt``      — 10,656 additional valid guesses.

We additionally apply a small blocklist of words NYT removed
post-acquisition for sensitivity reasons; running this script reproduces
``terminal_games/data/words_wordle_answers.txt`` and
``terminal_games/data/words_wordle_valid.txt`` exactly.

Usage::

    python3 scripts/build_wordle_answers.py
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

ANSWERS_URL = (
    "https://gist.githubusercontent.com/cfreshman/"
    "a03ef2cba789d8cf00c08f767e0fad7b/raw/"
    "wordle-answers-alphabetical.txt"
)
ALLOWED_URL = (
    "https://gist.githubusercontent.com/cfreshman/"
    "cdcdf777450c5b5301e439061d29694c/raw/"
    "wordle-allowed-guesses.txt"
)

# Words present in the original Wordle answer list that NYT explicitly
# removed post-acquisition (sensitivity / topicality). We mirror those
# removals so the bundled list matches a current, family-friendly Wordle.
#
# IMPORTANT — DAILY-MODE STABILITY: this set is FROZEN. Adding entries
# after the first release (v0.3.0) shifts the alphabetical index of every
# later word, which would silently change the answer for every past and
# future date in daily mode. If a future word truly must be retired, do
# it as an in-place edit of ``words_wordle_answers.txt`` that preserves
# pool length, or accept the date shift as a deliberate, version-bumped
# breaking change.
BLOCKLIST = frozenset({
    "agora",
    "bitch",
    "fetus",
    "harem",
    "lynch",
    "pussy",
    "slave",
    "whore",
    "wench",
})

FETCH_TIMEOUT_SECS = 30

DATA_DIR = Path(__file__).resolve().parent.parent / "terminal_games" / "data"


def _fetch(url: str) -> list[str]:
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT_SECS) as resp:
        text = resp.read().decode("utf-8")
    return [w.strip().lower() for w in text.splitlines() if w.strip()]


def main() -> None:
    answers = _fetch(ANSWERS_URL)
    allowed = _fetch(ALLOWED_URL)

    bad_answers = [w for w in answers if not (len(w) == 5 and w.isascii() and w.isalpha())]
    bad_allowed = [w for w in allowed if not (len(w) == 5 and w.isascii() and w.isalpha())]
    if bad_answers or bad_allowed:
        raise SystemExit(f"Unexpected entries: answers={bad_answers} allowed={bad_allowed}")

    cleaned_answers = sorted({w for w in answers if w not in BLOCKLIST})
    cleaned_valid = sorted(set(answers) | set(allowed))
    cleaned_valid = [w for w in cleaned_valid if w not in BLOCKLIST]

    answers_path = DATA_DIR / "words_wordle_answers.txt"
    valid_path = DATA_DIR / "words_wordle_valid.txt"
    answers_path.write_text("\n".join(cleaned_answers) + "\n", encoding="utf-8")
    valid_path.write_text("\n".join(cleaned_valid) + "\n", encoding="utf-8")

    removed = sorted(set(answers) & BLOCKLIST)
    print(f"Wrote {answers_path.relative_to(DATA_DIR.parent.parent)}: {len(cleaned_answers)} answers")
    print(f"Wrote {valid_path.relative_to(DATA_DIR.parent.parent)}: {len(cleaned_valid)} valid guesses")
    if removed:
        print(f"Filtered by blocklist: {', '.join(removed)}")


if __name__ == "__main__":
    main()
