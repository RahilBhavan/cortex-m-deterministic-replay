CC = arm-none-eabi-gcc
CFLAGS = -mcpu=cortex-m3 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -Os -Wall -Wextra
LDFLAGS = -T linker/mps2.ld -nostdlib -Wl,--gc-sections

all: build/race.elf

.PHONY: toolchain-info check-hash

toolchain-info:
	$(CC) --version
	$(CC) -dumpfullversion -dumpmachine

build/race.elf: src/main.c linker/mps2.ld
	mkdir -p build
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ src/main.c

# The ELF is byte-reproducible with the pinned Arm GNU Toolchain 15.2.Rel1.
# Other compiler versions give a different hash; update race.elf.sha256 with them.
check-hash: build/race.elf
	sha256sum --check --strict race.elf.sha256

# QEMU boot smoke: firmware is an infinite loop with no semihosting output.
# Success means the image loads and runs until the timeout kills QEMU (124).
smoke: build/race.elf
	@command -v qemu-system-arm >/dev/null || { echo "smoke blocked: qemu-system-arm not on PATH"; exit 1; }
	@set -e; \
	out=$$(mktemp); \
	status=0; \
	perl -e 'alarm shift; exec @ARGV' 2 qemu-system-arm -M mps2-an385 -cpu cortex-m3 -nographic -monitor none -kernel build/race.elf >$$out 2>&1 || status=$$?; \
	cat $$out; \
	rm -f $$out; \
	test $$status -eq 124 -o $$status -eq 142

clean:
	rm -rf build
