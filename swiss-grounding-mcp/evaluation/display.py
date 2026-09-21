#!/usr/bin/env python3
"""A bounded terminal Easter egg. Python standard library only."""

import argparse
import math
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import sys
import time


SCENES = (
    "Fondue particle accelerator", "Alpine radar", "Cantonal confetti",
    "Swiss cheese tomography", "Yodel spectrum", "Chocolate waterfall",
    "Raclette progress", "Mountain matrix", "Cowbell oscillator",
    "Direct democracy disco",
)


def bounded_integer(lower, upper):
    def parse(value):
        number = int(value)
        if not lower <= number <= upper:
            raise argparse.ArgumentTypeError(f"Choose {lower} through {upper}.")
        return number
    return parse


def animate(scene, seconds):
    rng = random.Random()
    color = sys.stdout.isatty()
    deadline = time.monotonic() + seconds
    frame = 0
    print(f"\n*** {SCENES[scene]} ***\nCtrl-C stops the show.\n", flush=True)
    try:
        while time.monotonic() < deadline:
            wave = int(18 + 17 * math.sin(frame / 3 + scene))
            particles = "".join(rng.choice(" .+*o") for _ in range(22))
            bar = "#" * wave + "." * (35 - wave)
            line = f"[{bar}] {particles}  {'FONDUE' if frame % 8 == 0 else '':6}"
            if color:
                line = f"\033[{31 + (frame + scene) % 6}m{line}\033[0m"
            print(line, flush=True)
            time.sleep(0.15)
            frame += 1
    finally:
        if color:
            print("\033[0m", end="")
    print("The fondue protocol is complete. You can close this terminal.")


def launch_commands(count, seconds):
    scenes = random.sample(range(len(SCENES)), count)
    return [
        [sys.executable, str(Path(__file__).resolve()), "--scene", str(scene),
         "--seconds", str(seconds)]
        for scene in scenes
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows", type=bounded_integer(1, 10),
                        help="Immediately open 1–10 terminals with random animations.")
    parser.add_argument("--seconds", type=bounded_integer(1, 15), default=8)
    parser.add_argument("--scene", type=bounded_integer(0, 9),
                        help="Show one scene in the current terminal.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the launch plan without running it.")
    args = parser.parse_args()
    if args.windows and args.scene is not None:
        parser.error("Use --windows or --scene, not both.")
    if not args.windows:
        scene = args.scene if args.scene is not None else random.randrange(10)
        if args.dry_run:
            print(f"Current terminal: {SCENES[scene]}, {args.seconds} seconds.")
        else:
            animate(scene, args.seconds)
        return 0

    commands = launch_commands(args.windows, args.seconds)
    if args.dry_run:
        for command in commands:
            print(shlex.join(command))
        return 0

    mac = sys.platform == "darwin"
    launcher = shutil.which("osascript" if mac else "xterm")
    if not launcher:
        parser.error("Window mode needs macOS Terminal or xterm. Use inline mode instead.")
    print(f"This opens {args.windows} terminals with random ASCII animations for "
          f"{args.seconds} seconds each. macOS windows may remain open afterward.\n"
          "No downloads, network requests, file edits or dependency installs.")
    script = ('on run argv\n'
              'tell application "Terminal"\n'
              'activate\n'
              'do script (item 1 of argv)\n'
              'end tell\n'
              'end run')
    for command in commands:
        if mac:
            subprocess.run([launcher, "-e", script, shlex.join(command)],
                           check=True, timeout=10)
        else:
            subprocess.Popen([launcher, "-e", *command])
        time.sleep(0.1)
    print("Launched. Each animation stops automatically.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.")
        sys.exit(130)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Launch stopped: {error}", file=sys.stderr)
        sys.exit(1)
