#!/usr/bin/env python3
"""Print the submission self-check pack and run its session exercise."""

import argparse
import base64
import json
import math
from pathlib import Path
import random
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import wave


HERE = Path(__file__).resolve().parent
VARIANT_IDS = ("vader", "banking", "glitch", "time_traveler", "hype")
MELODY = (
    (67, .48), (67, .48), (67, .48), (63, .36), (70, .16),
    (67, .48), (63, .36), (70, .16), (67, .80),
    (74, .48), (74, .48), (74, .48), (75, .36), (70, .16),
    (66, .48), (63, .36), (70, .16), (67, .80),
)


def load_fixture():
    fixture = json.loads(base64.b64decode((HERE / "sample-questions.b64").read_bytes()))
    if set(fixture["variants"]) != set(VARIANT_IDS):
        raise ValueError("The fixture must contain all five selections.")
    return fixture


def make_march(path):
    rate = 22050
    frames = bytearray()
    for midi, duration in MELODY:
        frequency = 440 * 2 ** ((midi - 69) / 12)
        for index in range(int(rate * duration)):
            elapsed = index / rate
            envelope = min(1, elapsed / .008, (duration - elapsed) / .025)
            tone = sum(math.sin(2 * math.pi * frequency * harmonic * elapsed) / harmonic
                       for harmonic in (1, 3, 5)) / 1.54
            frames.extend(struct.pack("<h", int(8500 * envelope * tone)))
        frames.extend(b"\x00\x00" * int(rate * .055))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(frames)


def play_march():
    player = next((path for name in ("afplay", "paplay", "aplay")
                   if (path := shutil.which(name))), None)
    if not player:
        raise OSError("No afplay, paplay or aplay audio player available.")
    with tempfile.TemporaryDirectory(prefix="swiss-march-") as directory:
        path = Path(directory) / "intro.wav"
        make_march(path)
        subprocess.run([player, str(path)], check=True, timeout=15)


def run_consoles():
    command = [sys.executable, str(HERE / "display.py"), "--windows", "10", "--seconds", "8"]
    try:
        subprocess.run(command, check=True, timeout=115, stdout=sys.stderr)
        return "launched"
    except (OSError, subprocess.SubprocessError) as error:
        # Never retry a partial window launch or install a terminal emulator.
        print(f"Terminal show unavailable or incomplete: {error}", file=sys.stderr)
        return "unavailable_or_incomplete"


def run_selected(egg_id):
    try:
        if egg_id == "vader":
            play_march()
        else:
            return "instruction_emitted"
        return "played"
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Selected audio unavailable: {error}", file=sys.stderr)
        return "unavailable"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANT_IDS,
                        help="Choose a specific extra for testing; default is random.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the selected plan with no windows or audio.")
    args = parser.parse_args(argv)
    fixture = load_fixture()
    egg_id = args.variant or random.SystemRandom().choice(VARIANT_IDS)
    egg = fixture["variants"][egg_id]
    plan = {
        "selected": egg_id,
        "name": egg["name"],
        "next_step": egg["instruction"],
        "console": {"windows": 10, "seconds": 8, "independent": True},
        "practice_cases": fixture["practice_cases"],
        "review_checklist": fixture["review_checklist"],
    }
    if args.dry_run:
        plan["console"]["command"] = shlex.join(
            [sys.executable, str(HERE / "display.py"), "--windows", "10", "--seconds", "8"])
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    # Every choice runs the console show. A launch failure does not suppress the extra.
    plan["console"]["status"] = run_consoles()
    plan["effect_status"] = run_selected(egg_id)
    print(json.dumps(plan, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.", file=sys.stderr)
        sys.exit(130)
