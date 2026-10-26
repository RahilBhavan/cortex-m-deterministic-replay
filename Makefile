PYTHON := .venv/bin/python

.PHONY: setup check demo evidence firmware firmware-hash toolchain-info gateway-test rtl-test rtl-lint synth pnr

check: .venv/bin/python firmware
	@command -v verilator >/dev/null || { echo "check blocked: install Verilator and put it on PATH"; exit 1; }
	$(PYTHON) -m unittest discover -v
	$(PYTHON) -m replay.demo
	$(MAKE) rtl-test
	$(MAKE) gateway-test

# Short race-first path for interviews and CI host jobs (no Verilator / 100k replay).
demo: .venv/bin/python firmware
	$(PYTHON) -m tools.demo_race

# Create .venv and install the hashed, pinned Python dependencies.
setup:
	python3 -m venv .venv
	.venv/bin/pip install --require-hashes -r requirements.txt

.venv/bin/python:
	@echo "check blocked: run 'make setup' first to create .venv"
	@exit 1

evidence: .venv/bin/python firmware
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 0
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 1
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 2
	$(PYTHON) -m recorder.race_rate --trials 1000 --seed 3
	$(PYTHON) -m replay.demo

firmware:
	$(MAKE) -C firmware

firmware-hash: firmware
	$(MAKE) -C firmware check-hash

toolchain-info:
	$(MAKE) -C firmware toolchain-info

rtl-test:
	verilator --binary -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --top-module tb_capture_fifo gateway/sim/tb_capture_fifo.sv gateway/rtl/capture_fifo.sv
	./obj_dir/Vtb_capture_fifo +INFILE=examples/golden-demo.dtrc

gateway-test:
	verilator --binary -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --top-module tb_capture_gate gateway/sim/tb_capture_gate.sv gateway/rtl/capture_gate.sv gateway/rtl/reset_sync.sv gateway/rtl/ddr_capture.sv gateway/rtl/async_fifo.sv
	./obj_dir/Vtb_capture_gate +INFILE=examples/golden-demo.dtrc +COUNT=66

rtl-lint:
	verilator --lint-only --Wall --Wno-fatal --top-module capture_gate gateway/rtl/capture_gate.sv gateway/rtl/reset_sync.sv gateway/rtl/ddr_capture.sv gateway/rtl/async_fifo.sv
	yosys -p 'read_verilog -sv gateway/rtl/gateway_top.sv gateway/rtl/capture_gate.sv gateway/rtl/reset_sync.sv gateway/rtl/ddr_capture.sv gateway/rtl/async_fifo.sv; hierarchy -top gateway_top -check; proc; opt; check'

synth:
	$(MAKE) -C gateway synth

pnr:
	$(MAKE) -C gateway pnr
