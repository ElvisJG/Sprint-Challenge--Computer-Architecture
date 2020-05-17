import sys

# Operations #
math = {"ADD": 0b10100000, "SUB": 0b10100001,
        "MUL": 0b10100010, 'CMP': 0b10100111}

binary = {0b00000001: 'HLT', 0b10000010: 'LDI', 0b01000111: 'PRN', 0b01000101: 'PUSH', 0b01000110: 'POP',
          0b01010000: 'CALL', 0b00010001: 'RET', 0b01010100: 'JMP', 0b01010101: 'JEQ', 0b01010110: 'JNE'}

pointer = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        # Constructing a new CPU, Registers, and flag #
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[pointer] = 0xF4
        self.operand_a = None
        self.operand_b = None
        self.ProgramCounter = 0
        self.MemoryAddress = None
        self.MemoryData = None
        self.FL = 0b00000000

        # Branches #
        self.instructions = {'HLT': self.HALT, 'LDI': self.LOAD, 'PRN': self.PRINT, 'PUSH': self.PUSH, 'POP': self.POP,
                             'CALL': self.CALL, 'RET': self.RET, 'JMP': self.JMP, 'JEQ': self.JEQ, 'JNE': self.JNE}

    def CALL(self):
        self.reg[pointer] -= 1
        instruction_address = self.ProgramCounter + 2
        self.ram[self.reg[pointer]] = instruction_address
        register = self.operand_a
        self.ProgramCounter = self.reg[register]

    def RET(self):
        self.ProgramCounter = self.ram[self.reg[pointer]]
        self.reg[pointer] += 1

    def JMP(self):
        address = self.reg[self.operand_a]
        print("WARP SPEED")
        self.ProgramCounter = address

    def JEQ(self):
        address = self.reg[self.operand_a]
        if self.FL & 0b00000001 == 1:
            self.ProgramCounter = address
        else:
            self.ProgramCounter += 2

    def JNE(self):
        address = self.reg[self.operand_a]
        if self.FL & 0b00000001 == 0:
            self.ProgramCounter = address
        else:
            self.ProgramCounter += 2

    def HALT(self):
        sys.exit()

    def LOAD(self):
        self.reg[self.operand_a] = self.operand_b

    def PRINT(self):
        print(self.reg[self.operand_a])

    def PUSH(self):
        global pointer
        self.reg[pointer] -= 1
        value = self.reg[self.operand_a]
        self.ram[self.reg[pointer]] = value

    def POP(self):
        global pointer
        value = self.ram[self.reg[pointer]]
        register = self.operand_a
        self.reg[register] = value
        self.reg[pointer] += 1

    def read(self, address):
        self.MemoryAddress = address
        self.MemoryData = self.ram[address]
        return self.ram[address]

    def write(self, value, address):
        self.MemoryAddress = address
        self.MemoryData = value
        self.ram[address] = value

    def load(self):

        if len(sys.argv) != 2:
            print("ERROR: Must have file name")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            address = 0
            with open(filename) as program:
                for instruction in program:
                    comment_split = instruction.strip().split("#")
                    value = comment_split[0].strip()
                    if value == "":
                        continue
                    num = int(value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def ALU(self, op, reg_a, reg_b):
        if op == math["ADD"]:
            print("ADDING")
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math["SUB"]:
            print("SUBTRACTING")
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math["MUL"]:
            print("MULTIPYING")
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == math["CMP"]:
            valueA = self.reg[self.operand_a]
            valueB = self.reg[self.operand_b]

            if valueA == valueB:
                self.FL = 0b00000001

            if valueA < valueB:
                self.FL = 0b00000100

            if valueA > valueB:
                self.FL = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.ProgramCounter,
            self.read(self.ProgramCounter),
            self.read(self.ProgramCounter + 1),
            self.read(self.ProgramCounter + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def move_pc(self, ir):
        if (ir << 3) % 255 >> 7 != 1:
            self.ProgramCounter += (ir >> 6) + 1

    def run(self):
        while True:
            IR = self.read(self.ProgramCounter)
            self.operand_a = self.read(self.ProgramCounter + 1)
            self.operand_b = self.read(self.ProgramCounter + 2)
            if (IR << 2) % 255 >> 7 == 1:
                self.ALU(IR, self.operand_a, self.operand_b)
                self.move_pc(IR)
            elif (IR << 2) % 255 >> 7 == 0:
                self.instructions[binary[IR]]()
                self.move_pc(IR)
            else:
                print(f"Did not understand command: {IR}")
                print(self.trace())
                sys.exit(1)
