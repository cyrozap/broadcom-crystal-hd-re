meta:
  id: bcm70012_fw
  endian: le
  title: BCM70012/BCM70010 firmware image
  license: CC0-1.0
seq:
  - id: firmware
    type: firmware
    size: _io.size - 36
  - id: signature
    type: signature
    size: 36
types:
  firmware:
    seq:
      - id: stream_arc
        size: 0x80000
      - id: vdec_outer_loop_arc
        size: 0xc0000
      - id: vdec_inner_loop_arc
        size-eos: true
  signature:
    seq:
      - id: len
        type: u4
      - id: data
        size: len
