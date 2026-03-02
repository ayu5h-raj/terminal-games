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
├── terminal_games/
│   ├── __init__.py             # Package init
│   ├── __main__.py             # python -m support
│   ├── main.py                 # Menu launcher & entry point
│   └── games/
│       ├── __init__.py         # Games package
│       ├── tetris.py           # 🧱 Tetris
│       ├── snake.py            # 🐍 Snake
│       └── minesweeper.py      # 💣 Minesweeper
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
- [ ] 🏓 Pong
- [ ] 🃏 Blackjack
- [ ] 🎯 2048
- [ ] 🔤 Hangman
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

---

<p align="center">
  Made with ❤️ and Python 🐍
  <br>
  <strong>Happy Gaming! 🎮</strong>
</p>