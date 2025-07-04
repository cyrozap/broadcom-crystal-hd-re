#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2025  Forest Crossman <cyrozap@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Parses a CMSIS-SVD file and generates a C header file with register definitions.
"""


import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Field:
    """Represents a register field."""
    name: str
    bit_offset: int
    bit_width: int

@dataclass
class Register:
    """Represents a register."""
    name: str
    description: str
    address_offset: int
    size: int
    fields: list[Field] = field(default_factory=list)

    def add_field(self, field: Field):
        self.fields.append(field)

@dataclass
class Peripheral:
    """Represents a peripheral."""
    name: str
    base_address: int
    registers: list[Register] = field(default_factory=list)

    def add_register(self, register: Register):
        self.registers.append(register)

@dataclass
class Device:
    """Represents a device."""
    name: str
    peripherals: list[Peripheral] = field(default_factory=list)

    def add_peripheral(self, peripheral: Peripheral):
        self.peripherals.append(peripheral)


def parse_svd_to_device_tree(svd_content: str) -> Device:
    """Parses the SVD content and builds a device tree."""
    root = ET.fromstring(svd_content)
    device_name_elem = root.find('name')
    if device_name_elem is None:
        raise ValueError("SVD file missing device name")
    device = Device(device_name_elem.text)

    peripherals_elem = root.find('peripherals')
    if peripherals_elem is None:
        return device

    for periph_elem in peripherals_elem.findall('peripheral'):
        periph_name = periph_elem.find('name').text
        base_address = int(periph_elem.find('baseAddress').text, 0)
        peripheral = Peripheral(periph_name, base_address)

        registers_elem = periph_elem.find('registers')
        if registers_elem is not None:
            for reg_elem in registers_elem.findall('register'):
                reg_name = reg_elem.find('name').text
                description = reg_elem.find('description').text
                address_offset = int(reg_elem.find('addressOffset').text, 0)
                size = int(reg_elem.find('size').text)

                register = Register(reg_name, description, address_offset, size)

                fields_elem = reg_elem.find('fields')
                if fields_elem is not None:
                    for field_elem in fields_elem.findall('field'):
                        field_name = field_elem.find('name').text
                        bit_offset = int(field_elem.find('bitOffset').text)
                        bit_width = int(field_elem.find('bitWidth').text)
                        field = Field(field_name, bit_offset, bit_width)
                        register.add_field(field)

                peripheral.add_register(register)
        device.add_peripheral(peripheral)
    return device

def generate_header(device: Device) -> str:
    """Generates a C header file from the device tree."""
    lines: list[str] = [
        '#ifndef MACFILE_H__',
        '#define MACFILE_H__',
    ]

    # Collect all register defines to calculate max length for alignment
    all_reg_defs = []
    for periph in device.peripherals:
        for reg in periph.registers:
            full_reg_name = f"{periph.name}_{reg.name}"
            all_reg_defs.append(full_reg_name)

    max_reg_len = max(len(name) for name in all_reg_defs) if all_reg_defs else 0

    # Generate register defines
    for periph in sorted(device.peripherals, key=lambda p: p.base_address):
        periph_has_regs = False
        for reg in sorted(periph.registers, key=lambda r: r.address_offset):
            full_reg_name = f"{periph.name}_{reg.name}"
            abs_addr = periph.base_address + reg.address_offset
            lines.append(f'#define {full_reg_name.ljust(max_reg_len + 2)} 0x{abs_addr:08x} /* {reg.description} */')
            periph_has_regs = True
        if periph_has_regs:
            lines.append('')
    lines.append('')

    # Collect all field defines to calculate max length
    all_field_defs = []
    for periph in device.peripherals:
        for reg in periph.registers:
            if not reg.fields:
                continue
            full_reg_name = f"{periph.name}_{reg.name}"
            for field in reg.fields:
                full_field_prefix = f"{full_reg_name}_{field.name}"
                all_field_defs.append(f"{full_field_prefix}_MASK")
                all_field_defs.append(f"{full_field_prefix}_ALIGN")
                all_field_defs.append(f"{full_field_prefix}_BITS")
                all_field_defs.append(f"{full_field_prefix}_SHIFT")

    max_field_len = max(len(name) for name in all_field_defs) if all_field_defs else 0

    # Generate field defines
    for periph in sorted(device.peripherals, key=lambda p: p.base_address):
        for reg in sorted(periph.registers, key=lambda r: r.address_offset):
            if not reg.fields:
                continue

            full_reg_name = f"{periph.name}_{reg.name}"
            for field in sorted(reg.fields, key=lambda f: f.bit_offset):
                full_field_prefix = f"{full_reg_name}_{field.name}"
                mask = ((1 << field.bit_width) - 1) << field.bit_offset

                lines.append(f'#define {(full_field_prefix + "_MASK").ljust(max_field_len + 2)} 0x{mask:08x}')
                lines.append(f'#define {(full_field_prefix + "_ALIGN").ljust(max_field_len + 2)} 0')
                lines.append(f'#define {(full_field_prefix + "_BITS").ljust(max_field_len + 2)} {field.bit_width}')
                lines.append(f'#define {(full_field_prefix + "_SHIFT").ljust(max_field_len + 2)} {field.bit_offset}')
                lines.append('')
            lines.append('')

    lines.append('#endif /* #ifndef MACFILE_H__ */')
    lines.append('')
    lines.append('/* End of File */')

    return '\n'.join(lines)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Convert CMSIS-SVD file to C header format.")
    parser.add_argument("-o", "--output", help="Path to the output header file. Defaults to stdout.")
    parser.add_argument("svd_file", help="Path to the SVD file.")
    args = parser.parse_args()

    try:
        with open(args.svd_file, 'r') as f:
            svd_content = f.read()
    except FileNotFoundError:
        print(f"Error: SVD file not found at {args.svd_file}", file=sys.stderr)
        sys.exit(1)

    try:
        device = parse_svd_to_device_tree(svd_content)
        header_content = generate_header(device)
    except Exception as e:
        print(f"Error processing SVD file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(header_content)
    else:
        sys.stdout.write(header_content)


if __name__ == "__main__":
    main()
