import contextlib
import io
from pathlib import Path
import shlex
import subprocess
import sys
import unittest
from unittest.mock import patch

import display


class DisplayTests(unittest.TestCase):
    def test_terminal_frame_has_roadrunner_and_rainbow(self):
        class TerminalOutput(io.StringIO):
            def isatty(self):
                return True

        output = TerminalOutput()
        with contextlib.redirect_stdout(output), patch.object(display.time, "monotonic", side_effect=[0, 0, 2]), patch.object(display.time, "sleep"):
            display.animate(0, 1)
        text = output.getvalue()
        self.assertIn("jgs", text)
        self.assertIn("...always on the go!", text)
        self.assertIn("DONT BE LAZY!", text)
        for color in range(31, 37):
            self.assertIn(f"\033[1;{color}m", text)
        self.assertIn("\033[?25h", text)

    def simulate_terminal(self, exit_code):
        real_run = subprocess.run
        paths = []

        def run(command, **kwargs):
            self.assertEqual(command[0], "/usr/bin/osascript")
            self.assertIn('application id "com.apple.Terminal"', command[2])
            shell_command = shlex.split(command[-1])
            paths.append(Path(shell_command[1]))
            # Exercise actual shell quoting and completion files, with no desktop.
            real_run(shell_command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return subprocess.CompletedProcess(command, 0)

        tricky_argument = "spaces ' quotes `literal` $(literal)"
        command = [sys.executable, "-c", f"import sys; assert sys.argv[1] == {tricky_argument!r}; sys.exit({exit_code})", tricky_argument]
        with patch.object(display.subprocess, "run", side_effect=run):
            if exit_code:
                with self.assertRaisesRegex(OSError, "unsuccessfully"):
                    display.launch_macos([command], 1)
            else:
                display.launch_macos([command], 1)
        self.assertTrue(paths)
        self.assertTrue(all(not path.exists() for path in paths))

    def test_completion_and_shell_quoting(self):
        self.simulate_terminal(0)

    def test_failed_animation_is_not_reported_as_success(self):
        self.simulate_terminal(3)

    def test_accepted_launch_without_completion_times_out(self):
        with patch.object(display.subprocess, "run"), patch.object(display.time, "monotonic", side_effect=[0, 100]):
            with self.assertRaisesRegex(OSError, "did not finish"):
                display.launch_macos([[sys.executable, "-c", "pass"]], 1)


if __name__ == "__main__":
    unittest.main()
