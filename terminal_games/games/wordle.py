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
from typing import Literal

from blessed import Terminal

WORD_LENGTH = 5
MAX_GUESSES = 6
CELL_WIDTH = 5
ROW_GAP = 1
COL_GAP = 1

LetterStatus = Literal["correct", "present", "absent"]

# Curated set of common 5-letter English words. Used both as the target pool
# and the valid-guess set. Inline keeps the package dependency-free.
WORDS: tuple[str, ...] = (
    "about", "above", "abuse", "actor", "adapt", "admit", "adopt", "adult",
    "after", "again", "agent", "agree", "ahead", "alarm", "album", "alert",
    "alien", "alike", "alive", "allow", "alone", "along", "alpha", "alter",
    "among", "anger", "angle", "angry", "ankle", "apart", "apple", "apply",
    "arena", "argue", "arise", "armor", "array", "arrow", "aside", "asset",
    "audio", "audit", "avoid", "awake", "award", "aware",
    "badge", "badly", "baker", "basic", "basis", "batch", "beach", "beard",
    "beast", "began", "begin", "being", "below", "bench", "berry", "birth",
    "black", "blade", "blame", "blank", "blast", "bleed", "blend", "bless",
    "blind", "blink", "block", "blood", "bloom", "blown", "board", "boast",
    "bonus", "boost", "booth", "bound", "brain", "brake", "brand", "brass",
    "brave", "bread", "break", "breed", "brick", "brief", "bring", "brink",
    "broad", "broke", "brown", "brush", "build", "built", "bunch", "burst",
    "buyer",
    "cabin", "cable", "candy", "cargo", "carry", "catch", "cause", "cease",
    "chain", "chair", "chalk", "chaos", "charm", "chart", "chase", "cheap",
    "cheat", "check", "cheek", "cheer", "chess", "chest", "chick", "chief",
    "child", "chime", "chips", "choke", "chose", "civic", "civil", "claim",
    "clamp", "clash", "class", "clean", "clear", "clerk", "click", "cliff",
    "climb", "cling", "clock", "clone", "close", "cloth", "cloud", "clown",
    "coach", "coast", "comet", "comic", "couch", "cough", "could", "count",
    "court", "cover", "crack", "craft", "crane", "crash", "crate", "crazy",
    "cream", "crest", "crime", "crisp", "cross", "crowd", "crown", "crude",
    "cruel", "crumb", "crush", "curve", "cycle",
    "daily", "dairy", "dance", "dated", "dealt", "death", "debit", "debug",
    "debut", "decay", "decor", "delay", "delta", "dense", "depth", "devil",
    "diary", "dirty", "ditch", "diver", "dizzy", "dough", "dozen", "draft",
    "drain", "drama", "drank", "drawn", "dream", "dress", "dried", "drier",
    "drift", "drill", "drink", "drive", "drone", "drove", "drown", "dryer",
    "dummy", "dwell",
    "eager", "eagle", "early", "earth", "eaten", "ebony", "eight", "elbow",
    "elder", "elect", "elite", "email", "ember", "empty", "enact", "enemy",
    "enjoy", "enter", "entry", "equal", "error", "essay", "event", "every",
    "exact", "excel", "exist", "extra",
    "fairy", "faith", "false", "fancy", "fatal", "fault", "favor", "feast",
    "fence", "ferry", "fetch", "fever", "fiber", "field", "fifth", "fifty",
    "fight", "final", "finer", "first", "fixed", "flair", "flame", "flash",
    "flask", "fleet", "flesh", "flick", "fling", "flint", "float", "flock",
    "flood", "floor", "flour", "flown", "fluid", "flung", "focal", "focus",
    "foggy", "force", "forge", "forth", "forty", "forum", "found", "frail",
    "frame", "fraud", "fresh", "fried", "frock", "front", "frost", "frown",
    "froze", "fruit", "fully", "funny",
    "games", "gauge", "gaunt", "ghost", "giant", "given", "giver", "gland",
    "glare", "glass", "gleam", "globe", "gloom", "glory", "gloss", "glove",
    "going", "goods", "grace", "grade", "grain", "grand", "grant", "grape",
    "graph", "grasp", "grass", "grave", "gravy", "great", "greed", "green",
    "greet", "grief", "grill", "grime", "grind", "gripe", "gross", "group",
    "grove", "grown", "gruff", "grunt", "guard", "guess", "guest", "guide",
    "guild", "guilt", "guise",
    "habit", "hairy", "halve", "handy", "happy", "hardy", "harsh", "haste",
    "hatch", "haunt", "haven", "havoc", "heart", "heavy", "hedge", "hefty",
    "helix", "hello", "hence", "hilly", "hinge", "hippo", "hoard", "hobby",
    "hoist", "holly", "honey", "honor", "horde", "horse", "hotel", "hound",
    "house", "hover", "human", "humid", "humor", "hunch", "hurry", "husky",
    "icily", "icing", "ideal", "idiom", "igloo", "image", "imply", "inbox",
    "index", "inert", "infer", "ingot", "inlay", "inner", "input", "intro",
    "irate", "irony", "issue", "ivory",
    "jaunt", "jelly", "jerky", "jewel", "jiffy", "joint", "joker", "jolly",
    "joust", "judge", "juice", "juicy", "jumpy", "junky", "juror",
    "kayak", "kebab", "kiosk", "knack", "knead", "kneel", "knelt", "knife",
    "knock", "knoll", "known", "koala", "kudos",
    "label", "labor", "laden", "ladle", "lager", "lance", "lanky", "lapel",
    "lapse", "large", "larva", "lasso", "latch", "later", "latex", "laugh",
    "layer", "leaky", "leant", "leapt", "learn", "lease", "leash", "least",
    "leech", "legal", "lemon", "level", "lever", "light", "liked", "limit",
    "lined", "liner", "linen", "lipid", "liver", "llama", "lobby", "local",
    "lodge", "lofty", "logic", "login", "loins", "loose", "lorry", "loser",
    "loved", "lover", "lower", "loyal", "lucid", "lucky", "lumpy", "lunar",
    "lunch", "lunge", "lurid", "lusty", "lying", "lyric",
    "macho", "madly", "madam", "magic", "major", "maker", "mango", "manor",
    "maple", "march", "marry", "marsh", "mason", "match", "maybe", "mayor",
    "meals", "means", "meant", "meaty", "medal", "media", "melon", "mercy",
    "merge", "merit", "merry", "metal", "meter", "micro", "might", "mimic",
    "minor", "minus", "mirth", "miser", "mixed", "mixer", "modal", "model",
    "modem", "money", "month", "moody", "moose", "moral", "motel", "motor",
    "mount", "mourn", "mouse", "mouth", "movie", "mover", "mower", "muddy",
    "mummy", "music",
    "naive", "naked", "nanny", "nasal", "nasty", "naval", "needy", "nerve",
    "never", "newer", "newly", "nicer", "niche", "niece", "night", "ninth",
    "noble", "nodal", "noise", "noisy", "nomad", "north", "nosey", "notch",
    "novel", "nudge", "nurse", "nutty", "nylon", "nymph",
    "ocean", "octal", "octet", "odder", "oddly", "offer", "often", "older",
    "olive", "omega", "onion", "onset", "opera", "opted", "optic", "orbit",
    "organ", "other", "otter", "ought", "ounce", "outer", "ovary", "overt",
    "owing", "owner", "oxide",
    "pager", "pages", "paint", "panda", "panel", "panic", "paper", "party",
    "paste", "patch", "patio", "peace", "peach", "pearl", "pedal", "peers",
    "penal", "perch", "peril", "perky", "petal", "petty", "phase", "phone",
    "photo", "piano", "picky", "piece", "piety", "piggy", "pilot", "pinch",
    "pinky", "pious", "pitch", "pithy", "pivot", "pixel", "pizza", "place",
    "plain", "plane", "plank", "plant", "plate", "plays", "plead", "pleat",
    "pluck", "plumb", "plume", "plump", "plush", "point", "polar", "polka",
    "poppy", "porch", "posed", "pouch", "pound", "power", "prank", "press",
    "price", "prick", "pride", "prime", "print", "prior", "prism", "prize",
    "probe", "prone", "prong", "proof", "prose", "proud", "prove", "prowl",
    "proxy", "prune", "psalm", "pulse", "punch", "pupil", "puppy", "purer",
    "purge", "purse", "pushy", "putty",
    "quack", "quail", "quake", "qualm", "quart", "quash", "queen", "queer",
    "query", "quest", "queue", "quick", "quiet", "quill", "quilt", "quirk",
    "quite", "quota", "quote",
    "rabid", "racer", "radar", "radio", "rainy", "rally", "ranch", "range",
    "rapid", "ratio", "raven", "reach", "ready", "realm", "rebel", "recap",
    "refer", "regal", "reign", "relax", "relay", "relic", "renal", "renew",
    "repay", "repel", "reply", "resin", "retro", "reuse", "rhino", "rhyme",
    "rider", "ridge", "rifle", "right", "rigid", "ripen", "rival", "river",
    "roach", "roast", "robin", "robot", "rocky", "rodeo", "rogue", "roman",
    "roost", "rough", "round", "rouse", "route", "royal", "rugby", "ruler",
    "rural", "rusty",
    "saber", "sable", "sadly", "safer", "saint", "salad", "sales", "salon",
    "salty", "salve", "sandy", "satin", "sauce", "saucy", "sauna", "saved",
    "scale", "scalp", "scaly", "scant", "scare", "scarf", "scary", "scene",
    "scent", "scion", "scoff", "scold", "scoop", "scope", "score", "scorn",
    "scour", "scout", "scowl", "scrap", "scrub", "scuba", "sedan", "seedy",
    "seize", "sense", "serum", "serve", "setup", "seven", "sever", "shack",
    "shade", "shady", "shaft", "shake", "shaky", "shale", "shall", "shame",
    "shape", "share", "shark", "sharp", "shave", "shawl", "shear", "sheen",
    "sheep", "sheer", "sheet", "shelf", "shell", "shied", "shift", "shine",
    "shiny", "shire", "shirk", "shirt", "shoal", "shock", "shone", "shoot",
    "shore", "short", "shout", "shove", "shown", "showy", "shred", "shrew",
    "shrub", "shrug", "shuck", "shunt", "shyly", "siege", "sieve", "sight",
    "sigma", "silly", "since", "siren", "sissy", "sixth", "sized", "skate",
    "skier", "skill", "skimp", "skull", "skunk", "slack", "slain", "slang",
    "slant", "slash", "slate", "sleek", "sleep", "sleet", "slept", "slice",
    "slick", "slide", "slime", "slimy", "sling", "slink", "sloop", "slope",
    "slosh", "sloth", "slump", "slung", "slyly", "smack", "small", "smart",
    "smash", "smear", "smell", "smile", "smirk", "smoke", "smoky", "snack",
    "snake", "snare", "snarl", "sneak", "sneer", "snide", "sniff", "snipe",
    "snore", "snort", "snout", "snowy", "soapy", "sober", "soggy", "solar",
    "solid", "solve", "sonar", "sonic", "sorry", "sound", "south", "space",
    "spade", "spank", "spare", "spark", "spasm", "spawn", "speak", "spear",
    "speck", "speed", "spell", "spelt", "spend", "spent", "sperm", "spice",
    "spicy", "spied", "spike", "spiky", "spill", "spine", "spire", "spite",
    "splat", "split", "spoil", "spoke", "spoof", "spool", "spoon", "sport",
    "spout", "spray", "spree", "sprig", "spunk", "spurn", "spurt", "squad",
    "squat", "stack", "staff", "stage", "stain", "stair", "stake", "stale",
    "stalk", "stall", "stamp", "stand", "stank", "stare", "stark", "start",
    "stash", "state", "steak", "steal", "steam", "steed", "steel", "steep",
    "steer", "stein", "stern", "stick", "stiff", "still", "stilt", "sting",
    "stink", "stint", "stock", "stoic", "stoke", "stole", "stomp", "stone",
    "stony", "stood", "stool", "stoop", "store", "stork", "storm", "story",
    "stout", "stove", "strap", "straw", "stray", "strip", "strut", "stuck",
    "study", "stuff", "stump", "stung", "stunk", "stunt", "style", "suave",
    "sugar", "suing", "suite", "sulky", "sully", "sunny", "super", "surge",
    "surly", "sushi", "swamp", "swarm", "swath", "swear", "sweat", "sweep",
    "sweet", "swell", "swept", "swift", "swill", "swine", "swing", "swirl",
    "swish", "sworn", "swung", "syrup",
    "table", "taboo", "tacit", "tacky", "taint", "taken", "taker", "tales",
    "tally", "tamed", "tango", "tangy", "tarot", "tarry", "taste", "tasty",
    "taunt", "tawny", "teach", "teams", "teary", "teddy", "teeth", "tempo",
    "tempt", "tenor", "tense", "tepid", "terms", "terse", "testy", "thank",
    "theft", "their", "theme", "there", "these", "theta", "thick", "thief",
    "thigh", "thine", "thing", "think", "third", "thong", "thorn", "those",
    "three", "threw", "throb", "throw", "thumb", "thump", "thyme", "tiara",
    "tibia", "tidal", "tiger", "tight", "tilde", "timer", "timid", "tipsy",
    "tired", "titan", "toast", "today", "token", "tonal", "tonic", "tooth",
    "topaz", "topic", "torch", "torso", "total", "totem", "touch", "tough",
    "towel", "tower", "toxic", "toxin", "trace", "track", "tract", "trade",
    "trail", "train", "trait", "tramp", "trash", "tread", "treat", "trend",
    "triad", "trial", "tribe", "trick", "tried", "tries", "trill", "tripe",
    "trite", "troll", "troop", "trope", "trout", "trove", "truce", "truck",
    "truly", "trump", "trunk", "truss", "trust", "truth", "tryst", "tuber",
    "tulip", "tumor", "tunic", "turbo", "tutor", "twang", "tweak", "tweed",
    "tweet", "twice", "twine", "twirl", "twist", "tying",
    "udder", "ulcer", "ultra", "umbra", "uncle", "uncut", "under", "undid",
    "undue", "unfit", "unify", "union", "unite", "unity", "until", "upper",
    "upset", "urban", "usage", "usher", "using", "usual", "usurp", "utter",
    "vague", "valet", "valid", "valor", "value", "valve", "vapor", "vault",
    "vegan", "venom", "venue", "verge", "verse", "video", "vigil", "vigor",
    "villa", "vinyl", "viola", "viper", "viral", "virus", "visit", "visor",
    "vista", "vital", "vivid", "vixen", "vocal", "vodka", "vogue", "voice",
    "vouch", "vowel",
    "wafer", "wager", "wagon", "waist", "waltz", "waste", "watch", "water",
    "waver", "weary", "weave", "wedge", "weedy", "weigh", "weird", "whack",
    "whale", "wharf", "wheat", "wheel", "where", "which", "whiff", "while",
    "whine", "whirl", "whisk", "white", "whole", "whoop", "whose", "widen",
    "wider", "widow", "width", "wield", "wince", "winch", "windy", "wings",
    "wiped", "wires", "wiser", "witch", "witty", "woman", "women", "woody",
    "woozy", "wordy", "world", "worry", "worse", "worst", "worth", "would",
    "wound", "woven", "wreck", "wrest", "wring", "wrist", "write", "wrong",
    "wrote", "wrung", "wryly",
    "yacht", "yards", "yearn", "yeast", "yield", "yodel", "young", "yours",
    "youth", "yummy",
    "zebra", "zesty", "zonal",
)

