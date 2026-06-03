# RE Phases

Always triage -> static -> decompile/disassemble -> dynamic. Dynamic target
execution is Docker/sandbox-only. Record proof or disproof with citations.

## Universal

`file`; size; `sha256sum`; `strings -n 6` plus UTF-16; grep URLs/paths/keys/
errors/banners/magic; `binwalk -E` or entropy script; map unknowns to `paths.md`.

## Binary

Structure: `readelf`, `objdump`, `nm`, PE headers/imports, `otool`. Decompile:
`r2 -A`/`aaa`/`afl`/`pdf` or Ghidra headless; use child cards for hard functions.
Dynamic in Docker: `gdb`, `strace`, `ltrace`. Crypto: constants, S-boxes, IVs,
key schedules; reproduce in `derived/` and validate.

## Firmware

Extract with `binwalk -e`, `--dd`, filesystem carvers; recover bootloader, `/etc`,
init, keys. Classify arch/RTOS/Linux/update format. Route binaries to Binary.
Emulate with QEMU/Firmadyne-style flow in Docker. UART/JTAG/SPI requires inbox
authorization.

## Mobile

APK: `apktool d`, `jadx`, manifest components/permissions/exports/network config.
IPA: unzip, `Info.plist`, entitlements, Mach-O. Native libs -> Binary. Dynamic:
authorized emulator/sandbox only; Frida for traces, decrypted strings, pinning.

## Protocol

Parse `.pcap`/`.pcapng`/`.btsnoop` with `scapy`, `pyshark`, `tshark`; split by
direction/endpoint/handle/port/stream. Infer length/opcode/seq/payload/CRC as
`[HYPOTHESIS]`. Build `derived/parse.py --selftest`; validate on held-out data.
Replay/synthesis needs explicit live scope.

## Unknown

Run Universal; route components. Treat custom formats like protocols.
