from warnings import deprecated

from src.z80.registers import Registers

REGISTER_BITS = {'A': 7, 'B': 0, 'C': 1, 'D': 2, 'E': 3, 'H': 4, 'L': 5}
INDEX_BYTES = [(0xDD, 'IX'), (0xfd, 'IY')]
#              i, name, bit, val
CONDITIONS = [(0 << 3, 'NZ', 'Z', 0),
              (1 << 3, 'Z', 'Z', 1),
              (2 << 3, 'NC', 'C', 0),
              (3 << 3, 'C', 'C', 1),
              (4 << 3, 'PO', 'PV', 0),
              (5 << 3, 'PE', 'PV', 1),
              (6 << 3, 'P', 'S', 0),
              (7 << 3, 'M', 'S', 1), ]

register_bits = REGISTER_BITS
index_bytes = INDEX_BYTES
conditions = CONDITIONS

_DEBUG_OUTPUT = False


def get_16bit_twos_comp(val: int):
    """ Return the value of a 16bit 2s comp number"""
    assert 0 <= val <= 0xFFFF
    if val & 0x8000:
        return -0x10000 + val
    else:
        return val


def get_8bit_twos_comp(val: int):
    """ Return the value of an 8bit 2s comp number"""
    assert 0 <= val <= 0xFF
    if val & 0x80:
        return -0x100 + val
    else:
        return val


def make_8bit_twos_comp(val: int):
    assert -128 <= val <= 0xFF
    return val & 0xFF


def subtract8(a: int, b: int, registers: Registers, S=True, N=True, Z=True,
              F3=True, F5=True, H=True, V=False, C=False):
    """ subtract b from a,  return result and set flags """
    assert 0 <= a <= 0xFF
    assert 0 <= b <= 0xFF
    res = a - b
    condition = registers.condition
    if S:
        condition.S = res & 0x80
    if N:
        condition.N = 1
    if Z:
        condition.notZ = res & 0xFF
    if F3:
        condition.F3 = res & 0x08
    if F5:
        condition.F5 = res & 0x20
    if H:
        registers.condition.H = (b & 0xF) > (a & 0xF)
    if V:
        a = get_8bit_twos_comp(a)
        b = get_8bit_twos_comp(b)
        condition.V = (a - b) < -127 or (a - b) > 128
    if C:
        condition.C = res & 0x100
    return res & 0xFF


def subtract8_check_overflow(a, b, registers):
    return subtract8(a, b, registers, V=True, C=True)


def add8(a: int, b: int, registers: Registers, S=True, Z=True, H=True,
         V=True, N=True, C=True, F3=True, F5=True):
    """ add a and b,  return result and set flags """
    assert 0 <= a <= 0xFF
    assert 0 <= b <= 0xFF
    res = a + b
    condition = registers.condition
    if S:
        condition.S = res & 0x80
    if Z:
        condition.notZ = res & 0xFF
    if H:
        condition.H = ((a & 0xF) + (b & 0xF)) > 0xF
    if V:
        condition.V = ((a & 0x80) == (b & 0x80)) and ((a & 0x80) != (res & 0x80))
    if N:
        condition.N = 0
    if C:
        condition.C = res & 0x100
    if F3:
        condition.F3 = res & 0x08
    if F5:
        condition.F5 = res & 0x20
    return res & 0xFF


def add16(a: int, b: int, registers: Registers):
    """ add a and b,  return result and set flags """
    assert 0 <= a <= 0xFFFF
    assert 0 <= b <= 0xFFFF
    res = a + b
    condition = registers.condition  # improves things on older Python 3 versions
    if _DEBUG_OUTPUT:
        print(a, "+", b, "=", res)
    condition.S = res & 0x8000
    condition.notZ = res & 0xFFFF
    condition.H = ((a & 0xFFF) + (b & 0xFFF)) > 0xFFF
    condition.V = ((a & 0x8000) == (b & 0x8000)) and ((a & 0x8000) != (res & 0x8000))
    condition.N = 0
    condition.C = res & 0x10000
    condition.F3 = res & 0x0800
    condition.F5 = res & 0x2000
    return res & 0xFFFF


