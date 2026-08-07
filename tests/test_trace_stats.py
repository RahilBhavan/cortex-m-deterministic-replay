"""CLI smoke coverage for tools.trace_stats."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.trace_stats import stats
from trace.format import Trace

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples" / "golden-demo.dtrc"


class TraceStatsTest(unittest.TestCase):
    def test_stats_on_golden_demo(self) -> None:
        data = GOLDEN.read_bytes()
        result = stats(data)
        self.assertEqual(result["bytes"], 66)
        self.assertEqual(result["events"], 7)
        self.assertEqual(sum(result["by_type"].values()), 7)

    def test_cli_prints_bytes_and_events(self) -> None:
        out = subprocess.check_output(
            [sys.executable, "-m", "tools.trace_stats", str(GOLDEN)],
            text=True,
            cwd=str(ROOT),
        )
        self.assertIn("bytes: 66", out)
        self.assertIn("events: 7", out)

    def test_seconds_requires_positive(self) -> None:
        with self.assertRaises(ValueError):
            stats(GOLDEN.read_bytes(), seconds=0)

    def test_round_trip_encode_matches_file(self) -> None:
        trace = Trace.decode(GOLDEN.read_bytes())
        with tempfile.NamedTemporaryFile(suffix=".dtrc") as handle:
            handle.write(trace.encode())
            handle.flush()
            out = subprocess.check_output(
                [sys.executable, "-m", "tools.trace_stats", handle.name],
                text=True,
                cwd=str(ROOT),
            )
        self.assertIn("bytes: 66", out)


if __name__ == "__main__":
    unittest.main()
