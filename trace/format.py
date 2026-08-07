"""Validated compact trace contract."""
import struct
import zlib

MAGIC = b"DTRC"
VERSION = 2
MAX_BUILD_ID = 64
MAX_EVENTS = 1_000_000
MAX_INSTRUCTIONS = (1 << 64) - 1


class TraceError(ValueError):
    pass


def varint(n):
    if not isinstance(n, int) or n < 0 or n > MAX_INSTRUCTIONS:
        raise TraceError("invalid integer")
    out = bytearray()
    while n > 127:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)


def readvar(b, i):
    n = shift = 0
    while i < len(b):
        x = b[i]
        i += 1
        if shift == 63 and x > 1:
            raise TraceError("varint overflow")
        n |= (x & 127) << shift
        if x < 128:
            if shift and x == 0:
                raise TraceError("non-minimal varint")
            return n, i
        shift += 7
        if shift > 63:
            raise TraceError("varint overflow")
    raise TraceError("truncated varint")


class Trace:
    def __init__(self, build_id=b"demo-v1", events=()):
        if (not isinstance(build_id, (bytes, bytearray)) or
                not 1 <= len(build_id) <= MAX_BUILD_ID or b"\0" in build_id):
            raise TraceError("invalid build id")
        self.build_id = bytes(build_id)
        self.events = list(events)

    def encode(self):
        if len(self.events) > MAX_EVENTS:
            raise TraceError("too many events")
        out = bytearray(MAGIC + bytes([VERSION, len(self.build_id)]) + self.build_id)
        last = 0
        last_kind = 0
        for event in self.events:
            if (not isinstance(event, tuple) or len(event) < 2 or
                    not isinstance(event[0], int) or event[0] not in range(1, 8) or
                    not isinstance(event[1], int) or event[1] < last or
                    (event[1] == last and event[0] < last_kind)):
                raise TraceError("bad event ordering")
            kind, point = event[:2]
            out += bytes([kind]) + varint(point - last)
            last, last_kind = point, kind
            try:
                if kind == 1:
                    if not isinstance(event[2], int) or not 0 <= event[2] <= 255:
                        raise TraceError("invalid irq")
                    out += struct.pack("<B", event[2])
                elif kind == 2:
                    address, value, width = event[2:5]
                    if width not in (1, 2, 4) or not 0 <= address <= 0xffffffff:
                        raise TraceError("invalid mmio")
                    if not isinstance(value, int) or not 0 <= value < (1 << (8 * width)):
                        raise TraceError("invalid mmio value")
                    out += struct.pack("<IIB", address, value, width)
                elif kind == 3:
                    address, length, payload = event[2:5]
                    if (not isinstance(address, int) or not 0 <= address <= 0xffffffff or
                            not isinstance(length, int) or not 0 <= length <= 65535 or
                            address + length > 0x100000000 or
                            not isinstance(payload, bytes) or len(payload) != length):
                        raise TraceError("bad dma payload")
                    out += struct.pack("<IIH", address, length, length) + payload
                else:
                    value = event[2]
                    if not isinstance(value, int) or not 0 <= value <= 0xffffffff:
                        raise TraceError("invalid event value")
                    out += struct.pack("<I" if kind in (4, 6, 7) else "<B", value)
            except (IndexError, TypeError, ValueError, struct.error):
                raise TraceError("malformed event")
        return bytes(out) + struct.pack("<I", zlib.crc32(out))

    @classmethod
    def decode(cls, data):
        if not isinstance(data, (bytes, bytearray)) or len(data) < 10 or data[:4] != MAGIC or data[4] != VERSION:
            raise TraceError("bad header")
        n = data[5]
        end = 6 + n
        if not 1 <= n <= MAX_BUILD_ID or b"\0" in data[6:end] or len(data) < end + 4:
            raise TraceError("truncated header")
        body = data[:-4]
        if struct.unpack("<I", data[-4:])[0] != zlib.crc32(body):
            raise TraceError("checksum mismatch")
        i = end
        last = last_kind = 0
        events = []
        while i < len(body):
            kind = body[i]
            i += 1
            point_delta, i = readvar(body, i)
            point = last + point_delta
            if point > MAX_INSTRUCTIONS or point < last or (point == last and kind < last_kind):
                raise TraceError("noncanonical event ordering")
            last, last_kind = point, kind
            try:
                if kind == 1:
                    events.append((kind, point, body[i])); i += 1
                elif kind == 2:
                    address, value, width = struct.unpack_from("<IIB", body, i); i += 9
                    if width not in (1, 2, 4) or value >= 1 << (8 * width): raise TraceError("invalid mmio")
                    events.append((kind, point, address, value, width))
                elif kind == 3:
                    address, length, payload_length = struct.unpack_from("<IIH", body, i); i += 10
                    if payload_length != length or address + length > 0x100000000 or i + length > len(body): raise TraceError("DMA length mismatch")
                    events.append((kind, point, address, length, body[i:i + length])); i += length
                elif kind in (4, 6, 7):
                    value = struct.unpack_from("<I", body, i)[0]; i += 4; events.append((kind, point, value))
                elif kind == 5:
                    events.append((kind, point, body[i])); i += 1
                else:
                    raise TraceError("unknown event")
            except (IndexError, struct.error):
                raise TraceError("truncated event")
            if len(events) > MAX_EVENTS: raise TraceError("too many events")
        return cls(body[6:6 + n], events)