def subtract16(a: int, b: int, registers: Registers):
    """ subtract b from a,  return result and set flags """
    assert 0 <= a <= 0xFFFF
    assert 0 <= b <= 0xFFFF
    res = a - b
    if _DEBUG_OUTPUT:
        print(a, "-", b, "=", res, "(", hex(res), ")")
    condition = registers.condition
    condition.S = res & 0x8000
    condition.N = 1
    condition.notZ = res & 0xFFFF
    condition.F3 = res & 0x0800
    condition.F5 = res & 0x2000
    condition.H = (b & 0xFFF) > (a & 0xFFF)
    condition.V = (a & 0x8000) != (res & 0x8000)
    condition.C = res & 0x10000
    return res & 0xFFFF


def inc16(val: int):
    assert 0 <= val <= 0xFFFF
    return (val + 1) & 0xFFFF


def dec16(val: int):
    assert 0 <= val <= 0xFFFF
    return (val - 1) & 0xFFFF


def inc8(val: int):
    assert 0 <= val <= 0xFF
    return (val + 1) & 0xFF


def dec8(val: int):
    assert 0 <= val <= 0xFF
    return (val - 1) & 0xFF


def parity8(n: int):
    assert 0 <= n <= 0xFF
    return not (n.bit_count() & 1)


@deprecated("Use parity8 instead")
def parity(n):
    return parity8(n)


def a_and_n(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = registers.A & n
    registers.A = v
    condition = registers.condition
    condition.H = 1
    condition.NC = 0
    condition.P = parity8(v)
    condition.notZ = v
    condition.S = v & 0x80
    set_f5_f3_from_a(registers)


def a_or_n(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = registers.A | n
    registers.A = v
    condition = registers.condition
    condition.HNC = 0
    condition.P = parity8(v)
    condition.notZ = v
    condition.S = v & 0x80
    set_f5_f3_from_a(registers)


def a_xor_n(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = registers.A ^ n
    registers.A = v
    condition = registers.condition
    condition.HNC = 0
    condition.P = parity8(v)
    condition.notZ = v
    condition.S = v & 0x80
    set_f5_f3_from_a(registers)


def rotate_left_carry(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    c = n >> 7
    v = (n << 1 | c) & 0xFF
    condition = registers.condition
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = c
    return v


def rotate_left(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    condition = registers.condition
    v = (n << 1 | condition.C) & 0xFF
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = n & 0x80
    return v


def rotate_right_carry(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    c = n & 0x01
    v = n >> 1 | (c << 7)
    condition = registers.condition
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = c
    return v


def rotate_right(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    condition = registers.condition
    v = n >> 1 | (condition.C << 7)
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = n & 0x01
    return v


def shift_left(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = (n << 1) & 0xFF
    condition = registers.condition
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = n & 0x80
    return v


def shift_left_logical(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = ((n << 1) & 0xFF) | 0x01
    condition = registers.condition
    condition.S = v >> 7
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = n & 0x80
    return v


def shift_right(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = n >> 1 | n & 0x80
    condition = registers.condition
    condition.S = v & 0x80
    condition.notZ = v
    condition.HN = 0
    condition.P = parity8(v)
    condition.C = n & 0x01
    return v


def shift_right_logical(registers: Registers, n: int):
    assert 0 <= n <= 0xFF
    v = n >> 1
    condition = registers.condition
    condition.SHN = 0
    condition.notZ = v
    condition.P = parity8(v)
    condition.C = n & 0x01
    return v


def offset_pc(registers: Registers, jump: int):
    assert 0 <= jump <= 0xFF
    registers.PC = (registers.PC + get_8bit_twos_comp(jump)) & 0xFFFF


def set_f5_f3(registers: Registers, v: int):
    assert 0 <= v <= 0xFF
    registers.condition.F5 = v & 0x20
    registers.condition.F3 = v & 0x08


def set_f5_f3_from_a(registers: Registers):
    set_f5_f3(registers, registers.A)