WORD_SET: frozenset[str] = frozenset(WORDS)

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
        self.target = random.choice(WORDS)
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
        if self.current not in WORD_SET:
            return (False, "Not in word list")

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
    text = f"  {label}  "  # 5 chars when label is 1 char (or space)
    text = text[:CELL_WIDTH].ljust(CELL_WIDTH)

    if status is not None:
        return _cell_style(term, status) + text + term.normal

    # Unsubmitted cell — bright if there's a letter (current row), dim otherwise.
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
    keyboard_height = len(KEYBOARD_ROWS) + (len(KEYBOARD_ROWS) - 1) * 0  # 1-line rows
    total_height = 2 + 1 + grid_height + 2 + keyboard_height + 2  # title + header + grid + flash + keyboard + controls

    start_y = max(1, (term.height - total_height) // 2)

    # Title
    title = "📝  W O R D L E  📝"
    title_x = max(0, (term.width - len(title)) // 2)
    output.append(term.move_xy(title_x, start_y) + term.bold + term.bright_yellow + title + term.normal)

    # Header (status / guess count)
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

    # Grid
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

    # Flash error message
    flash_y = grid_y + grid_height + 1
    if game.flash:
        fx = max(0, (term.width - len(game.flash)) // 2)
        output.append(term.move_xy(fx, flash_y) + term.bold + term.bright_red + game.flash + term.normal)

    # On-screen keyboard
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

    # Footer controls
    controls_y = kb_y + len(KEYBOARD_ROWS) + 1
    if game.state == "playing":
        controls = "A-Z type  •  ENTER submit  •  ⌫ delete  •  r restart  •  q quit"
    else:
        controls = "r: new word  •  q: quit to menu"
    cx = max(0, (term.width - len(controls)) // 2)
    output.append(term.move_xy(cx, controls_y) + term.dim + controls + term.normal)

    # Game-over reveal (under controls so we don't cover the grid)
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

            if key == "q" or key.name == "KEY_ESCAPE":
                return

            if key == "r":
                game.reset()
                draw_game(term, game)
                continue

            if game.state != "playing":
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

            # Letter input
            ks = str(key)
            if len(ks) == 1 and ks.isalpha():
                game.add_letter(ks)
                draw_game(term, game)
                continue

            if had_flash:
                draw_game(term, game)
