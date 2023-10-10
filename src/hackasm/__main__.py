import sys
import math


def to_linked_repr(value: str, must_be_hex=False):
    if isinstance(value, int):
        return False, value, (str(value) if not must_be_hex else hex(value).replace("0x", "").upper())

    if value.startswith("0x"):
        return True, int(value, 16), value.replace("0x", "").upper()

    if value.startswith("0b"):
        return True, int(value, 2), hex(int(value, 2)).replace("0x", "").upper()

    if value.isdecimal():
        return True, int(value), hex(int(value)).replace("0x", "").upper()

    return False, value, value


class VmInstructionInfo:
    def __init__(self, opcode: str, hasarg=True, argsize=1, maxarg=None) -> None:
        self.opcode = opcode
        self.hasarg = hasarg
        self.argsize = argsize
        self.maxarg = maxarg
        if self.maxarg == None:
            self.maxarg = int(math.pow(2, 8 * self.argsize))


VM_INSTRUCTIONS = {
    "CLD": VmInstructionInfo(opcode="40", hasarg=False, argsize=0),
    "LDX": VmInstructionInfo(opcode="50", hasarg=True, argsize=1),
    "LDY": VmInstructionInfo(opcode="51", hasarg=True, argsize=1),
    "STRX": VmInstructionInfo(opcode="52", hasarg=True, argsize=2, maxarg=4096),
    "STRY": VmInstructionInfo(opcode="53", hasarg=True, argsize=2, maxarg=4096),
    "LDRX": VmInstructionInfo(opcode="54", hasarg=True, argsize=2, maxarg=4096),
    "LDRY": VmInstructionInfo(opcode="55", hasarg=True, argsize=2, maxarg=4096),
    "OUT": VmInstructionInfo(opcode="60", hasarg=False, argsize=0, maxarg=4096),
    "IN": VmInstructionInfo(opcode="61", hasarg=False, argsize=0),
    "CMPX": VmInstructionInfo(opcode="70", hasarg=True, argsize=1),
    "CMPY": VmInstructionInfo(opcode="71", hasarg=True, argsize=1),
    "JE": VmInstructionInfo(opcode="72", hasarg=True, argsize=2),
    "JRE": VmInstructionInfo(opcode="73", hasarg=True, argsize=2, maxarg=4096),
    "JL": VmInstructionInfo(opcode="74", hasarg=True, argsize=2, maxarg=4096),
    "JRL": VmInstructionInfo(opcode="75", hasarg=True, argsize=2, maxarg=4096),
    "JLE": VmInstructionInfo(opcode="76", hasarg=True, argsize=2, maxarg=4096),
    "JRLE": VmInstructionInfo(opcode="77", hasarg=True, argsize=2, maxarg=4096),
    "JG": VmInstructionInfo(opcode="78", hasarg=True, argsize=2, maxarg=4096),
    "JRG": VmInstructionInfo(opcode="79", hasarg=True, argsize=2, maxarg=4096),
    "JGE": VmInstructionInfo(opcode="80", hasarg=True, argsize=2, maxarg=4096),
    "JRGE": VmInstructionInfo(opcode="81", hasarg=True, argsize=2, maxarg=4096),
    "ADDX": VmInstructionInfo(opcode="A0", hasarg=True, argsize=1),
    "ADDXY": VmInstructionInfo(opcode="A1", hasarg=False, argsize=0),
    "DECX": VmInstructionInfo(opcode="A2", hasarg=True, argsize=1),
    "DECXY": VmInstructionInfo(opcode="A3", hasarg=False, argsize=0),
    "RORX": VmInstructionInfo(opcode="A4", hasarg=False, argsize=0),
    "ROLX": VmInstructionInfo(opcode="A5", hasarg=False, argsize=0),
    "XORX": VmInstructionInfo(opcode="A6", hasarg=False, argsize=0),
    "PUSHX": VmInstructionInfo(opcode="B0", hasarg=False, argsize=0),
    "POPX": VmInstructionInfo(opcode="B1", hasarg=False, argsize=0),
    "PUSHY": VmInstructionInfo(opcode="B2", hasarg=False, argsize=0),
    "POPY": VmInstructionInfo(opcode="B3", hasarg=False, argsize=0),
    "RMEMX": VmInstructionInfo(opcode="C0", hasarg=False, argsize=0),
    "WMEMX": VmInstructionInfo(opcode="C1", hasarg=False, argsize=0),
    "RMEMY": VmInstructionInfo(opcode="C2", hasarg=False, argsize=0),
    "WMEMY": VmInstructionInfo(opcode="C3", hasarg=False, argsize=0),
    "NOP": VmInstructionInfo(opcode="90", hasarg=False, argsize=0),
    "RET": VmInstructionInfo(opcode="91", hasarg=False, argsize=0)
}


