#!/usr/bin/env python3
"""A bounded terminal presentation. Python standard library only."""

import argparse
import math
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import sys
import tempfile
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
    if color:
        print("\033[2J\033[?25l", end="", flush=True)
    try:
        while time.monotonic() < deadline:
            wave = int(18 + 17 * math.sin(frame / 3 + scene))
            particles = "".join(rng.choice(" .+*o") for _ in range(22))
            bar = "#" * wave + "." * (35 - wave)
            line = f"[{bar}]  {'FONDUE' if frame % 8 == 0 else '':6}"
            if color:
                art = '              .==,_\n             .===,_`\\\n           .====,_ ` \\      .====,__\n     ---     .==-,`~. \\           `:`.__,\n      ---      `~~=-.  \\           /^^^   ...always on the go!\n        ---       `~~=. \\         /\n                     `~. \\       /\n                       ~. \\____./\n              jgs        `.=====)\n                      ___.--~~~--.__\n            ___\\.--~~~              ~~~---.._|/\n            ~~~"                             /\n'
                art = "\n".join(
                    f"\033[1;{31 + (row + frame + scene) % 6}m{line}"
                    for row, line in enumerate(art.splitlines())
                ) + "\n"
                screen = (f"\033[H\033[1;{31 + (frame + scene) % 6}m"
                          f"   === {SCENES[scene].upper()} / MEEP MEEP! ===\n"
                          f"\033[36m{art}\n"
                          f"\033[33m       {particles}\n"
                          f"\033[1;32m    {line}\n\n"
                          "\033[1;37m              DONT BE LAZY!\n"
                          "\033[0m    Ctrl-C stops the show.\033[J")
                print(screen, end="", flush=True)
            else:
                print(f"{SCENES[scene]}: {line}", flush=True)
            time.sleep(0.15)
            frame += 1
    finally:
        if color:
            print("\033[0m\033[?25h", end="", flush=True)
    print("\nDONT BE LAZY! You can close this terminal.")


def launch_macos(commands, seconds):
    """Address Terminal by bundle ID and verify that each animation ran."""
    with tempfile.TemporaryDirectory(prefix="swiss-display-") as temporary:
        directory = Path(temporary)
        documents = []
        completions = []
        starts = []
        for index, command in enumerate(commands):
            document = directory / f"Swiss-{index + 1:02d}.command"
            complete = directory / f"complete-{index}"
            started = directory / f"started-{index}"
            document.write_text(
                "#!/bin/sh\n"
                f"printf started > {shlex.quote(str(started))}\n"
                + shlex.join(command) + "\n"
                "result=$?\n"
                f"printf '%s' \"$result\" > {shlex.quote(str(complete))}\n"
                "if [ -t 0 ]; then\n"
                "  printf '\\nPress Return to close this display... '\n"
                "  read -r session_reply\n"
                "fi\n"
                'exit "$result"\n'
            )
            document.chmod(0o700)
            documents.append(str(document))
            completions.append(complete)
            starts.append(started)
        script = ('on run argv\n'
                  'tell application id "com.apple.Terminal"\n'
                  'activate\n'
                  'do script (item 1 of argv)\n'
                  'end tell\n'
                  'end run')
        for document in documents:
            subprocess.run(
                ["/usr/bin/osascript", "-e", script,
                 shlex.join(["/bin/sh", document])],
                check=True, timeout=10, stdout=subprocess.DEVNULL,
            )
        deadline = time.monotonic() + seconds + 20
        while time.monotonic() < deadline:
            if all(path.exists() and path.read_text() for path in completions):
                if any(path.read_text() != "0" for path in completions):
                    raise OSError("A Terminal animation exited unsuccessfully.")
                return
            time.sleep(0.1)
        started_count = sum(path.exists() for path in starts)
        complete_count = sum(path.exists() and path.read_text() == "0" for path in completions)
        raise OSError(f"Terminal did not finish the animations: {started_count}/{len(commands)} "
                      f"started, {complete_count}/{len(commands)} completed. "
                      "Check the graphical desktop and Terminal execution access.")


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
          "Uses temporary launch files; no downloads or dependency installs.", flush=True)
    if mac:
        launch_macos(commands, args.seconds)
    else:
        for command in commands:
            subprocess.Popen([launcher, "-e", *command])
            time.sleep(0.1)
    print("Completed." if mac else "Launched. Each animation stops automatically.")
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
