# 🎮 Terminal Games

A collection of classic mini games you can play right in your terminal! Built with Python and the `blessed` library for a smooth, colorful terminal UI experience.

[![PyPI version](https://img.shields.io/pypi/v/terminal-games?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/terminal-games/)
![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

---

## 🕹️ Games Included

### 🧱 Tetris
The classic falling blocks puzzle game! Arrange tetrominoes to complete lines and score points. Features ghost pieces, next piece preview, NES-style scoring, and increasing difficulty.

| Key | Action |
|-----|--------|
| `← →` or `A/D` | Move piece left/right |
| `↑` or `W` | Rotate piece |
| `↓` or `S` | Soft drop |
| `Space` | Hard drop |
| `P` | Pause |
| `Q` | Quit to menu |

### 🐍 Snake
Navigate the snake to eat food and grow longer — but don't run into the walls or yourself! Features bonus food, speed progression, and a gradient snake body.

| Key | Action |
|-----|--------|
| `← → ↑ ↓` or `WASD` | Change direction |
| `P` | Pause |
| `Q` | Quit to menu |

### 💣 Minesweeper
The timeless puzzle of logic and deduction. Uncover cells without detonating any mines! Features three difficulty levels, flagging, chording, and flood-fill reveal.

| Key | Action |
|-----|--------|
| `← → ↑ ↓` or `WASD` | Move cursor |
| `Space` / `Enter` | Reveal cell (or chord) |
| `F` | Flag / unflag cell |
| `C` | Chord (auto-reveal neighbors) |
| `R` | Restart / new game |
| `Q` | Quit to menu |

### 🎯 2048
Slide tiles on a 4×4 grid to combine matching numbers and reach the elusive 2048 tile! Features colorful tiles, score tracking, best score persistence within session, and the option to keep playing beyond 2048.

| Key | Action |
|-----|--------|
| `← → ↑ ↓` or `WASD` | Slide tiles |
| `R` | Restart game |
| `C` | Continue playing (after reaching 2048) |
| `Q` | Quit to menu |

### 📝 Wordle
The viral word-guessing game in your terminal! You have 6 tries to guess a hidden 5-letter word. After each guess, letters light up green (right letter, right spot), yellow (right letter, wrong spot), or grey (not in the word). An on-screen keyboard tracks the letters you've already used.

| Key | Action |
|-----|--------|
| `A-Z` | Type a letter (yes, including `Q` and `R`) |
| `Enter` | Submit guess |
| `Backspace` | Delete last letter |
| `Esc` | Quit to menu |
| `R` *(after round ends)* | New word |
| `Q` *(after round ends)* | Quit to menu |

---

## 📦 Installation

### Quick Play (No Install)

The fastest way to play — runs directly without installing anything permanently:

```sh
# Using uvx (recommended, requires uv)
uvx terminal-games

# Using pipx
pipx run terminal-games
```

### Install with pip

```sh
pip install terminal-games
terminal-games
```

### Install with pipx (Isolated Environment)

```sh
pipx install terminal-games
terminal-games
```

### Install with uv

```sh
uv tool install terminal-games
terminal-games
```

### Install from Source

```sh
# Clone the repository
git clone https://github.com/ayu5h-raj/terminal-games.git
cd terminal-games

# Run directly with uv (no install needed)
uv run terminal-games

# Or install in a virtual environment
uv sync
uv run terminal-games
```

### Install with Homebrew 🍺

```sh
brew tap ayu5h-raj/tap
brew install terminal-games
```

---

## 🚀 Usage

After installation, simply run:

```sh
terminal-games
```

You can also run it as a Python module:

```sh
python -m terminal_games
```

You'll be greeted with a beautiful menu where you can select any game using the arrow keys and Enter:

```
 ______                    _             __   _____
/_  __/__  _________ ___  (_)___  ____ _/ /  / ___/____ _____ ___  ___  _____
 / / / _ \/ ___/ __ `__ \/ / __ \/ __ `/ /  / /  _ / __ `/ __ `__ \/ _ \/ ___/
/ / /  __/ /  / / / / / / / / / / /_/ / /  / /_/ / /_/ / / / / / /  __(__  )
/_/  \___/_/  /_/ /_/ /_/_/_/ /_/\__,_/_/   \____/\__,_/_/ /_/ /_/\___/____/

                🎮  Classic Mini Games for your Terminal  🎮

                ▸ 🧱  Tetris  -  Arrange falling blocks to clear lines
                  🐍  Snake   -  Eat food, grow longer, don't hit yourself
                  💣  Minesweeper  -  Uncover tiles without hitting mines
                  🎯  2048    -  Slide and merge tiles to reach 2048

              ↑/↓ Navigate  •  Enter Select  •  q Quit
```

---

## 🛠️ Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setting Up the Dev Environment

```sh
# Clone the repo
git clone https://github.com/ayu5h-raj/terminal-games.git
cd terminal-games

# Install dependencies
uv sync

# Run the game
uv run terminal-games

# Or run as a module
uv run python -m terminal_games
```

### Project Structure

```
terminal-games/
├── pyproject.toml              # Project config & dependencies
├── README.md                   # You're reading this!
├── LICENSE                     # MIT License
├── LICENSES_DATA.md            # Provenance & licenses for bundled word lists
├── terminal_games/
│   ├── __init__.py             # Package init
│   ├── __main__.py             # python -m support
│   ├── main.py                 # Menu launcher & entry point
│   ├── data/                   # Bundled word lists (shipped in the wheel)
│   │   ├── __init__.py         # importlib.resources loaders (cached)
│   │   ├── words_common.txt    # ~8.3K common English words
│   │   └── words_5letter_valid.txt  # ~16K 5-letter words (Wordle validation)
│   └── games/
│       ├── __init__.py         # Games package
│       ├── tetris.py           # 🧱 Tetris
│       ├── snake.py            # 🐍 Snake
│       ├── minesweeper.py      # 💣 Minesweeper
│       ├── twenty48.py         # 🎯 2048
│       └── wordle.py           # 📝 Wordle
```

### Adding a New Game

1. Create a new file in `terminal_games/games/` (e.g., `pong.py`)
2. Implement a `play_pong(term: Terminal) -> None` function
3. Add it to the `GAMES` list in `terminal_games/main.py`
4. That's it! The menu will pick it up automatically.

---

## 🗺️ Roadmap

- [x] 🧱 Tetris
- [x] 🐍 Snake
- [x] 💣 Minesweeper
- [x] 🎯 2048
- [x] 📝 Wordle
- [ ] 🪢 Hangman
- [ ] 🏓 Pong
- [ ] 🃏 Blackjack
- [ ] 🏃 Flappy Bird
- [ ] 🚀 Space Invaders
- [ ] 🏰 Text Adventure
- [ ] 🏆 Global high scores
- [ ] 🎨 Custom themes
- [ ] 📦 Homebrew formula

---

## 📋 Requirements

- **Terminal size:** At least 80×24 (standard terminal size). Larger terminals provide a better experience.
- **Python:** 3.12 or newer
- **OS:** macOS, Linux, or Windows (Windows Terminal recommended)
- **Dependencies:** `blessed` (installed automatically)

---

## 🤝 Contributing

Contributions are welcome! Whether it's a new game, bug fix, or UI improvement:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-game`)
3. Commit your changes (`git commit -m 'Add awesome new game'`)
4. Push to the branch (`git push origin feature/new-game`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 💖 Acknowledgments

- Built with [blessed](https://github.com/jquast/blessed) — a thin, practical wrapper around terminal capabilities
- Inspired by the classic games we all grew up playing
- Managed with [uv](https://docs.astral.sh/uv/) — an extremely fast Python package manager
- Word lists bundled from [`first20hours/google-10000-english`](https://github.com/first20hours/google-10000-english) (MIT) and [`dwyl/english-words`](https://github.com/dwyl/english-words) (Unlicense). See [LICENSES_DATA.md](LICENSES_DATA.md) for details.

---

<p align="center">
  Made with ❤️ and Python 🐍
  <br>
  <strong>Happy Gaming! 🎮</strong>
</p>