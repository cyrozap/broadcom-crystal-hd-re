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
- BCM70015
  - Three cores (one ARM, two ARC):
    - System Management ARM
    - Video Decoder Outer Loop ARC
    - Video Decoder Inner Loop ARC
  - ARC firmware is stored as ELF files within the ARM firmware.
  - ARC UART is [this][arc_uart].

- ARC cores:
  - Little-endian ARC6 (pre-ARC600).


## More info

- [Wikipedia][wikipedia]
- [Out-of-tree kernel module, userspace library, and firmware][driver]


[arc_uart]: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/tty/serial/arc_uart.c
[wikipedia]: https://en.wikipedia.org/wiki/Broadcom_Crystal_HD
[driver]: https://github.com/yeradis/crystalhd