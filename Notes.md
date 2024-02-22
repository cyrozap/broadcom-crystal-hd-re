# Reverse engineering notes


## General notes

- [BCM70012/BCM70010][bcm70010/bcm70012]
  - BCM70012 is some kind of bridge IC.
  - [BCM70010][bcm70010] is the video decoder IC.
    - Possibly a die-shrunk [BCM7411][bcm7411]/[BCM7412][bcm7412].
    - The block diagram of the BCM70010 matches that of the BCM7412 almost
      exactly.
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
- [BCM70015][bcm70015]
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
- Product briefs:
  - [BCM70010 Product Brief][bcm70010]
  - [BCM70010/BCM70012 Product Brief][bcm70010/bcm70012]
  - [BCM70015 Product Brief][bcm70015]
- Product web pages:
  - [BCM70010][bcm70010-web]
  - [BCM70012][bcm70012-web]
  - [BCM70015][bcm70015-web]
- Press releases:
  - [BCM70010/BCM70012][bcm70010/bcm70012-pr]
  - [BCM70015][bcm70015-pr]
- Schematics for laptops that have an onboard BCM70015:
  - [HP Mini 210-2003er / 110-3601er / 010153H00-600-G][010153h00-600-g]
  - [Samsung N220 / N210 / N150 / NB30][samsung]


[bcm70010/bcm70012]: https://web.archive.org/web/20240214223754if_/https://static6.arrow.com/aropdfconversion/ea0893d8b88c1224d0b011f1bcc23123748ead6d/70010_70012-pb01-r.pdf
[bcm70010]: https://web.archive.org/web/20240214225008if_/https://static6.arrow.com/aropdfconversion/17e2c4acba947affa1d89c6d7214304b1c852a8d/70010-pb01-r.pdf
[bcm70015]: https://web.archive.org/web/20240214232928if_/https://acerfans.ru/uploads/forum/files/1456776117_bcm70015.pdf
[bcm7411]: https://web.archive.org/web/20060111091139if_/http://www.broadcom.com/collateral/pb/7411-PB05-R.pdf
[bcm7412]: https://web.archive.org/web/20240214230054if_/https://www.digchip.com/datasheets/download_datasheet.php?id=3187850&part-number=BCM7412
[hmac]: https://en.wikipedia.org/wiki/HMAC
[arc_uart]: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/tty/serial/arc_uart.c
[cmac]: https://datatracker.ietf.org/doc/html/rfc4493
[isa-manual]: https://web.archive.org/web/20160618094913if_/http://me.bios.io/images/c/c6/ARC4._Programmers_reference.pdf
[binutils]: https://www.gnu.org/software/binutils/
[toolchain]: https://www.maintech.de/support/toolchains/
[wikipedia]: https://en.wikipedia.org/wiki/Broadcom_Crystal_HD
[driver]: https://github.com/yeradis/crystalhd
[bcm70010-web]: https://web.archive.org/web/20070606095145/http://www.broadcom.com/products/Consumer-Electronics/Media-PC-Solutions/BCM70010
[bcm70012-web]: https://web.archive.org/web/20071027080309/http://www.broadcom.com/products/Consumer-Electronics/Media-PC-Solutions/BCM70012
[bcm70015-web]: https://web.archive.org/web/20091226234150/http://www.broadcom.com/products/Consumer-Electronics/Netbook-and-Nettop-Solutions/BCM70015
[bcm70010/bcm70012-pr]: https://web.archive.org/web/20070614014131/http://www.broadcom.com/press/release.php?id=1010620
[bcm70015-pr]: https://web.archive.org/web/20091228045547/http://www.broadcom.com/press/release.php?id=s431589
[010153h00-600-g]: https://web.archive.org/web/20210726063354if_/https://www.abcelectronique.com/forum/attachment.php?attachmentid=48741#page=26
[samsung]: https://web.archive.org/web/20210726062516if_/https://www.informaticanapoli.it/download/SCHEMIELETTRICI/SAMSUNG/np-n220_n210_n150_nb30_bloomington_rev_0.9_sch.pdf#page=20
