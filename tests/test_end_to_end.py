import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from replay.engine import first_divergence, replay
from trace.format import Trace

ROOT = Path(__file__).resolve().parents[1]


class TestEndToEnd(unittest.TestCase):
    def test_stream_rejects_invalid_count_and_output_path(self):
        iverilog = shutil.which("iverilog")
        vvp = shutil.which("vvp")
        if not iverilog or not vvp:
            self.skipTest("Icarus Verilog is not installed")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_hex = directory / "trace.hex"
            input_hex.write_text("00\\n")
            binary = directory / "stream.vvp"
            subprocess.run([
                iverilog, "-g2012", "-o", str(binary),
                str(ROOT / "gateway/sim/tb_capture_fifo_stream.sv"),
                str(ROOT / "gateway/rtl/capture_fifo.sv"),
            ], check=True, cwd=ROOT)
            for count in ("-1", str(65537)):
                result = subprocess.run([
                    vvp, str(binary), f"+INFILE={input_hex}",
                    f"+OUTFILE={directory / 'out.bin'}", f"+COUNT={count}",
                ], cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
            result = subprocess.run([
                vvp, str(binary), f"+INFILE={input_hex}",
                f"+OUTFILE={directory / 'missing' / 'out.bin'}", "+COUNT=0",
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_encoded_trace_round_trips_through_rtl_fifo(self):
        iverilog = shutil.which("iverilog")
        vvp = shutil.which("vvp")
        if not iverilog or not vvp:
            self.skipTest("Icarus Verilog is not installed")

        trace = Trace(events=[
            (1, 2, 3), (2, 4, 0x4000, 7, 1),
            (3, 6, 20, 2, b"AB"), (4, 8, 9),
            (5, 10, 1), (6, 12, 0x1234), (7, 14, 0x55),
        ])
        encoded = trace.encode()
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_hex = directory / "trace.hex"
            output_bin = directory / "trace.bin"
            input_hex.write_text("".join(f"{byte:02x}\n" for byte in encoded))
            binary = directory / "stream.vvp"
            subprocess.run([
                iverilog, "-g2012", "-o", str(binary),
                str(ROOT / "gateway/sim/tb_capture_fifo_stream.sv"),
                str(ROOT / "gateway/rtl/capture_fifo.sv"),
            ], check=True, cwd=ROOT)
            subprocess.run([
                vvp, str(binary),
                f"+INFILE={input_hex}", f"+OUTFILE={output_bin}",
                f"+COUNT={len(encoded)}",
            ], check=True, cwd=ROOT)
            emitted = output_bin.read_bytes()

        decoded = Trace.decode(emitted)
        self.assertEqual(emitted, encoded)
        self.assertIsNone(first_divergence(replay(trace), replay(decoded), trace.events))


if __name__ == "__main__":
    unittest.main()
