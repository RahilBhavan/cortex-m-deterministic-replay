"""One-instruction Cortex-M execution using the official Unicorn engine."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

try:
    from unicorn import (
        UC_ARCH_ARM,
        UC_HOOK_CODE,
        UC_HOOK_MEM_READ,
        UC_HOOK_MEM_WRITE,
        UC_MODE_THUMB,
        Uc,
    )
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_R4,
        UC_ARM_REG_R5,
        UC_ARM_REG_R6,
        UC_ARM_REG_R7,
        UC_ARM_REG_R8,
        UC_ARM_REG_R9,
        UC_ARM_REG_R10,
        UC_ARM_REG_R11,
        UC_ARM_REG_R12,
        UC_ARM_REG_SP,
        UC_ARM_REG_XPSR,
    )
except ImportError as exc:
    raise ImportError("Install Unicorn from https://github.com/unicorn-engine/unicorn") from exc

REGS = (
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_R8,
    UC_ARM_REG_R9,
    UC_ARM_REG_R10,
    UC_ARM_REG_R11,
    UC_ARM_REG_R12,
)

# Thumb BX lr encoding used by the synthetic exception-return shim.
_BX_LR = 0x4770
_EXC_RETURN_THREAD = 0xFFFFFFF9


def _sign_extend(value: int, bits: int) -> int:
    """Sign-extend a `bits`-wide immediate to a Python int."""
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def condition_passed(xpsr: int, cond: int) -> bool:
    """Evaluate an ARM condition code against APSR flags in xPSR."""
    n = bool(xpsr & (1 << 31))
    z = bool(xpsr & (1 << 30))
    c = bool(xpsr & (1 << 29))
    v = bool(xpsr & (1 << 28))
    if cond == 0x0:
        return z
    if cond == 0x1:
        return not z
    if cond == 0x2:
        return c
    if cond == 0x3:
        return not c
    if cond == 0x4:
        return n
    if cond == 0x5:
        return not n
    if cond == 0x6:
        return v
    if cond == 0x7:
        return not v
    if cond == 0x8:
        return c and not z
    if cond == 0x9:
        return (not c) or z
    if cond == 0xA:
        return n == v
    if cond == 0xB:
        return n != v
    if cond == 0xC:
        return (not z) and (n == v)
    if cond == 0xD:
        return z or (n != v)
    if cond == 0xE:
        return True
    return False


def thumb16_next_pc(pc: int, insn: int, xpsr: int) -> int | None:
    """
    Resolve the next PC for Thumb-16 control-flow encodings.

    Returns None when the halfword is not a resolved 16-bit branch/sequential
    site that this Phase-0 core owns (caller falls back to width-based advance,
    including 32-bit Thumb first halves).
    """
    # Conditional B<cond> label: 1101 cond imm8 (excludes 0xDE UDF / 0xDF SVC).
    if (insn & 0xF000) == 0xD000:
        cond = (insn >> 8) & 0xF
        if cond < 0xE and condition_passed(xpsr, cond):
            imm8 = _sign_extend(insn & 0xFF, 8)
            return (pc + 4 + (imm8 << 1)) & 0xFFFFFFFF
        if cond < 0xE:
            return (pc + 2) & 0xFFFFFFFF
        return None
    # Unconditional B label: 11100 imm11.
    if (insn & 0xF800) == 0xE000:
        imm11 = _sign_extend(insn & 0x7FF, 11)
        return (pc + 4 + (imm11 << 1)) & 0xFFFFFFFF
    return None


def thumb_insn_size(insn: int) -> int:
    """Return 2 or 4 for a Thumb first halfword (ARMv7-M BL/32-bit prefixes)."""
    # 32-bit Thumb encodings begin with 0b11101 / 0b11110 / 0b11111.
    if (insn & 0xE000) == 0xE000 and (insn & 0x1800) != 0x0000:
        return 4
    return 2


class CortexM:
    """Unicorn-backed Cortex-M instruction stepper with a narrow IRQ shim."""

    def __init__(self, elf: str, mmio: dict | None = None) -> None:
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.count = 0
        self.mmio = mmio or {}
        self._read_override: dict[str, object] | None = None
        self.build_id = hashlib.sha256(Path(elf).read_bytes()).digest()
        # Optional ELF symbol table for diagnostics / tests (not used for branching).
        self.symbols = self._load_symbols(Path(elf).read_bytes())
        self._load(elf)
        self.pc = int.from_bytes(self.uc.mem_read(4, 4), "little") & ~1
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self._read)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)

    @staticmethod
    def _load_symbols(blob: bytes) -> dict[str, int]:
        """Parse ELF32 symbol names to values when a symbol table is present."""
        if len(blob) < 52 or blob[4] != 1:
            return {}
        endian = "<" if blob[5] == 1 else ">"
        header = struct.unpack_from(endian + "16sHHIIIIIHHHHHH", blob, 0)
        shoff, shentsize, shnum = header[6], header[11], header[12]
        if shoff == 0 or shnum == 0:
            return {}
        sections = [
            struct.unpack_from(endian + "IIIIIIIIII", blob, shoff + i * shentsize)
            for i in range(shnum)
        ]
        # SHT_SYMTAB == 2; sh_link (index 6) points at the string table section.
        symtab = next((section for section in sections if section[1] == 2), None)
        if symtab is None:
            return {}
        link = symtab[6]
        if link >= len(sections):
            return {}
        strtab = sections[link]
        strings = blob[strtab[4] : strtab[4] + strtab[5]]
        entry_size = symtab[9] or 16
        symbols: dict[str, int] = {}
        for offset in range(0, symtab[5], entry_size):
            name_off, value, _size, _info, _other, _shndx = struct.unpack_from(
                endian + "IIIBBH", blob, symtab[4] + offset
            )
            end = strings.find(b"\0", name_off)
            if end < 0:
                continue
            name = strings[name_off:end].decode("ascii", errors="ignore")
            if name:
                symbols[name] = value
        return symbols

    def _load(self, path: str) -> None:
        blob = Path(path).read_bytes()
        cls = blob[4]
        endian = "<" if blob[5] == 1 else ">"
        if cls != 1:
            raise ValueError("only ELF32 firmware is supported")
        header = struct.unpack_from(endian + "16sHHIIIIIHHHHHH", blob, 0)
        phoff, ents, n = header[5], header[9], header[10]
        for i in range(n):
            p = struct.unpack_from(endian + "IIIIIIII", blob, phoff + i * ents)
            if p[0] == 1 and p[4]:
                addr = p[2]
                size = (p[5] + 0xFFF) & ~0xFFF
                base = addr & ~0xFFF
                try:
                    self.uc.mem_map(base, size)
                except Exception:
                    pass
                self.uc.mem_write(addr, blob[p[1] : p[1] + p[4]])
        self.uc.mem_map(0x20000000, 0x10000)
        self.uc.mem_map(0x40000000, 0x1000)
        self.uc.reg_write(UC_ARM_REG_SP, struct.unpack("<I", self.uc.mem_read(0, 4))[0])
        self.uc.reg_write(
            UC_ARM_REG_PC, struct.unpack("<I", self.uc.mem_read(4, 4))[0] & ~1
        )

    def _code(self, uc: Uc, address: int, size: int, user: object) -> None:
        self.pc = address

    def _read(
        self, uc: Uc, access: int, address: int, size: int, value: int, user: object
    ) -> None:
        if self._read_override is not None:
            expected_address = self._read_override["address"]
            expected_width = self._read_override["width"]
            if address != expected_address or size != expected_width:
                raise ValueError(
                    "read override does not match instruction access: "
                    f"expected {expected_address:#x}/{expected_width}, "
                    f"got {address:#x}/{size}"
                )
            original = bytes(uc.mem_read(address, size))
            uc.mem_write(
                address,
                int(self._read_override["value"]).to_bytes(size, "little"),
            )
            self._read_override["original"] = original
            self._read_override["consumed"] = True
            return
        if address in self.mmio:
            uc.mem_write(address, int(self.mmio[address]).to_bytes(size, "little"))

    def _write(
        self, uc: Uc, access: int, address: int, size: int, value: int, user: object
    ) -> None:
        return None

    def snapshot(self) -> tuple[int, ...]:
        return tuple(self.uc.reg_read(r) for r in REGS) + (
            self.uc.reg_read(UC_ARM_REG_SP),
            self.uc.reg_read(UC_ARM_REG_LR),
            self.uc.reg_read(UC_ARM_REG_PC),
            self.uc.reg_read(UC_ARM_REG_XPSR),
        )

    def inject_irq(self, irq: int) -> None:
        if not isinstance(irq, int) or not 0 <= irq <= 255:
            raise ValueError("invalid IRQ")
        vector = int.from_bytes(self.uc.mem_read(4 * (16 + irq), 4), "little") & ~1
        if not vector:
            raise ValueError("unmapped IRQ vector")
        old_sp = self.uc.reg_read(UC_ARM_REG_SP)
        old_pc = self.pc | 1
        state = self.snapshot()
        frame = struct.pack("<8I", *state[:4], state[12], state[14], old_pc, state[16])
        self.uc.mem_write(old_sp - len(frame), frame)
        self.uc.reg_write(UC_ARM_REG_SP, old_sp - len(frame))
        self.uc.reg_write(UC_ARM_REG_LR, _EXC_RETURN_THREAD)
        self.uc.reg_write(UC_ARM_REG_PC, vector)
        self.pc = vector

    def dma(self, address: int, payload: bytes) -> None:
        if not isinstance(payload, bytes) or not 0 <= address <= 0xFFFFFFFF - len(payload):
            raise ValueError("invalid DMA")
        self.uc.mem_write(address, payload)

    def queue_read_override(self, address: int, value: int, width: int) -> None:
        """Apply one recorded read value to the next instruction's matching access."""
        if self._read_override is not None:
            raise ValueError("multiple read overrides for one instruction are unsupported")
        if (
            not isinstance(address, int)
            or not 0 <= address <= 0xFFFFFFFF
            or width not in (1, 2, 4)
            or not isinstance(value, int)
            or not 0 <= value < (1 << (8 * width))
        ):
            raise ValueError("invalid read override")
        self._read_override = {
            "address": address,
            "value": value,
            "width": width,
            "consumed": False,
            "original": None,
        }

    def _finish_read_override(self) -> None:
        override = self._read_override
        self._read_override = None
        if override is None:
            return
        original = override["original"]
        if original is not None:
            self.uc.mem_write(int(override["address"]), original)
        if not override["consumed"]:
            raise ValueError("read override was not consumed by the scheduled instruction")

    def run(self, steps: int) -> list[tuple[int, ...]]:
        return [self.step() for _ in range(steps)]

    def _restore_exception_frame(self) -> None:
        """Restore every field owned by the narrow synthetic exception frame."""
        sp = self.uc.reg_read(UC_ARM_REG_SP)
        frame = struct.unpack("<8I", self.uc.mem_read(sp, 32))
        for reg, value in zip(
            (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), frame[:4], strict=True
        ):
            self.uc.reg_write(reg, value)
        self.uc.reg_write(UC_ARM_REG_R12, frame[4])
        self.uc.reg_write(UC_ARM_REG_LR, frame[5])
        self.pc = frame[6] & ~1
        self.uc.reg_write(UC_ARM_REG_PC, self.pc)
        self.uc.reg_write(UC_ARM_REG_XPSR, frame[7])
        self.uc.reg_write(UC_ARM_REG_SP, sp + 32)

    def _exception_return(self) -> tuple[int, ...]:
        """Restore the synthetic stacked frame for EXC_RETURN via BX LR."""
        self.count += 1
        self._restore_exception_frame()
        return self.snapshot()

    def _advance_pc(self, pc: int, insn: int) -> None:
        """Set PC after a retired instruction using Thumb decode, not hardcodes."""
        xpsr = self.uc.reg_read(UC_ARM_REG_XPSR)
        branched = thumb16_next_pc(pc, insn, xpsr)
        if branched is not None:
            self.pc = branched
            return
        self.pc = (pc + thumb_insn_size(insn)) & 0xFFFFFFFF

    def step(self) -> tuple[int, ...]:
        pc = self.pc
        insn = int.from_bytes(self.uc.mem_read(pc, 2), "little")
        # Synthetic exception return before Unicorn executes BX LR with EXC_RETURN.
        if insn == _BX_LR and self.uc.reg_read(UC_ARM_REG_LR) == _EXC_RETURN_THREAD:
            self._finish_read_override()
            return self._exception_return()
        try:
            self.uc.emu_start(pc | 1, 0, count=1)
        except Exception:
            if self._read_override is not None:
                original = self._read_override["original"]
                if original is not None:
                    self.uc.mem_write(int(self._read_override["address"]), original)
                self._read_override = None
            raise
        self._finish_read_override()
        self.count += 1
        self._advance_pc(pc, insn)
        return self.snapshot()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("elf")
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    cpu = CortexM(args.elf)
    for _ in range(args.count):
        cpu.step()
    print(
        "unicorn Cortex-M steps=%d build=%s"
        % (cpu.count, cpu.build_id.hex()[:16])
    )


if __name__ == "__main__":
    main()
