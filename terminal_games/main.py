"""Terminal Games - Main menu launcher 🎮"""

import sys

from blessed import Terminal

from terminal_games.games.tetris import play_tetris
from terminal_games.games.snake import play_snake
from terminal_games.games.minesweeper import play_minesweeper
from terminal_games.games.twenty48 import play_twenty48
from terminal_games.games.wordle import play_wordle
from terminal_games.games.hangman import play_hangman

GAMES = [
    {
        "name": "Tetris",
        "icon": "🧱",
        "description": "Arrange falling blocks to clear lines",
        "play": play_tetris,
    },
    {
        "name": "Snake",
        "icon": "🐍",
        "description": "Eat food, grow longer, don't hit yourself",
        "play": play_snake,
    },
    {
        "name": "Minesweeper",
        "icon": "💣",
        "description": "Uncover tiles without hitting mines",
        "play": play_minesweeper,
    },
    {
        "name": "2048",
        "icon": "🎯",
        "description": "Slide and merge tiles to reach 2048",
        "play": play_twenty48,
    },
    {
        "name": "Wordle",
        "icon": "📝",
        "description": "Guess the 5-letter word in 6 tries",
        "play": play_wordle,
    },
    {
        "name": "Hangman",
        "icon": "🪢",
        "description": "Guess the word before the hangman is drawn",
        "play": play_hangman,
    },
]

TITLE_ART = r"""
 ______                    _             __   _____
/_  __/__  _________ ___  (_)___  ____ _/ /  / ___/____ _____ ___  ___  _____
 / / / _ \/ ___/ __ `__ \/ / __ \/ __ `/ /  / /  _ / __ `/ __ `__ \/ _ \/ ___/
/ / /  __/ /  / / / / / / / / / / /_/ / /  / /_/ / /_/ / / / / / /  __(__  )
/_/  \___/_/  /_/ /_/ /_/_/_/ /_/\__,_/_/   \____/\__,_/_/ /_/ /_/\___/____/
"""


def draw_menu(term: Terminal, selected: int) -> None:
    """Draw the main menu screen."""
    print(term.home + term.clear)

    # Get terminal dimensions
    width = term.width
    height = term.height

    # Draw title
    title_lines = TITLE_ART.strip().split("\n")
    title_start_y = max(1, (height // 2) - len(title_lines) - len(GAMES) - 3)

    for i, line in enumerate(title_lines):
        x = max(0, (width - len(line)) // 2)
        print(term.move_xy(x, title_start_y + i) + term.bold + term.cyan + line + term.normal)

    # Subtitle
    subtitle = "🎮  Classic Mini Games for your Terminal  🎮"
    x = max(0, (width - len(subtitle)) // 2)
    print(term.move_xy(x, title_start_y + len(title_lines) + 1) + term.dim + subtitle + term.normal)

    # Draw game list
    menu_start_y = title_start_y + len(title_lines) + 4

    for i, game in enumerate(GAMES):
        icon = game["icon"]
        name = game["name"]
        desc = game["description"]

        if i == selected:
            line = f"  ▸ {icon}  {name}  -  {desc}  "
            styled = term.bold + term.black_on_white + line + term.normal
        else:
            line = f"    {icon}  {name}  -  {desc}  "
            styled = term.dim + line + term.normal

        x = max(0, (width - len(line)) // 2)
        print(term.move_xy(x, menu_start_y + i * 2) + styled)

    # Footer
    footer_y = menu_start_y + len(GAMES) * 2 + 2
    controls = "↑/↓ Navigate  •  Enter Select  •  q Quit"
    x = max(0, (width - len(controls)) // 2)
    print(term.move_xy(x, footer_y) + term.dim + controls + term.normal)

    version_text = "v0.1.0"
    print(term.move_xy(width - len(version_text) - 2, height - 1) + term.dim + version_text + term.normal)


def main() -> None:
    """Main entry point for terminal-games."""
    term = Terminal()
    selected = 0

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        draw_menu(term, selected)

        while True:
            key = term.inkey(timeout=None)

            if key.name == "KEY_UP" or key == "k":
                selected = (selected - 1) % len(GAMES)
                draw_menu(term, selected)

            elif key.name == "KEY_DOWN" or key == "j":
                selected = (selected + 1) % len(GAMES)
                draw_menu(term, selected)

            elif key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                # Launch the selected game
                game = GAMES[selected]
                try:
                    game["play"](term)
                except Exception as e:
                    # If a game crashes, show error and return to menu
                    print(term.home + term.clear)
                    print(term.move_xy(2, 2) + term.red + f"Game error: {e}" + term.normal)
                    print(term.move_xy(2, 4) + "Press any key to return to menu...")
                    term.inkey(timeout=None)

                # Redraw menu after returning from game
                draw_menu(term, selected)

            elif key == "q" or key.name == "KEY_ESCAPE":
                # Goodbye message
                print(term.home + term.clear)
                goodbye = "Thanks for playing! 🎮"
                x = max(0, (term.width - len(goodbye)) // 2)
                y = term.height // 2
                print(term.move_xy(x, y) + term.bold + term.cyan + goodbye + term.normal)
                print(term.move_xy(0, y + 2))
                break


if __name__ == "__main__":
    main()
