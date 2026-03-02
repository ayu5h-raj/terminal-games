# Agent Instructions for Terminal Games

This file contains instructions for AI coding agents working on this project.

## Project Overview

Terminal Games is a collection of classic mini games you can play right in your terminal. Built with Python and the `blessed` library for smooth, colorful terminal UI.

## Tech Stack

- **Language**: Python 3.12+
- **Terminal UI**: blessed (thin wrapper around terminal capabilities)
- **Package Manager**: uv
- **Build Backend**: hatchling
- **Distribution**: PyPI, Homebrew, pipx, uvx

## Project Structure

```
terminal-games/
├── pyproject.toml              # Project config, dependencies & entry point
├── README.md                   # User-facing documentation
├── LICENSE                     # MIT License
├── CLAUDE.md                   # This file — agent instructions
├── .github/
│   └── workflows/
│       └── publish.yml         # Auto-publish to PyPI + update Homebrew
├── terminal_games/
│   ├── __init__.py             # Package init (__version__)
│   ├── __main__.py             # python -m terminal_games support
│   ├── main.py                 # Menu launcher & entry point
│   └── games/
│       ├── __init__.py         # Games package
│       ├── tetris.py           # 🧱 Tetris
│       ├── snake.py            # 🐍 Snake
│       ├── minesweeper.py      # 💣 Minesweeper
│       └── twenty48.py         # 🎯 2048
```

## Key Architecture Decisions

1. **blessed over curses**: Cross-platform terminal UI. Works on macOS, Linux, and Windows without extra dependencies.
2. **Single entry point**: All games launch from a menu in `main.py`. The `GAMES` list drives the menu.
3. **Game function signature**: Every game exposes a `play_<name>(term: Terminal) -> None` function. The menu calls it and redraws when it returns.
4. **Full-screen rendering**: Each game uses `term.fullscreen()`, `term.cbreak()`, and `term.hidden_cursor()` context managers.
5. **Flicker-free drawing**: All output is built as a list of strings, joined, and printed in a single `print()` call.
6. **Non-blocking input**: Games use `term.inkey(timeout=...)` for responsive input without blocking the game loop.

## Running the Project

```bash
# Install dependencies
uv sync

# Run the game
uv run terminal-games

# Or run as a Python module
uv run python -m terminal_games
```

## Coding Standards

- Use type hints for all function signatures
- Follow PEP 8 conventions
- Use `from __future__ import annotations` if needed for forward references
- Keep game logic separate from rendering (engine class + draw function pattern)
- **ALWAYS create separate branches for features and fixes** — never commit directly to main
- Use conventional commit messages

## Adding a New Game

1. Create a new file in `terminal_games/games/` (e.g., `pong.py`)
2. Implement the game with this pattern:
   ```python
   """Pong - Classic paddle game 🏓

   Controls:
       ...
   """
   from blessed import Terminal

   class PongGame:
       """Game engine — pure logic, no rendering."""
       def __init__(self):
           ...

   def draw_game(term: Terminal, game: PongGame) -> None:
       """Render game state to terminal."""
       output = []
       output.append(term.home + term.clear)
       # ... build output ...
       print("".join(output), end="", flush=True)

   def play_pong(term: Terminal) -> None:
       """Main game loop."""
       game = PongGame()
       with term.fullscreen(), term.cbreak(), term.hidden_cursor():
           draw_game(term, game)
           while True:
               key = term.inkey(timeout=0.03)
               if key == "q" or key.name == "KEY_ESCAPE":
                   return
               # ... handle input, tick, draw ...
   ```
3. Add the import and entry to the `GAMES` list in `terminal_games/main.py`:
   ```python
   from terminal_games.games.pong import play_pong

   GAMES = [
       # ... existing games ...
       {
           "name": "Pong",
           "icon": "🏓",
           "description": "Classic paddle and ball game",
           "play": play_pong,
       },
   ]
   ```
4. That's it — the menu picks it up automatically.

## Game Development Guidelines

### Input Handling
- Always support both arrow keys AND WASD
- Use `term.inkey(timeout=...)` — short timeout (0.02-0.05s) for action games, longer (0.5s) for turn-based
- Always provide `q` or `ESC` to quit back to menu
- Support `p` for pause in real-time games
- Support `r` for restart on game over screens

### Rendering
- Use `CELL_WIDTH = 2` for square-looking cells (terminal characters are taller than wide)
- Build all output as a list, join and print once to avoid flicker
- Center the game board based on `term.width` and `term.height`
- Use box-drawing characters for borders: `╔ ═ ╗ ║ ╚ ╝`
- Use `term.bold`, `term.dim`, `term.normal` for emphasis
- Use color via `term.cyan`, `term.red`, `term.green`, etc.

### Game State
- Separate game engine (logic) from rendering (display)
- Use a game class to hold all state
- Implement `tick()` method for time-based updates
- Track score, level, and game_over state
- Support pause/resume

## Git Workflow

**CRITICAL**: Always create a separate branch for every feature or fix. Never commit directly to main.

1. Create feature branch:
   ```bash
   git checkout -b feature/feature-name
   # or
   git checkout -b fix/bug-name
   ```
2. Make changes and commit with conventional commits:
   - `feat:` for new features (new game, new UI element)
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `chore:` for version bumps, dependency updates
   - `ci:` for CI/CD changes
3. Push branch and create PR:
   ```bash
   git push -u origin feature/my-feature
   ```
4. After merge, bump version and create tag for release (see Release Process below)

## Release Process

### Version Bumping

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **PATCH** (0.1.1 → 0.1.2): Bug fixes, small improvements
- **MINOR** (0.1.2 → 0.2.0): New games, new features
- **MAJOR** (0.2.0 → 1.0.0): Breaking changes, major redesigns

