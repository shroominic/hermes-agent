# Tool Matrix

Missing tool: inbox request + fallback note, not automatic stop.

| Need | Primary | Fallback | Run |
|---|---|---|---|
| Type/hash | `file`, `sha256sum` | hexdump | host |
| Strings | `strings` | `rabin2 -z` | host |
| Entropy/packing | `binwalk -E` | entropy script | host |
| Firmware extract | `binwalk -e`, `unsquashfs` | `dd` carve | host |
| Symbols/sections | `readelf`, `objdump`, `nm`, `rabin2 -I` | `otool` | host |
| Decompile | radare2, Ghidra | `objdump -d` | host |
| Android | `jadx`, `apktool` | `unzip`, `aapt` | host |
| Runtime trace | `strace`, `ltrace`, `gdb` | `qemu-user` | Docker |
| Hooking | Frida | emulator instrumentation | Docker/emulator |
| Firmware emu | QEMU | static only | Docker |
| Captures | `scapy`, `pyshark`, `tshark` | byte parser | host |
| Crypto | Python + `pycryptodome` | local script | host |

Static inspection/capture parsing may run on host. Target execution, tracing,
hooking, fuzzing, or emulation must run in Docker/sandbox. Record tool versions.
