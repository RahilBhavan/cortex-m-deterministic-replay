#!/usr/bin/env python3
"""Report trace event/byte totals and workload byte rate."""
import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trace.format import Trace


def stats(data, seconds=None):
    trace = Trace.decode(data)
    counts = {}
    for event in trace.events:
        counts[event[0]] = counts.get(event[0], 0) + 1
    result = {"bytes": len(data), "events": len(trace.events), "by_type": counts}
    if seconds is not None:
        if seconds <= 0:
            raise ValueError("seconds must be positive")
        result["bytes_per_second"] = len(data) / seconds
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--seconds", type=float, help="workload duration; this is not hardware measurement")
    args = parser.parse_args()
    result = stats(args.trace.read_bytes(), args.seconds)
    print("bytes:", result["bytes"])
    print("events:", result["events"])
    print("events by tag:", result["by_type"])
    if "bytes_per_second" in result:
        print("workload bytes/sec:", result["bytes_per_second"])