class VmInstructionNode:
    def __init__(self, instruction: VmInstructionInfo, argument: str|None, offset: int, lineno: int) -> None:
        self.instruction =instruction
        self.argument = argument
        self.offset = offset
        self.lineno = lineno


class VmValueInfo(VmInstructionInfo):
    def __init__(self, value: str) -> None:
        super().__init__("", False, len(value), 0)
        self.value = value


class AsmComponent:
    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code
        self.lines = self.code.split("\n")

    def throw_error(self, line: int, segment: int|None, error: str):
        print(f"{self.name} ERROR: {error}")
        lines = self.code.split('\n')
        if line < 0 or line > len(lines) - 1:
            exit(-4)
        target_line: str = lines[line]
        segments = target_line.split(' ')
        target_segment: str = segments[segment] if segment != None else target_line
        
        segment_offset = 0
        if segment != None:
            for i in range(segment):
                segment_offset += len(segments[i]) + 1

        print(f"{line + 1}\t{target_line}")
        print(' ' * len(str(line)) + '\t' + ' ' * segment_offset + '~' * len(target_segment))
        exit(-3)


class Compiler(AsmComponent):
    def __init__(self, code: str) -> None:
        self.symbols = {}
        self.labels = {}
        self.strings = {}
        self.result = []
        self.code_written = False
        self.byte_offset = 0
        self.section = None
        super().__init__("COMPILER", code)
        self.setup()

    def setup(self):
        cld = VmInstructionNode(VM_INSTRUCTIONS["CMPX"], "0", self.byte_offset, 0)
        self.result.append(cld)
        self.byte_offset += 2
        inst = VmInstructionNode(VM_INSTRUCTIONS["JE"], "_main", self.byte_offset, 0)
        self.result.append(inst)
        self.byte_offset += inst.instruction.argsize + 1


    def add_symbol(self, key: str, value: str):
        self.symbols.__setitem__(key, value)

    def get_symbol(self, key: str):
        return self.symbols[key]

    def add_label(self, label: str, address: int):
        self.labels.__setitem__(label, address)

    def get_label(self, label: str):
        return self.labels[label]

    def compile_line(self, index: int, segments: list[str]):
        line = self.lines[index]
        if len(line.replace(" ", "").replace("\t", "")) == 0:
            return
        opcode = segments[0]
        starting_sym = opcode[0]
        
        match (starting_sym):
            case '.':
                self.process_macro(index, opcode, segments[1:])

            case '#':
                return

            case _:
                self.process_instruction(index, opcode, segments[1:])

    def process_macro(self, index: int, macro: str, segments: list[str]):
        match (macro.replace('.', '').upper()):
            case 'SET':
                if len(segments) != 2:
                    self.throw_error(index, None, "Expected 2 arguments for macro SET")
                if segments[0] in self.labels or segments[0] in self.symbols:
                    self.throw_error(index, 1, "Symbol already exists")
                self.add_symbol(*segments)

            case 'LABEL':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected 1 argument for macro LABEL")
                if segments[0] in self.symbols or segments[0] in self.labels:
                    self.throw_error(index, 1, "Symbol already exists")
                self.add_label(segments[0], self.byte_offset)

            case 'ASCII':
                if self.section != "DATA":
                    self.throw_error(index, None, "ASCII String outside of DATA section")
                if len(segments) == 0:
                    self.throw_error(index, None, "Expected ASCII sequence")
                ascii_sequence = ' '.join(segments)
                ascii_string = ""
                if ascii_sequence[0] != '"':
                    self.throw_error(index, 1, "Expected quotes")
                ascii_index = 1
                while ascii_index < len(ascii_sequence) and ascii_sequence[ascii_index] != '"':
                    ascii_string += ascii_sequence[ascii_index]
                    ascii_index += 1
                if len(ascii_string) < len(ascii_sequence) - 2:
                    self.throw_error(index, None, "Invalid syntax")
                hex_string = ""
                for i, c in enumerate(ascii_string):
                    char = hex(ord(c)).replace("0x", "").upper()
                    while len(char) % 2 != 0:
                        char = "0" + char
                    hex_string += str(char)
                hex_string += "00"
                self.result.append(VmInstructionNode(VmValueInfo(hex_string), hex_string, self.byte_offset, index))
                self.strings.__setitem__(self.byte_offset, hex_string)
                self.byte_offset += len(ascii_string) + 1

            case 'SECTION':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected section")
                
                match (segments[0].upper()):
                    case 'DATA':
                        self.section = "DATA"
                        if self.section == "TEXT":
                            self.result.append(VmInstructionNode(VM_INSTRUCTIONS["RET"], "", self.byte_offset, index))
                            self.byte_offset += 1

                    case 'TEXT':
                        self.section = "TEXT"

                    case _:
                        self.throw_error(index, 1, "Unknown section")

            case 'ALLOC':
                if self.section != "DATA":
                    self.throw_error(index, None, "Cannot allocate buffer outside of DATA section")
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected buffer size")
                if segments[0] in self.symbols:
                    segments[0] = self.get_symbol(segments[0])
                if not segments[0].isdecimal():
                    self.throw_error(index, 1, "Expected buffer size or macro symbol")
                segments[0] = int(segments[0])
                val = VmValueInfo("00" * segments[0])
                self.result.append(VmInstructionNode(val, val.value, self.byte_offset, index))
                self.byte_offset += segments[0]

            case 'PUSHSTR':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected address or label")

                if segments[0] in self.labels:
                    segments[0] = self.get_label(segments[0])
                
                changed, int_val, str_val = to_linked_repr(segments[0])
                if not changed and not isinstance(segments[0], int):
                    self.throw_error(index, 1, "Invalid syntax")

                address = int_val
                if address not in self.strings:
                    self.throw_error(index, 1, f"No string at location {hex(address).upper()}")
                string = self.strings[address]
                
                base_ldx = VmInstructionNode(VM_INSTRUCTIONS["LDX"], "0", self.byte_offset, index)
                self.byte_offset += base_ldx.instruction.argsize + 1
                base_pushx = VmInstructionNode(VM_INSTRUCTIONS["PUSHX"], "", self.byte_offset, index)
                self.byte_offset += 1
                self.result.append(base_ldx)
                self.result.append(base_pushx)

                for byte in (string[i:i+2] for i in range(0, len(string), 2)):
                    ldx = VmInstructionNode(VM_INSTRUCTIONS["LDX"], str(int(byte, 16)), self.byte_offset, index)
                    self.byte_offset += ldx.instruction.argsize + 1
                    pushx = VmInstructionNode(VM_INSTRUCTIONS["PUSHX"], "", self.byte_offset, index)
                    self.byte_offset += 1
                    self.result.append(ldx)
                    self.result.append(pushx)

            case 'STRREGS':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected address or label")
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["STRX"], segments[0], self.byte_offset, index))
                self.byte_offset += 3
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["STRY"], f"{segments[0]}+1", self.byte_offset, index))
                self.byte_offset += 3

            case 'LDREGS':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected address or label")
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["LDRX"], segments[0], self.byte_offset, index))
                self.byte_offset += 3
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["LDRY"], f"{segments[0]}+1", self.byte_offset, index))
                self.byte_offset += 3

            case 'LD16':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected value or symbol")
                if '+' in segments[0]:
                    self.throw_error(index, 1, "LD16 macro does not support address offsets")
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["LDX"], f"{segments[0]}|1", self.byte_offset, index))
                self.byte_offset += 2
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["LDY"], f"{segments[0]}|0", self.byte_offset, index))
                self.byte_offset += 2

            case 'PUSHREGS':
                if len(segments) != 0:
                    self.throw_error(index, None, "No argument expected")
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["PUSHY"], "", self.byte_offset, index))
                self.byte_offset += 1 
                self.result.append(VmInstructionNode(VM_INSTRUCTIONS["PUSHX"], "", self.byte_offset, index))
                self.byte_offset += 1

            case 'ADD16':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected operand")
                self.process_macro(index, "STRREGS", ["_swap"])
                # self.process_instruction(index, "LDX", ["0"])
                # self.process_instruction(index, "LDY", ["0"])
                self.process_instruction(index, "POPX", [])
                self.process_instruction(index, "CMPX", ["0"])
                self.process_instruction(index, "ADDX", [segments[0]])
                self.process_instruction(index, "JRE", ["29"])
                self.process_instruction(index, "CMPX", [segments[0]])
                self.process_instruction(index, "JRLE", ["6"])
                # skip first overflow step if not necessary
                self.process_instruction(index, "JRG", ["21"])
                # first overflow step
                self.process_instruction(index, "POPY", []) # get Y
                self.process_instruction(index, "PUSHX", []) # save X
                self.process_instruction(index, "LDX", ["0"]) # reset X
                self.process_instruction(index, "ADDXY", []) # mov Y to X
                self.process_instruction(index, "ADDX", ["1"]) # add 1 to X
                self.process_instruction(index, "CMPX", ["0"]) # check if x has overflowed
                # set Y = X
                self.process_instruction(index, "PUSHX", [])
                self.process_instruction(index, "POPY", [])
                self.process_instruction(index, "POPX", [])
                # Skip overflow step if not necessary
                self.process_instruction(index, "JRG", ["5"])
                # overflow step
                self.process_instruction(index, "LDX", ["0"])
                # restore registers
                self.process_instruction(index, "PUSHY", [])
                self.process_instruction(index, "PUSHX", [])
                self.process_macro(index, "LDREGS", ["_swap"])

            case 'JUMP':
                if len(segments) != 1:
                    self.throw_error(index, None, "Expected address or label")
                self.process_instruction(index, "PUSHX", [])
                self.process_instruction(index, "LDX", ["0"])
                self.process_instruction(index, "CMPX", ["0"])
                self.process_instruction(index, "POPX", [])
                self.process_instruction(index, "JE", [segments[0]])

            case 'ZERO':
                if len(segments) != 0:
                    self.throw_error(index, None, "Expected no arguments")
                self.process_instruction(index, "LDX", ["0"])
                self.process_instruction(index, "LDY", ["0"])

            case 'POPREGS':
                if len(segments) != 0:
                    self.throw_error(index, None, "Expected no arguments")
                self.process_instruction(index, "POPX", [])
                self.process_instruction(index, "POPY", [])

            case 'RMREGS':
                if len(segments) != 0:
                    self.throw_error(index, None, "Expected no arguments")
                self.process_macro(index, "STRREGS", ["_swap"])
                self.process_macro(index, "POPREGS", [])
                self.process_macro(index, "LDREGS", ["_swap"])

            case 'FETCHREGS':
                self.process_macro(index, "POPREGS", [])
                self.process_macro(index, "PUSHREGS", [])

            case _:
                self.throw_error(index, None, f"Unknown macro '{macro}'")

    def process_instruction(self, index: int, opcode: str, segments: list[str]):
        if self.section != "TEXT":
            self.throw_error(index, None, "Unexpected code outside of TEXT section")
        line: str = self.lines[index]
        if opcode.upper() not in VM_INSTRUCTIONS:
            self.throw_error(index, 0, "Unrecognized Instruction")
        instruction_info: VmInstructionInfo = VM_INSTRUCTIONS[opcode.upper()]
        if instruction_info.hasarg and len(segments) == 0:
            self.throw_error(index, None, "Expected instruction operand")
        elif not instruction_info.hasarg and len(segments) != 0:
            self.throw_error(index, None, "Unexpected instruction operand(s)")
        if len(segments) > 1:
            self.throw_error(index, 2, "VM Architecture only supports single-operand instructions")
        inst_node = VmInstructionNode(instruction_info, segments[0] if len(segments) != 0 else "", self.byte_offset, index)
        self.result.append(inst_node)
        self.byte_offset += 1 + instruction_info.argsize
        self.code_written = True


