[contributors-shield]: https://img.shields.io/github/contributors/Alessandro-Salerno/Hackasm.svg?style=flat-square
[contributors-url]: https://github.com/Alessandro-Salerno/Hackasm/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Alessandro-Salerno/Hackasm.svg?style=flat-square
[forks-url]: https://github.com/Alessandro-Salerno/Hackasm/network/members
[stars-shield]: https://img.shields.io/github/stars/Alessandro-Salerno/Hackasm.svg?style=flat-square
[stars-url]: https://github.com/Alessandro-Salerno/Hackasm/stargazers
[issues-shield]: https://img.shields.io/github/issues/Alessandro-Salerno/Hackasm.svg?style=flat-square
[issues-url]: https://github.com/Alessandro-Salerno/Hackasm/issues
[license-shield]: https://img.shields.io/github/license/Alessandro-Salerno/Hackasm.svg?style=flat-square
[license-url]: https://github.com/Alessandro-Salerno/Hackasm/blob/master/LICENSE.txt

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
![](https://tokei.rs/b1/github/Alessandro-Salerno/Hackasm)
![shield](https://img.shields.io/static/v1?label=version&message=0.1.1&color=blue) 


# Hackasm
Hackasm is an assembler made in a few days to complete the Sorint.lab HackersGen Hacking Challenge, and supports all instructions part of the VM-O-MATIC Specification while adding several handy macros to write cleaner and more powerful code

## Installing Hackasm
* Windows:
```
pip install git+https://github.com/Alessandro-Salerno/Hackasm
```
* macOS/Linux:
```
pip3 install git+https://github.com/Alessandro-Salerno/Hackasm
```

## Usage
- Windows: `py -m hackasm <input file>`
- Linux/macOS: `python3 -m hackasm <input file>`

## Writing Hackasm Assembly
Hackasm Assembly is quite straight-forward and fairly intuitive, but it sports a cuple of quarks which may set you off at first.
Following these rules and examples may help you write standard-fitting code:
- Start by creating a `data`section and a `text` section
- Create a `_swap` label in the `data` section and allocate 2 bytes
- Create a `_main` label in the `text` section (this will become the program's entry point)

**Keep in mind that:**
- All original VM-O-MATIC instructions use the format `<opcode> <operand>`
- All Hackasm macros start with a `.` and use the format `.<macro> <operands>`
- The Hackasm Linker Directive Language uses the `+` symbol to offset values and addresses as in `stry _swap+1` (Store Y at _swap address + 1) or `ldx 200+1` (Store 201 in X)
- The Hackasm Linker Directive Language uses the `|` symbol to access the higher and lower bytes of a 16 bit value as in `ldx 500|0` (Stores the higher byte) or `ldx 500|1` (Stores the lower byte)

Thus your Hackasm Assembly code should look like this:
```
.section data
  .label _swap
  .alloc 2                # Allocates two bytes here

  .label my_string
  .ascii "Hello, world"   # Allocates zero-terminated ASCII string here

.section text
  # This is where the program will start
  # This program prints the base pointer to `my_string`
  .label _main
    .ld16 my_string       # Loads 16 bit pointer to `my_string` in X and Y
    .pushregs             # Pushes Y and X (in this order) on the stack
    popx                  # Pops the top 8 bits of the stack into X
    out                   # Outputs X to stdout
    popx                  # Pops the top 8 bits of the stack into Y
    out                   # Outputs X to stdout
```

If everything goes smoothly, the output of the assembelr should look something like this:
```
Compiling...
Linking...
Linked bytecode size: 30 byte(s)
Linked labels:
  - _swap: 0x5
  - my_string: 0x7
  - _main: 0x14
Linked symbols:
```

The output of the assembler should be written to a file in the working directory called `vm_asm_out.txt` which, once opened, should reveal a hex sequence similar to this:
```
7000720014000048656C6C6F2C20776F726C640050075100B2B0B160B160
```

## Hackasm Macros
Hackasm includes several handy macros to help developers. Following is a list of all macros supported by the current stable version of Hackasm, along with a short explanation and example
| Macro | Syntax | Description | Example |
| ----- | ------ | ----------- | ------- |
| `.set` | `.set <name> <value>` | Defines a symbol to be used instead of a value | `.set INT8_MAX 255` |
| `.label` | `.label <name>` | Declares a label at the current position in the executable | `.label _main` |
| `.ascii` | `.ascii "<string>"` | Stores an ASCII string in a continuous region of memory starting at the current byte offset | `.ascii "Hello, world!"` |
| `.section` | `.section <section>` | Starts a new secion | `.section text ` |
| `.alloc` | `.alloc <num bytes>` | Allocates a continuous buffer starting at the current byte offset. The assembler runs no checks on the size! Make sure it fits | `.alloc 16` |
| `.strregs` | `.strregs <pointer>` | Stores X at `pointer` and Y at `pointer+1` | `.strregs _swap` |
| `.ldregs` | `.ldregs <pointer>` | Loads X from `pointer ` and  Y from `pointer+1` | `.ldregs _swap` |
| `.ld16` | `.ld16 <value or pointer>` | Loads a 16 bit value or pointer into X and Y. Higher bytes goes into Y and lower byte goes into X | `.ld16 2048` |
| `.pushregs` | `.pushregs` | Pushes Y and X on the stack (in this order) | `.pushregs` |
| `.add16` | `.add16 <value>` | Adds an 8 bit value to a 16 bit value. The 16 bit value **MUST** already be on the stack! | `.add16 1` |
| `.jump` | `.jump <address>` | Unconditional branch to `address` | `.jump program_exit` |
| `.zero` | `.zero` | Sets X and Y to 0 | `.zero` |
| `.popregs` | `.popregs` | Pops X and Y from the stack (in this order) | `.popregs` |
| `.rmregs` | `.rmregs` | Removes top 16 bits from the stack without altering X and Y | `.rmregs` |
| `.fetchregs` | `.fetchregs` | Reads X and Y from the stack (in this order) without popping | `.fetchregs` |

## License
Hackasm is licensed under the GPL v3 license. See [LICENSE](LICENSE) for details

## Notes
VM-O-MATIC and the accompanying specifications are proprietary software developed by [Sorint.lab S.p.A.](https://www.sorint.com/en/) for the [HackersGen Event](https://s4s.sorint.it/). Hackasm is in **NO WAY** affiliated with Sorint.lab S.p.A. and **IS NOT** a redistribution of software developed by Sorint.lab S.p.A. Hackasm has been developed solely by means of reverse engineering and official documentation by Sorint.lab S.p.A.
and is not intended to infringe Sorint.lab S.p.A.'s Intellectual Property. If you're a representatvie from Sorint.lab S.p.A. and would prefer for this project to be taken down, contact me at the E-Mail Address in my info box.
