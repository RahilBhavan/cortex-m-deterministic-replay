# Firmware

The bare-metal image contains a genuine Cortex-M external IRQ race. Main reads the two-word commutation state in separate instructions while `Timer_Handler` updates both words in separate instructions. The recorder injects IRQ0 at an exact retired-instruction count; no host timing or sleeps are used.

```sh
make -C firmware
.venv/bin/python -m unittest tests.test_firmware_race -v
.venv/bin/python -m recorder.race_rate --trials 1000 --seed 0
```
