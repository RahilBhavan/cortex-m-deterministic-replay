# DTRC v2 wire format

This page is the sole wire-spec owner. The exact implementation is `trace/format.py`.

## Container

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | ASCII `DTRC` |
| 4 | 1 | version `2` |
| 5 | 1 | build-ID length `N` |
| 6 | N | 1–64 non-NUL build-ID bytes |
| … | variable | ordered events |
| end-4 | 4 | little-endian CRC32 of every preceding byte |

Integers are unsigned. Varints are little-endian base-128, minimally encoded, and limited to 64 bits. Event point is the cumulative instruction count; points ascend, and tags ascend for equal points. Unknown tags, trailing bytes, malformed lengths, overflow, bad CRC, and nonminimal varints are rejected.

## Event tags

| Tag | Name | Payload after point delta | Encoding |
|---:|---|---|---|
| 1 | IRQ | IRQ number | 1 byte, 0–255 |
| 2 | MMIO | address, value, width | `<IIB`; width 1/2/4 |
| 3 | DMA | address, declared length, separately encoded payload length, bytes | address u32 + declared length u32 + payload length u16 + payload bytes; the two lengths must be equal; length ≤65535 |
| 4 | checkpoint | value | little-endian u32 |
| 5 | byte marker | value | 1 byte |
| 6 | memory/status value | value | little-endian u32 |
| 7 | external value | value | little-endian u32 |

Tag 2 address/value are 32-bit and the value must fit width. Tag 3 uses address u32, declared length u32, separately encoded payload length u16, and payload bytes; the lengths must be equal, the decoder rejects a mismatch, length ≤65535, and address + length must stay within 32-bit address space. Maximum events is 1,000,000; maximum instruction point is `2^64-1`.

## Canonical example

The demo contains seven events, one of each tag, and encodes to 66 bytes. That is 9.43 bytes/event. This is not a rate: no bytes/sec value is defined without a timebase.

## Host/RTL contract

The RTL transports the exact ordered encoded bytes. It does not parse tags 1–3 or 4–7, reserialize, or validate CRC. `overflow` and `accepted_count` are sideband status; any overflow invalidates the capture until reset.

## Validation

`Trace.encode` validates bounds and ordering; `Trace.decode` validates header, CRC, canonical varints, payload lengths, ordering, and event count. Tests cover 10,000 deterministic randomized round trips plus malformed/boundary cases.
