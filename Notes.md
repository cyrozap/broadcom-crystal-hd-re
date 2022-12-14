# Reverse engineering notes


## General notes

- BCM70012/BCM70010
  - BCM70012 is some kind of bridge IC.
  - BCM70010 is the video decoder IC.
    - Possibly a die-shrunk BCM7411/BCM7412.
  - Three ARC cores:
    - Stream ARC (BCM70012?)
    - Video Decoder Outer Loop ARC (BCM70010)
    - Video Decoder Inner Loop ARC (BCM70010)
  - Firmware is verified with an [HMAC-SHA256][hmac] signature.
    - Verification can be bypassed via the following method:
      1. Follow the normal startup procedure, but stop before uploading any
         firmware.
      2. Upload the signed firmware the normal way (the one that simultaneously
         loads it into DRAM and verifies the signature), but do not start the
         firmware.
      3. Use direct DRAM writes to overwrite the previously-uploaded signed
         firmware with your unsigned firmware.
      4. Release the CPU from reset.
    - It may be possible to extract the HMAC key using a side-channel attack.
- BCM70015
  - Three cores (one ARM, two ARC):
    - System Management ARM
    - Video Decoder Outer Loop ARC
    - Video Decoder Inner Loop ARC
  - ARC firmware is stored as ELF files within the ARM firmware.
  - ARC UART is [this][arc_uart].
  - Firmware is verified with an [AES-CMAC][cmac] signature.
    - It may be possible to extract the AES key using a side-channel attack.
- ARC cores
  - Little-endian ARC6 (pre-ARC600).
  - An ISA manual for this architecture can be downloaded [here][isa-manual].
  - Version 2.25.1 of [GNU binutils][binutils] is the last version to support
    this architecture.
    - Configure with `./configure --target=arc-elf32`.
    - Assemble code with `arc-elf32-as -marc6`.
  - The last version of GCC to support this architecture is version 4.5.4, but
    the code has bitrotted significantly and can't be built as-is on modern
    systems.
  - A complete toolchain precompiled for x86 can be downloaded
    [here][toolchain], but it uses extremely old versions of GCC and binutils
    (GCC 3.4.5 and binutils 2.15).


## More info

- [Wikipedia][wikipedia]
- [Out-of-tree kernel module, userspace library, and firmware][driver]


[hmac]: https://en.wikipedia.org/wiki/HMAC
[arc_uart]: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/tty/serial/arc_uart.c
[cmac]: https://datatracker.ietf.org/doc/html/rfc4493
[isa-manual]: https://web.archive.org/web/20160618094913if_/http://me.bios.io/images/c/c6/ARC4._Programmers_reference.pdf
[binutils]: https://www.gnu.org/software/binutils/
[toolchain]: https://www.maintech.de/support/toolchains/
[wikipedia]: https://en.wikipedia.org/wiki/Broadcom_Crystal_HD
[driver]: https://github.com/yeradis/crystalhd