When bumping version, update BOTH files:
1. `pyproject.toml` → `version = "X.X.X"` (line 3)
2. `terminal_games/__init__.py` → `__version__ = "X.X.X"`

### Creating a Release

1. Create version bump branch:
   ```bash
   git checkout -b chore/bump-version-X.X.X
   ```
2. Update version in `pyproject.toml` and `terminal_games/__init__.py`
3. Commit, push, and create PR:
   ```bash
   git add -A
   git commit -m "chore: bump version to X.X.X"
   git push -u origin chore/bump-version-X.X.X
   ```
4. After PR is merged to main, create and push tag:
   ```bash
   git checkout main
   git pull
   git tag vX.X.X
   git push origin vX.X.X
   ```
5. GitHub Actions will automatically:
   - 📦 Build and publish to PyPI (via trusted publishing)
   - ⏳ Wait for PyPI to index the new version
   - 🍺 Update Homebrew formula in `ayu5h-raj/homebrew-tap`

### Monitoring a Release

- Watch the workflow: https://github.com/ayu5h-raj/terminal-games/actions
- Verify PyPI: https://pypi.org/project/terminal-games/
- Verify Homebrew tap: https://github.com/ayu5h-raj/homebrew-tap/blob/main/Formula/terminal-games.rb

### Troubleshooting Release Issues

- **If tag already exists**: Delete and recreate it:
  ```bash
  git tag -d vX.X.X
  git push origin --delete vX.X.X
  git tag vX.X.X
  git push origin vX.X.X
  ```
- **PyPI publish fails**: Check that trusted publishing is configured at https://pypi.org/manage/project/terminal-games/settings/publishing/
  - Owner: `ayu5h-raj`
  - Repository: `terminal-games`
  - Workflow: `publish.yml`
  - Environment: `pypi`
- **Homebrew update fails**: Check that `HOMEBREW_TAP_TOKEN` secret is set in repo settings and the token has Contents (read & write) permission on the `homebrew-tap` repo.

## Distribution Channels

| Method | Command | How it works |
|--------|---------|--------------|
| **uvx** | `uvx terminal-games` | Runs from PyPI without installing |
| **pipx run** | `pipx run terminal-games` | Runs from PyPI without installing |
| **pip** | `pip install terminal-games` | Installs from PyPI |
| **pipx** | `pipx install terminal-games` | Isolated install from PyPI |
| **uv** | `uv tool install terminal-games` | Installs as uv tool |
| **Homebrew** | `brew tap ayu5h-raj/tap && brew install terminal-games` | Installs via Homebrew formula |
| **Source** | `git clone ... && uv run terminal-games` | Run from source |
| **Module** | `python -m terminal_games` | Run as Python module |

## Homebrew Tap

- Tap repo: `ayu5h-raj/homebrew-tap`
- Formula: `Formula/terminal-games.rb`
- Uses `Language::Python::Virtualenv` mixin
- Dependencies (blessed, wcwidth) are bundled as resources
- Auto-updated on release via the `publish.yml` workflow
- The workflow fetches latest SHA256 hashes from PyPI for all dependencies

## Secrets & Configuration

| Secret | Repository | Purpose |
|--------|-----------|---------|
| `HOMEBREW_TAP_TOKEN` | `terminal-games` | Fine-grained token with Contents (R/W) on `homebrew-tap` repo |
| PyPI Trusted Publishing | Configured on pypi.org | Allows `publish.yml` to publish without API tokens |
| `pypi` environment | `terminal-games` | GitHub environment required by trusted publishing |

## Files Overview

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, CLI entry point, build config |
| `terminal_games/__init__.py` | Package version (`__version__`) |
| `terminal_games/__main__.py` | Enables `python -m terminal_games` |
| `terminal_games/main.py` | Menu launcher, game registry, entry point |
| `terminal_games/games/tetris.py` | Tetris: 7-bag randomizer, wall kicks, ghost piece, NES scoring |
| `terminal_games/games/snake.py` | Snake: bonus food, speed progression, gradient body |
| `terminal_games/games/minesweeper.py` | Minesweeper: 3 difficulties, flagging, chording, flood fill |
| `terminal_games/games/twenty48.py` | 2048: slide & merge tiles, colorful styling, continue past 2048 |
| `.github/workflows/publish.yml` | CI/CD: PyPI publish + Homebrew formula update on tag push |

## Common Tasks

### Adding a new game
1. Create feature branch: `git checkout -b feature/game-name`
2. Create `terminal_games/games/game_name.py` following the pattern above
3. Add import and entry in `terminal_games/main.py`
4. Test locally: `uv run terminal-games`
5. Update `README.md` with game description and controls
6. Commit, push branch, and create PR

### Fixing a bug
1. Create fix branch: `git checkout -b fix/bug-name`
2. Fix the bug in the appropriate file
3. Test locally: `uv run terminal-games`
4. Commit, push branch, and create PR

### Making a release
1. Create version bump branch: `git checkout -b chore/bump-version-X.X.X`
2. Bump version in `pyproject.toml` and `terminal_games/__init__.py`
3. Push branch and create PR
4. After merge: `git checkout main && git pull && git tag vX.X.X && git push origin vX.X.X`
5. Monitor workflow at: https://github.com/ayu5h-raj/terminal-games/actions

### Testing installation methods locally
```bash
# Test pip install from local build
uv build && pip install dist/terminal_games-*.whl

# Test uvx with local package
uv run terminal-games

# Test python -m
uv run python -m terminal_games

# Test brew formula (after release)
brew tap ayu5h-raj/tap
brew install terminal-games
```
