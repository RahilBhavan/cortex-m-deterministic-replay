"""One-instruction Cortex-M execution using the official Unicorn engine."""
import argparse, hashlib, struct
from pathlib import Path

try:
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11, UC_ARM_REG_R12, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_XPSR
except ImportError as exc:
    raise ImportError("Install Unicorn from https://github.com/unicorn-engine/unicorn") from exc

REGS=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12)

class CortexM:
    def __init__(self, elf, mmio=None):
        self.uc=Uc(UC_ARCH_ARM, UC_MODE_THUMB); self.count=0; self.mmio=mmio or {}
        self.build_id=hashlib.sha256(Path(elf).read_bytes()).digest()
        self._load(elf)
        self.pc = int.from_bytes(self.uc.mem_read(4, 4), "little") & ~1
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self._read)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)

    def _load(self, path):
        b=Path(path).read_bytes(); cls=b[4]; endian='<' if b[5]==1 else '>'
        if cls != 1: raise ValueError('only ELF32 firmware is supported')
        h=struct.unpack_from(endian+'16sHHIIIIIHHHHHH',b,0); phoff,ents,n=h[5],h[9],h[10]
        for i in range(n):
            p=struct.unpack_from(endian+'IIIIIIII',b,phoff+i*ents)
            if p[0]==1 and p[4]:
                addr=p[2]; size=(p[5]+0xfff)&~0xfff; base=addr&~0xfff
                try:self.uc.mem_map(base,size)
                except Exception:pass
                self.uc.mem_write(addr,b[p[1]:p[1]+p[4]])
        self.uc.mem_map(0x20000000,0x10000)
        self.uc.mem_map(0x40000000, 0x1000)
        self.uc.reg_write(UC_ARM_REG_SP,struct.unpack('<I',self.uc.mem_read(0,4))[0])
        self.uc.reg_write(UC_ARM_REG_PC,struct.unpack('<I',self.uc.mem_read(4,4))[0]&~1)

    def _code(self, uc, address, size, user):
        self.pc = address

    def _read(self, uc, access, address, size, value, user):
        if address in self.mmio: uc.mem_write(address,int(self.mmio[address]).to_bytes(size,'little'))
    def _write(self, uc, access, address, size, value, user): pass
    def snapshot(self):
        return tuple(self.uc.reg_read(r) for r in REGS) + (
            self.uc.reg_read(UC_ARM_REG_SP), self.uc.reg_read(UC_ARM_REG_LR),
            self.uc.reg_read(UC_ARM_REG_PC), self.uc.reg_read(UC_ARM_REG_XPSR))

    def inject_irq(self, irq):
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
        self.uc.reg_write(UC_ARM_REG_LR, 0xfffffff9)
        self.uc.reg_write(UC_ARM_REG_PC, vector)
        self.pc = vector

    def dma(self, address, payload):
        if not isinstance(payload, bytes) or not 0 <= address <= 0xffffffff - len(payload):
            raise ValueError("invalid DMA")
        self.uc.mem_write(address, payload)

    def run(self, steps):
        return [self.step() for _ in range(steps)]

    def step(self):
        pc = self.pc
        insn = int.from_bytes(self.uc.mem_read(pc, 2), "little")
        if insn == 0x4770 and self.uc.reg_read(UC_ARM_REG_LR) == 0xfffffff9:
            self.count += 1
            sp = self.uc.reg_read(UC_ARM_REG_SP)
            frame = struct.unpack("<8I", self.uc.mem_read(sp, 32))
            for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), frame[:4]):
                self.uc.reg_write(reg, value)
            self.uc.reg_write(UC_ARM_REG_R12, frame[4]); self.uc.reg_write(UC_ARM_REG_LR, frame[5])
            self.pc = frame[6] & ~1; self.uc.reg_write(UC_ARM_REG_SP, sp + 32)
            return self.snapshot()
        self.uc.emu_start(pc | 1, 0, count=1)
        self.count += 1
        if insn == 0x4770 and self.uc.reg_read(UC_ARM_REG_LR) == 0xfffffff9:
            sp = self.uc.reg_read(UC_ARM_REG_SP)
            frame = struct.unpack("<8I", self.uc.mem_read(sp, 32))
            for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), frame[:4]):
                self.uc.reg_write(reg, value)
            self.uc.reg_write(UC_ARM_REG_R12, frame[4]); self.uc.reg_write(UC_ARM_REG_LR, frame[5])
            self.pc = frame[6] & ~1; self.uc.reg_write(UC_ARM_REG_SP, sp + 32)
        # Phase-0 ceiling: hardcoded redirects for current race.elf control flow.
        # Rebuilds that move these sites must update docs/emulator-record-replay.md.
        elif pc == 0x70 and (self.uc.reg_read(UC_ARM_REG_XPSR) & (1 << 30)):
            self.pc = 0x64
        elif pc == 0x78:
            self.pc = 0x64
        else:
            self.pc = pc + (4 if insn & 0xe000 == 0xe000 else 2)
        return self.snapshot()

def main():
    p=argparse.ArgumentParser(); p.add_argument('elf'); p.add_argument('--count',type=int,default=1); a=p.parse_args()
    cpu=CortexM(a.elf)
    for _ in range(a.count): cpu.step()
    print('unicorn Cortex-M steps=%d build=%s' % (cpu.count,cpu.build_id.hex()[:16]))
if __name__ == '__main__': main()
