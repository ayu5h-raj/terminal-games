# Bundled Data Licenses

This project ships four word-list data files inside the wheel under
`terminal_games/data/`. Each is derived from a third-party source and
retains its upstream license. This document records provenance and the
exact transformations applied so end users can audit what they are
installing.

| Bundled file | Source repository | Upstream file | Upstream license |
|---|---|---|---|
| `terminal_games/data/words_common.txt` | [`first20hours/google-10000-english`](https://github.com/first20hours/google-10000-english) | `google-10000-english.txt` | MIT |
| `terminal_games/data/words_5letter_valid.txt` | [`dwyl/english-words`](https://github.com/dwyl/english-words) | `words_alpha.txt` | The Unlicense (public domain) |
| `terminal_games/data/words_wordle_answers.txt` | Original Wordle source (Josh Wardle, pre-NYT) — archived at [`cfreshman` gist](https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b) | `wordle-answers-alphabetical.txt` | MIT |
| `terminal_games/data/words_wordle_valid.txt` | Original Wordle source (Josh Wardle, pre-NYT) — archived at [`cfreshman` gist](https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c) | `wordle-allowed-guesses.txt` ∪ answers | MIT |

## Transformations applied

For both files, the upstream content was filtered as follows. No words
were added; only filtering and de-duplication were applied.

### `words_common.txt`
- Started from `google-10000-english.txt` (10,000 words, frequency-sorted).
- Lowercased and stripped whitespace.
- Kept only entries that are pure ASCII alphabetic and 4–12 characters long.
- **Intersected with `dwyl/english-words/words_alpha.txt`** to drop entries
  that aren't in a real English dictionary — this removes web-frequency
  artifacts like "freebsd", "mediawiki", "javascript" that appear in the
  Google corpus but would feel wrong as a Hangman target word.
- Removed duplicates while preserving the first occurrence (so the file
  remains roughly frequency-sorted from most- to least-common).
- Result: ~8,319 words.

### `words_5letter_valid.txt`
- Started from `words_alpha.txt` (370,105 words).
- Lowercased and stripped whitespace.
- Kept only entries that are pure ASCII alphabetic and exactly 5 characters long.
- Sorted alphabetically and de-duplicated.
- Result: ~15,921 words.

### `words_wordle_answers.txt`
**Generated file — do not hand-edit.** Run `python3 scripts/build_wordle_answers.py`
to regenerate.
- Started from the original Wordle answer list (`wordle-answers-alphabetical.txt`,
  2,314 words), archived from the pre-NYT Wordle source (MIT-licensed).
- Removed a small sensitivity blocklist mirroring NYT's own post-acquisition
  removals: `agora`, `bitch`, `fetus`, `harem`, `lynch`, `pussy`, `slave`,
  `whore`, `wench`.
- Sorted alphabetically. **Treated as append-only** so the daily-mode word
  index for any given date stays stable across releases.
- Result: ~2,309 words.
- Build script: `scripts/build_wordle_answers.py`.

### `words_wordle_valid.txt`
**Generated file — do not hand-edit.** Run `python3 scripts/build_wordle_answers.py`
to regenerate.
- Union of the original Wordle answers (2,314) and the original Wordle
  allowed-guesses list (`wordle-allowed-guesses.txt`, 10,656 words), both
  archived from the pre-NYT Wordle source (MIT-licensed).
- Removed the same sensitivity blocklist as above.
- Sorted alphabetically and de-duplicated.
- Result: ~12,963 words.
- Build script: `scripts/build_wordle_answers.py`.

## License texts

### MIT (google-10000-english)

```
MIT License

Copyright (c) Josh Kaufman

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject
to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND...
```

Full text: <https://github.com/first20hours/google-10000-english/blob/master/LICENSE.md>

### The Unlicense (dwyl/english-words)

```
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means...
```

Full text: <https://unlicense.org/>

## Reproducing the filters

Both filtered files can be regenerated locally from the upstream sources
with the following commands (for transparency, not required for normal
usage):

```bash
curl -fsSL -o /tmp/google-10000-english.txt \
  https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt

curl -fsSL -o /tmp/dwyl-words-alpha.txt \
  https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt

python3 - <<'PY'
dictionary = {w.strip().lower() for w in open('/tmp/dwyl-words-alpha.txt')
              if w.strip().isascii() and w.strip().isalpha()}

seen = set(); common = []
for w in open('/tmp/google-10000-english.txt'):
    w = w.strip().lower()
    if not (4 <= len(w) <= 12): continue
    if not (w.isascii() and w.isalpha()): continue
    if w in seen: continue
    if w not in dictionary: continue   # drop brand names / non-dictionary entries
    common.append(w); seen.add(w)
with open('terminal_games/data/words_common.txt', 'w') as f:
    f.write('\n'.join(common) + '\n')

five = sorted({w.strip().lower() for w in open('/tmp/dwyl-words-alpha.txt')
               if len(w.strip()) == 5 and w.strip().isascii() and w.strip().isalpha()})
with open('terminal_games/data/words_5letter_valid.txt', 'w') as f:
    f.write('\n'.join(five) + '\n')
PY
```
