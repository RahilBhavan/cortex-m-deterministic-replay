PYTHON=python3

check:
	$(PYTHON) -m unittest discover -v
	$(PYTHON) -m replay.demo
	$(MAKE) rtl-test

rtl-test:
	@command -v verilator >/dev/null || command -v iverilog >/dev/null || (echo "rtl-test blocked: install Verilator or Icarus"; exit 1)
	@if command -v verilator >/dev/null; then \
		verilator --binary --timed --top-module tb_capture_fifo gateway/sim/tb_capture_fifo.sv gateway/rtl/capture_fifo.sv && \
		./obj_dir/Vtb_capture_fifo; \
	else \
		iverilog -g2012 -o /tmp/capture_fifo.vvp gateway/sim/tb_capture_fifo.sv gateway/rtl/capture_fifo.sv && \
		vvp /tmp/capture_fifo.vvp; \
	fi
