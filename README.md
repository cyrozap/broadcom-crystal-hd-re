# Broadcom Crystal HD Reverse Engineering


## Quick start


### Software dependencies

* Python 3
* [Kaitai Struct Compiler][ksc]
* [Kaitai Struct Python Runtime][kspr]


### Procedure

1. Install dependencies.
2. Run `make` in the [tools](tools) directory to generate the parser modules.
3. Obtain the firmware binaries you're interested in. You can download all the
   publicly-available Crystal HD firmware using the
   [download.sh](firmware/download.sh) script in the [firmware](firmware)
   directory.
4. Explore the firmware with [the Kaitai Web IDE][ide] and the Kaitai Struct
   definition (`*.ksy`) files in the [tools](tools) directory.


## Reverse engineering notes

See [Notes.md](Notes.md).


## License

Except where otherwise noted:

* All software in this repository (e.g., tools for unpacking and generating
  firmware, tools for building documentation, etc.) is made available under the
  [GNU General Public License, version 3 or later][gpl].
* All copyrightable content that is not software (e.g., chip register and
  programming manuals, reverse engineering notes, this README file, etc.) is
  licensed under the
  [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].


[ksc]: https://github.com/kaitai-io/kaitai_struct_compiler
[kspr]: https://github.com/kaitai-io/kaitai_struct_python_runtime
[ide]: https://ide.kaitai.io/
[gpl]: COPYING.txt
[cc-by-sa]: https://creativecommons.org/licenses/by-sa/4.0/
