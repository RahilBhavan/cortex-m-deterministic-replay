PYTHON := .venv/bin/python

.PHONY: check demo evidence firmware gateway-test rtl-test synth pnr

check: .venv/bin/python firmware
	@command -v verilator >/dev/null || { echo "check blocked: install Verilator and put it on PATH"; exit 1; }
	$(PYTHON) -m unittest discover -v
	$(PYTHON) -m replay.demo
	$(MAKE) rtl-test
	$(MAKE) gateway-test

# Short race-first path for interviews and CI host jobs (no Verilator / 100k replay).
demo: .venv/bin/python firmware
	$(PYTHON) -m tools.demo_race

.venv/bin/python:
	@echo "check blocked: create .venv first (python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)"
	@exit 1

evidence: .venv/bin/python firmware
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 0
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 1
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 2
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 3
	$(PYTHON) -m replay.demo

firmware:
	$(MAKE) -C firmware

rtl-test:
	verilator --binary -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --top-module tb_capture_fifo gateway/sim/tb_capture_fifo.sv gateway/rtl/capture_fifo.sv
	./obj_dir/Vtb_capture_fifo

gateway-test:
	verilator --binary -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --top-module tb_capture_gate gateway/sim/tb_capture_gate.sv gateway/rtl/capture_gate.sv gateway/rtl/ddr_capture.sv gateway/rtl/async_fifo.sv
	./obj_dir/Vtb_capture_gate

synth:
	$(MAKE) -C gateway synth

pnr:
	$(MAKE) -C gateway pnr
