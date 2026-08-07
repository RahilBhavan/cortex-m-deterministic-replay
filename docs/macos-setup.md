# macOS setup

Observed Apple Silicon tool versions: ARM GCC 16.1.0, QEMU 11.0.3, Unicorn 2.1.4, Verilator 5.050, Yosys 0.68+post, Project Trellis 1.4_8, and nextpnr ECP5 `de8cd97`.

```sh
brew install arm-none-eabi-gcc qemu yosys verilator prjtrellis cmake eigen
python3 -m venv .venv
.venv/bin/python -m pip install unicorn
make check
make evidence
make synth
PATH=/tmp/nextpnr-build:$PATH make pnr
```

Build nextpnr outside the repository:

```sh
git clone --depth 1 https://github.com/YosysHQ/nextpnr.git /tmp/nextpnr
cmake -S /tmp/nextpnr -B /tmp/nextpnr-build -DARCH=ecp5 -DTRELLIS_INSTALL_PREFIX="$(brew --prefix prjtrellis)" -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/nextpnr-build --target nextpnr-ecp5 -j2
PATH=/tmp/nextpnr-build:$PATH make pnr
```

`make check` requires `.venv/bin/python` and Verilator and fails explicitly when absent. QEMU boot smoke is `make -C firmware smoke`; it is not the exact recorder gate. No bytes/sec figure is produced.