class Linker(AsmComponent):
    def __init__(self, code: str) -> None:
        super().__init__("LINKER", code)


def compile(code: str):
    print('Compiling...')
    res = Compiler(code)

    code_lines: list[str] = code.split('\n')
    for index, line in enumerate(code_lines):
        line_segments: list[str] = line.split('#')[0].split(' ')
        line_segments = [i for i in line_segments if i != '']
        if len(line_segments) == 0:
            continue  
        res.compile_line(index, line_segments)
    return res


def link(compiler: Compiler):
    print('Linking...')
    linker = Linker(compiler.code)
    if "_main" not in compiler.labels:
        linker.throw_error(-1, None, "_main label not found")
    if "_swap" not in compiler.labels:
        linker.throw_error(-1, None, "_swap label not found")
    res = []
    for node in compiler.result:
        node: VmInstructionNode
        inst_info = node.instruction
        max_size: int = inst_info.maxarg
        if not inst_info.hasarg:
            res.append(node)
            continue

        global changed, int_val, str_val
        values = node.argument.split("+")
        final_int = 0

        while len(values) >= 1:
            changed, int_val, str_val = to_linked_repr(values[0].split("|")[0])
            if not changed:
                if values[0].split("|")[0] in compiler.symbols:
                    changed, int_val, str_val = to_linked_repr(compiler.get_symbol(values[0].split("|")[0]))
                elif values[0].split("|")[0] in compiler.labels:
                    changed = True
                    int_val = compiler.get_label(values[0].split("|")[0])
                    str_val = hex(int_val).replace("0x", "").upper()
                else:
                    linker.throw_error(node.lineno, 1, "Undefined symbol")

            if "|" in values[0]:
                v = values[0].split("|")
                if len(v) != 2:
                    linker.throw_error(node.lineno, None, "Invalid byte-indexing syntax")
                if not v[1].isdecimal():
                     linker.throw_error(node.lineno, None, "Byte-index expected after |")
                int_val = int_val.to_bytes(length=2, byteorder='big', signed=False)[int(v[1])]

            if int_val >= max_size:
                linker.throw_error(node.lineno, 1, f"Value exceeds maximum of {max_size}")

            final_int += int_val
            values.pop(0)
        
        final_int = final_int if final_int != 0 else int_val
        changed, int_val, str_val = to_linked_repr(final_int, True)
        while len(str_val) < 2 * inst_info.argsize:
            str_val = "0" + str_val
        linked_node = VmInstructionNode(node.instruction, str_val, node.offset, node.lineno)
        res.append(linked_node)
    
    print(f'Linked bytecode size: {compiler.byte_offset} byte(s)')
    print("Linked labels:")
    for label, address in compiler.labels.items():
        print(f"  - {label}: {hex(address)}")
    print("Linked symbols:")
    for sym, value in compiler.symbols.items():
        print(f"  - {sym}: {value}")
    return res


def linked_code_to_hex_string(linked_code_seq: list[VmInstructionNode]):
    res = ""
    for node in linked_code_seq:
        res += node.instruction.opcode + node.argument
    return res


def save(linked_code_repr: str):
    with open("vm_asm_out.txt", "w") as outfile:
        outfile.write(linked_code_repr)


def main(filepath: str):
    try:
        with open(filepath, "r") as file:
            save(linked_code_to_hex_string(link(compile(file.read()))))
            return 0
    except Exception as e:
        raise e


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Expected 1 argument")
        exit(-1)

    exit(main(sys.argv[1]))
