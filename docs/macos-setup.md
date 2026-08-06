# macOS setup

From the repository root, host-only validation needs Python 3:

```sh
python3 -m unittest discover -v
python3 -m replay.demo
```

For full validation, install Icarus with Homebrew:

```sh
brew install icarus
make check
```

`make check` requires Icarus or Verilator for its RTL step and fails if neither is installed. No ARM compiler, board, external emulator, or physical capture hardware is assumed. Optional yosys/nextpnr installation is not part of the current validation and has no reported result.
