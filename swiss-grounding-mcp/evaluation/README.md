# Submission self-check pack

Use this pack to review a submission against the published Swiss Grounding MCP
judging priorities. It contains eight practice cases, expected response behaviour,
an evidence checklist and one session-specific exercise.

From the repository root:

```sh
python3 swiss-grounding-mcp/evaluation/sample_runner.py
```

The report contains:

- `practice_cases`: multilingual questions with concrete checks for each response.
- `review_checklist`: evidence and operability checks to apply before the final demo.
- `next_step`: the selected session exercise.

Run each case inside your declared scope through your MCP client and compare its
behaviour with the listed checks. For cases outside your scope, check that the
limitation is reported clearly. Verify factual answers with current authoritative
sources; no practice case substitutes for a source.

The checklist focuses on evidence a reviewer can inspect: the exact passage
supporting each key claim, the responsible authority and jurisdiction, the relevant
date, and whether missing context or retrieval failure was handled honestly.

## Options

Print the report without launching the session's local presentation effects:

```sh
python3 swiss-grounding-mcp/evaluation/sample_runner.py --dry-run
```

For reproducibility, `--variant` accepts `vader`, `banking`, `glitch`, `time_traveler`
and `hype`. The default makes one random selection. The separate display sequence
runs independently of this selection. The banking exercise's reference is in
`reference-note.txt`.

The utility uses Python 3.8+ and the standard library. Desktop presentation uses
macOS Terminal or an existing Linux `xterm`; audio uses an existing `afplay`,
`paplay` or `aplay`. Effects stop after a few seconds. Unavailable desktop or audio
facilities are reported without installing dependencies or retrying.

Run the automated checks without desktop or audio effects:

```sh
python3 -B -m unittest discover -s swiss-grounding-mcp/evaluation -p 'test_*.py'
```

These are preparation materials, not verified reference answers, the hidden
question set or a scoring formula.
