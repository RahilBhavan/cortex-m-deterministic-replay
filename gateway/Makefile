SHELL := /bin/bash
TOP := gateway_top
BUILD := build
RTL := rtl/gateway_top.sv rtl/capture_gate.sv rtl/reset_sync.sv rtl/ddr_capture.sv rtl/async_fifo.sv
PART_SIZE ?= 25k
PACKAGE ?= CABGA381

.PHONY: synth pnr clean

$(BUILD):
	mkdir -p $@

synth: $(BUILD)
	set -o pipefail; yosys -p 'read_verilog -sv $(RTL); synth_ecp5 -top $(TOP) -json $(BUILD)/$(TOP).json' 2>&1 | tee $(BUILD)/synth.log

pnr: synth
	set -o pipefail; nextpnr-ecp5 --json $(BUILD)/$(TOP).json --textcfg $(BUILD)/$(TOP).config --lpf constraints/gateway.lpf --lpf-allow-unconstrained --package $(PACKAGE) --$(PART_SIZE) --freq 100 2>&1 | tee $(BUILD)/pnr.log

clean:
	rm -rf $(BUILD)
