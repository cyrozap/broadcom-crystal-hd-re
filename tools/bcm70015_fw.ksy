meta:
  id: bcm70015_fw
  endian: le
  title: BCM70015 firmware image
  license: CC0-1.0
seq:
  - id: firmware
    size: _io.size - 20
  - id: signature
    type: signature
    size: 20
types:
  signature:
    seq:
      - id: len
        type: u4
      - id: data
        size: len
