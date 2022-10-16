meta:
  id: arcextmap
  title: ARC extension information in Crystal HD firmware ELF files
  license: GPL-3.0-or-later
doc: "Partly based on opcodes/arc-ext.{c,h} from GNU binutils"
seq:
  - id: records
    type: record
    repeat: eos
types:
  record:
    seq:
      - id: len
        type: u1
      - id: type
        type: u1
        enum: ext
      - id: value
        size: len - 2
        type:
          switch-on: type
          cases:
            ext::instruction: instruction
            ext::core_register: core_register
            ext::aux_register: aux_register
            ext::cond_code: cond_code
    enums:
      ext:
        0: instruction
        1: core_register
        2: aux_register
        3: cond_code
    types:
      instruction:
        seq:
          - id: opcode_maj
            type: u1
          - id: opcode_min
            type: u1
          - id: flags
            type: u1
          - id: name
            type: strz
            encoding: ascii
            size-eos: true
      core_register:
        seq:
          - id: value
            type: u1
          - id: name
            type: strz
            encoding: ascii
            size-eos: true
      aux_register:
        seq:
          - id: value
            type: u4be
          - id: name
            type: strz
            encoding: ascii
            size-eos: true
      cond_code:
        seq:
          - id: value
            type: u1
          - id: name
            type: strz
            encoding: ascii
            size-eos: true
