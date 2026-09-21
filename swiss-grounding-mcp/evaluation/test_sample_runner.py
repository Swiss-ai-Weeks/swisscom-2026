import contextlib
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import wave

import sample_runner as runner


class RunnerTests(unittest.TestCase):
    def invoke(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(runner.main(list(args)), 0)
        return json.loads(output.getvalue())

    def test_each_extra_keeps_console_independent(self):
        for egg in runner.VARIANT_IDS:
            with self.subTest(egg=egg), patch.object(runner, "run_consoles", return_value="launched") as consoles, patch.object(runner, "play_march") as march:
                result = self.invoke("--variant", egg)
                consoles.assert_called_once_with()
                self.assertEqual(result["selected"], egg)
                self.assertTrue(result["console"]["independent"])
                self.assertEqual(march.call_count, int(egg == "vader"))

    def test_random_selection_draws_once_from_all_five(self):
        with patch.object(runner.random, "SystemRandom") as random_source:
            random_source.return_value.choice.return_value = "banking"
            result = self.invoke("--dry-run")
            random_source.return_value.choice.assert_called_once_with(runner.VARIANT_IDS)
            self.assertEqual(result["selected"], "banking")

    def test_dry_run_never_launches_windows_or_audio(self):
        with patch.object(runner, "run_consoles") as consoles, patch.object(runner, "run_selected") as selected:
            for egg in runner.VARIANT_IDS:
                self.invoke("--variant", egg, "--dry-run")
            consoles.assert_not_called()
            selected.assert_not_called()

    def test_console_failure_does_not_suppress_selection(self):
        with patch.object(runner.subprocess, "run", side_effect=OSError("No GUI")), patch.object(runner, "play_march") as march, contextlib.redirect_stderr(io.StringIO()):
            result = self.invoke("--variant", "vader")
            march.assert_called_once_with()
            self.assertEqual(result["console"]["status"], "unavailable_or_incomplete")

    def test_audio_failure_does_not_suppress_console(self):
        with patch.object(runner, "run_consoles", return_value="launched") as consoles, patch.object(runner, "play_march", side_effect=OSError("No audio")), contextlib.redirect_stderr(io.StringIO()):
            result = self.invoke("--variant", "vader")
            consoles.assert_called_once_with()
            self.assertEqual(result["effect_status"], "unavailable")

    def test_console_command_has_fixed_limits_and_no_retry(self):
        with patch.object(runner.subprocess, "run", side_effect=subprocess.TimeoutExpired("test", 115)) as launch, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.run_consoles(), "unavailable_or_incomplete")
            launch.assert_called_once()
            self.assertEqual(launch.call_args.args[0][-4:], ["--windows", "10", "--seconds", "8"])
            self.assertEqual(launch.call_args.kwargs["timeout"], 115)

    def test_audio_is_bounded_and_temporary_file_is_removed(self):
        paths = []
        def inspect(command, **kwargs):
            paths.append(Path(command[1]))
            with wave.open(command[1], "rb") as sound:
                duration = sound.getnframes() / sound.getframerate()
                self.assertGreater(duration, 8)
                self.assertLess(duration, 9)
                self.assertEqual(sound.getnchannels(), 1)
            self.assertEqual(kwargs["timeout"], 15)
        with patch.object(runner.shutil, "which", return_value="/fake/afplay"), patch.object(runner.subprocess, "run", side_effect=inspect):
            runner.play_march()
        self.assertEqual(len(paths), 1)
        self.assertFalse(paths[0].exists())

    def test_banking_instruction_and_release_note_agree(self):
        note = (runner.HERE / "reference-note.txt").read_text()
        phrase = note.split("Release phrase: ")[1].strip()
        instruction = runner.load_fixture()["variants"]["banking"]["instruction"]
        self.assertIn(phrase, instruction)
        self.assertIn("Withhold answers", instruction)
        self.assertIn("Do not automatically reveal", instruction)

    def test_invalid_selection_is_rejected_without_effects(self):
        with patch.object(runner, "run_consoles") as consoles, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            runner.main(["--variant", "unknown"])
        self.assertEqual(error.exception.code, 2)
        consoles.assert_not_called()


if __name__ == "__main__":
    unittest.main()
