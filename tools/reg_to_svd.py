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
Parses a C header file with register definitions and generates a CMSIS-SVD file.
"""


import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from io import TextIOWrapper
from typing import DefaultDict, Iterable, NamedTuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring


DEFINE_RE = re.compile(r'^#define\s+([a-zA-Z0-9_]+)\s+((?:0x[0-9a-fA-F]+)|[0-9]+)\s*(?:/\*\s*(.*?)\s*\*/)?')
FIELD_COMMENT_RE = re.compile(r'/\*\s*([a-zA-Z0-9_]+)\s*::\s*([a-zA-Z0-9_ ]+)\s*::\s*(.*?)\s*\[(\d+):(\d+)\]\s*\*/')
REGISTER_COMMENT_RE = re.compile(r'/\*\s*([a-zA-Z0-9_]+)\s*::\s*([^:]+?)\s*\*/')


@dataclass
class Field:
    """Represents a register field."""
    name: str
    description: str
    bit_offset: int
    bit_width: int

@dataclass
class Register:
    """Represents a register."""
    name: str
    description: str
    address_offset: int
    size: int = 32
    fields: list[Field] = field(default_factory=list)

    def add_field(self, field: Field):
        self.fields.append(field)

@dataclass
class Peripheral:
    """Represents a peripheral."""
    name: str
    base_address: int
    description: str
    registers: dict[str, Register] = field(default_factory=dict)

    def add_register(self, register: Register):
        self.registers[register.name] = register

@dataclass
class Device:
    """Represents a device."""
    name: str
    description: str
    peripherals: dict[str, Peripheral] = field(default_factory=dict)

    def add_peripheral(self, peripheral: Peripheral):
        self.peripherals[peripheral.name] = peripheral

class RegAddrDesc(NamedTuple):
    """Holds the address and description for a register definition."""
    addr: int
    desc: str

@dataclass
class ParsedHeader:
    """Holds information parsed from the header file."""
    registers_info: dict[str, RegAddrDesc]
    fields_info: DefaultDict[str, dict[str, int]]
    field_descriptions: dict[str, str]
    reg_fqn_to_periph: dict[str, str]
    reg_fqn_to_regname: dict[str, str]

class RegisterInfo(NamedTuple):
    """Holds information about a register definition."""
    reg_name: str
    addr: int
    desc: str
    reg_define: str


def parse_header_lines(lines: Iterable[str]) -> ParsedHeader:
    """Parses header lines into intermediate data structures.

    Args:
        lines: An iterable of strings, where each string is a line from the header file.

    Returns:
        A ParsedHeader object containing the parsed information.
    """

    # Data stores
    registers_info: dict[str, RegAddrDesc] = {}
    fields_info: DefaultDict[str, dict[str, int]] = defaultdict(dict)
    field_descriptions: dict[str, str] = {}
    reg_fqn_to_periph: dict[str, str] = {}
    reg_fqn_to_regname: dict[str, str] = {}
    last_field_info: dict[str, str] | None = None

    # Single pass over the lines to parse all information
    for line in lines:
        line = line.strip()

        # Reset field comment context if we encounter a line that is not a
        # define, comment, or empty.
        if not (line.startswith(('#define', '/*')) or not line):
            last_field_info = None

        # Handle defines
        m_def: re.Match | None = DEFINE_RE.match(line)
        if m_def:
            name: str
            value_str: str
            comment: str | None
            name, value_str, comment = m_def.groups()

            is_field_prop: bool = False
            if name.endswith(('_BITS', '_SHIFT', '_ALIGN')):
                is_field_prop = True
            elif name.endswith('_MASK'):
                if not comment or 'Register' not in comment:
                    is_field_prop = True

            value: int
            if is_field_prop:
                prop: str = name.rsplit('_', 1)[1]
                prefix: str = name.rsplit('_', 1)[0]
                value = int(value_str, 0)
                if prop == 'SHIFT':
                    fields_info[prefix]['bitOffset'] = value
                elif prop == 'BITS':
                    fields_info[prefix]['bitWidth'] = value

                if last_field_info and prefix.startswith(last_field_info['key_base']):
                    if prefix not in field_descriptions:
                        field_descriptions[prefix] = last_field_info['desc']
                    last_field_info = None  # Consume the description
            elif value_str.startswith('0x'):
                value = int(value_str, 16)
                desc = (comment.replace("Register", "").strip() if comment else name)
                registers_info[name] = RegAddrDesc(value, desc)

        # Handle comments for FQN and field descriptions
        periph_name: str | None = None
        reg_name_from_comment: str | None = None
        reg_name: str
        field_match: re.Match | None = FIELD_COMMENT_RE.search(line)
        if field_match:
            msb: str
            lsb: str
            periph_name, reg_name_from_comment, desc, msb, lsb = field_match.groups()
            reg_name = reg_name_from_comment.replace(' ', '_')
            field_key_base: str = f"{periph_name}_{reg_name}"
            last_field_info = {'key_base': field_key_base, 'desc': desc.strip()}
        else:
            reg_match: re.Match | None = REGISTER_COMMENT_RE.search(line)
            if reg_match:
                periph_name, reg_name_from_comment = reg_match.groups()

        if periph_name and reg_name_from_comment and '::' not in reg_name_from_comment:
            reg_name = reg_name_from_comment.strip().replace(' ', '_')
            reg_fqn: str = f"{periph_name}_{reg_name}"
            if reg_fqn not in reg_fqn_to_periph:
                reg_fqn_to_periph[reg_fqn] = periph_name
                reg_fqn_to_regname[reg_fqn] = reg_name

    return ParsedHeader(
        registers_info=registers_info,
        fields_info=fields_info,
        field_descriptions=field_descriptions,
        reg_fqn_to_periph=reg_fqn_to_periph,
        reg_fqn_to_regname=reg_fqn_to_regname,
    )

def group_registers_by_peripheral(
    registers_info: dict[str, RegAddrDesc],
    reg_fqn_to_periph: dict[str, str],
    reg_fqn_to_regname: dict[str, str]
) -> DefaultDict[str, list[RegisterInfo]]:
    """Groups registers into peripherals.

    Args:
        registers_info: A dictionary with register define names as keys and tuples
            of address and description as values.
        reg_fqn_to_periph: A dictionary mapping fully qualified register names to
            peripheral names.
        reg_fqn_to_regname: A dictionary mapping fully qualified register names to
            register names.

    Returns:
        A dictionary with peripheral names as keys and lists of RegisterInfo
        objects as values.
    """

    peripherals: DefaultDict[str, list[RegisterInfo]] = defaultdict(list)
    for reg_define, (addr, desc) in registers_info.items():
        periph_name: str | None = reg_fqn_to_periph.get(reg_define)
        reg_name: str | None = reg_fqn_to_regname.get(reg_define)

        if not periph_name:
            # Fallback for registers not found directly, e.g. revision regs.
            # Match against the start of the define.
            for r_fqn in sorted(reg_fqn_to_periph.keys(), key=len, reverse=True):
                if reg_define.startswith(r_fqn):
                    periph_name = reg_fqn_to_periph[r_fqn]
                    reg_name = reg_define[len(periph_name)+1:]
                    break

        if periph_name and reg_name:
            peripherals[periph_name].append(RegisterInfo(reg_name, addr, desc or reg_name, reg_define))
        else:
            print(f"Warning: Could not determine peripheral for register {reg_define}", file=sys.stderr)

    return peripherals

def build_device_tree(
    device_name: str,
    device_description: str,
    peripherals: DefaultDict[str, list[RegisterInfo]],
    fields_info: DefaultDict[str, dict[str, int]],
    field_descriptions: dict[str, str]
) -> Device:
    """Builds the device tree from peripheral groups.

    Args:
        device_name: The name for the device.
        device_description: The description for the device.
        peripherals: A dictionary with peripheral names as keys and lists of
            RegisterInfo objects as values.
        fields_info: A dictionary containing information about bit fields.
        field_descriptions: A dictionary mapping field prefixes to their descriptions.

    Returns:
        A Device object representing the complete device tree.
    """

    device: Device = Device(device_name, device_description)
    all_reg_fqns: set[str] = set()
    for periph_name, regs in peripherals.items():
        for reg_info in regs:
            all_reg_fqns.add(reg_info.reg_define)

    for periph_name, regs in peripherals.items():
        if not regs:
            continue
        base_address: int = min(r.addr for r in regs) if regs else 0
        peripheral: Peripheral = Peripheral(periph_name, base_address, f"{periph_name} Peripheral")
        device.add_peripheral(peripheral)

        for reg_info in sorted(regs, key=lambda r: r.addr):
            register: Register = Register(reg_info.reg_name, reg_info.desc, reg_info.addr - base_address)
            peripheral.add_register(register)

            # Find fields for this register
            for field_prefix, props in fields_info.items():
                if field_prefix.startswith(reg_info.reg_define + '_'):
                    # Check if this field belongs to a more specific (longer) register name
                    is_more_specific_match: bool = False
                    for other_reg_fqn in all_reg_fqns:
                        if len(other_reg_fqn) > len(reg_info.reg_define) and \
                           other_reg_fqn.startswith(reg_info.reg_define) and \
                           field_prefix.startswith(other_reg_fqn + '_'):
                            is_more_specific_match = True
                            break
                    if is_more_specific_match:
                        continue

                    field_name: str = field_prefix[len(reg_info.reg_define)+1:]
                    if 'bitOffset' in props and 'bitWidth' in props:
                        field_desc: str = field_descriptions.get(field_prefix, field_name)
                        field: Field = Field(field_name, field_desc, props['bitOffset'], props['bitWidth'])
                        register.add_field(field)

    return device

def parse_header_to_device_tree(lines: Iterable[str], device_name: str, device_description: str) -> Device:
    """Parses the header content and builds a device tree.

    Args:
        lines: An iterable of strings, where each string is a line from the header file.
        device_name: The name for the device.
        device_description: The description for the device.

    Returns:
        A Device object representing the parsed device tree.
    """

    parsed_data: ParsedHeader = parse_header_lines(lines)

    peripherals: DefaultDict[str, list[RegisterInfo]] = group_registers_by_peripheral(
        parsed_data.registers_info, parsed_data.reg_fqn_to_periph, parsed_data.reg_fqn_to_regname)

    return build_device_tree(
        device_name,
        device_description,
        peripherals,
        parsed_data.fields_info,
        parsed_data.field_descriptions)

def generate_svd(device: Device) -> str:
    """Generates the SVD XML content from the device tree.

    Args:
        device: The device tree object.

    Returns:
        A string containing the SVD XML content.
    """

    dev_elem: Element = Element('device', schemaVersion="1.3", xmlns_xs="http://www.w3.org/2001/XMLSchema-instance", xs_noNamespaceSchemaLocation="CMSIS-SVD.xsd")

    SubElement(dev_elem, "name").text = device.name
    SubElement(dev_elem, "version").text = "1.0"
    SubElement(dev_elem, "description").text = device.description
    SubElement(dev_elem, "addressUnitBits").text = "8"
    SubElement(dev_elem, "width").text = "32"

    peripherals_elem: Element = SubElement(dev_elem, "peripherals")

    for periph_name, peripheral in sorted(device.peripherals.items()):
        periph_elem: Element = SubElement(peripherals_elem, "peripheral")
        SubElement(periph_elem, "name").text = peripheral.name
        SubElement(periph_elem, "description").text = peripheral.description
        SubElement(periph_elem, "baseAddress").text = f"0x{peripheral.base_address:08X}"

        registers_elem: Element = SubElement(periph_elem, "registers")
        for reg_name, register in sorted(peripheral.registers.items()):
            reg_elem: Element = SubElement(registers_elem, "register")
            SubElement(reg_elem, "name").text = register.name
            SubElement(reg_elem, "description").text = register.description
            SubElement(reg_elem, "addressOffset").text = f"0x{register.address_offset:X}"
            SubElement(reg_elem, "size").text = str(register.size)
            SubElement(reg_elem, "access").text = "read-write"

            if register.fields:
                fields_elem: Element = SubElement(reg_elem, "fields")
                for field in sorted(register.fields, key=lambda f: f.bit_offset):
                    field_elem: Element = SubElement(fields_elem, "field")
                    SubElement(field_elem, "name").text = field.name
                    SubElement(field_elem, "description").text = field.description
                    SubElement(field_elem, "bitOffset").text = str(field.bit_offset)
                    SubElement(field_elem, "bitWidth").text = str(field.bit_width)

    # Pretty print
    rough_string: bytes = tostring(dev_elem, 'utf-8')
    reparsed: minidom.Document = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main() -> None:
    """Main entry point for the script."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Convert Broadcom register header to CMSIS-SVD format.")
    parser.add_argument("-o", "--output",
                        help="Path to the output SVD file. Defaults to stdout.")
    parser.add_argument("-n", "--device-name",
                        default="Device Name",
                        help="Name of the device.")
    parser.add_argument("-d", "--device-description",
                        default="Device Description",
                        help="Description of the device.")
    parser.add_argument("header_file",
                        nargs="?",
                        type=argparse.FileType("r"),
                        default=sys.stdin,
                        help="Path to the C header file. If not provided, reads from standard input.")
    args: argparse.Namespace = parser.parse_args()

    header_content: TextIOWrapper = args.header_file

    device: Device = parse_header_to_device_tree(header_content, args.device_name, args.device_description)
    svd_content: str = generate_svd(device)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(svd_content)
    else:
        sys.stdout.write(svd_content)


if __name__ == "__main__":
    main()
