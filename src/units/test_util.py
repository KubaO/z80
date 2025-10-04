import operator as op
import unittest

from src.z80 import registers, util


def oddparity(n: int) -> bool:
    if n.bit_count() % 2:
        return False
    else:
        return True


def signext8(n: int) -> int:
    if n & 0x80:
        return 0xFF00 | (n & 0xFF)
    else:
        return n & 0xFF


class TestZ80Util(unittest.TestCase):
    def setUp(self):
        self.regs = registers.Registers(power=None)

    def check8_SZ(self, val):
        flags = self.regs.flags
        self.assertEqual(flags.Z, val == 0)
        self.assertEqual(flags.S, bool(val & 0x80))

    def check8_SZP(self, val):
        flags = self.regs.flags
        self.assertEqual(flags.Z, val == 0)
        self.assertEqual(flags.S, bool(val & 0x80))
        self.assertEqual(flags.P, oddparity(val))

    def check16_SZ(self, val):
        flags = self.regs.flags
        self.assertEqual(flags.Z, val == 0)
        self.assertEqual(flags.S, bool(val & 0x8000))

    def test_get_16bit_twos_comp(self):
        for i in range(0x8000):
            self.assertEqual(i, util.get_16bit_twos_comp(i))
        for i in range(1, 0x8001):
            self.assertEqual(-i, util.get_16bit_twos_comp(0x10000 - i))

    def test_get_8bit_twos_comp(self):
        for i in range(0x80):
            self.assertEqual(i, util.get_8bit_twos_comp(i))
        for i in range(1, 0x81):
            self.assertEqual(-i, util.get_8bit_twos_comp(0x100 - i))

    def test_make_8bit_twos_comp(self):
        for i in range(0x80):
            self.assertEqual(i, util.make_8bit_twos_comp(i))
        for i in range(1, 0x81):
            self.assertEqual(0x100 - i, util.make_8bit_twos_comp(-i))

    def test_subtract8(self):
        flags = self.regs.flags
        for i in range(0x100):
            for j in range(0x100):
                res = (i - j) & 0xFF
                self.assertEqual(res, util.subtract8(i, j, self.regs, C=True))
                self.check8_SZ(res)
                self.assertTrue(flags.N)
                self.assertEqual(bool((i - j) & 0x100), bool(flags.C))

    def test_add8(self):
        flags = self.regs.flags
        for i in range(0x100):
            for j in range(0x100):
                res = (i + j) & 0xFF
                self.assertEqual(res, util.add8(i, j, self.regs, C=True))
                self.check8_SZ(res)
                self.assertFalse(flags.N)
                self.assertEqual(bool((i + j) & 0x100), bool(flags.C))

    def test_subtract16(self):
        regs = self.regs
        flags = regs.flags
        for i in range(0, 0x10000, 63):
            for j in range(0, 0x10000, 71):
                res = (i - j) & 0xFFFF
                self.assertEqual(res, util.subtract16(i, j, regs))
                self.check16_SZ(res)
                self.assertTrue(flags.N)
                self.assertEqual(bool((i - j) & 0x10000), bool(flags.C))

    def test_inc16(self):
        res = 0
        for i in range(0x10000):
            self.assertEqual(i, res)
            res = util.inc16(res)
        self.assertEqual(res, 0)

    def test_dec16(self):
        res = 0xFFFF
        for i in range(0xFFFF, -1, -1):
            self.assertEqual(i, res)
            res = util.dec16(res)
        self.assertEqual(res, 0xFFFF)

    def test_inc8(self):
        res = 0
        for i in range(0x100):
            self.assertEqual(i, res)
            res = util.inc8(res)
        self.assertEqual(res, 0)

    def test_dec8(self):
        res = 0xFF
        for i in range(0xFF, -1, -1):
            self.assertEqual(i, res)
            res = util.dec8(res)
        self.assertEqual(res, 0xFF)

    def test_parity8(self):
        for i in (0x00, 0x03, 0x0F, 0x3F, 0xFF):
            self.assertEqual(True, util.parity8(i))
        for i in (0x01, 0x07, 0x1F, 0x7F):
            self.assertEqual(False, util.parity8(i))
        for i in range(0x100):
            self.assertEqual(oddparity(i), util.parity8(i))

    def check_logic(self, testfn, expfn, /, H):
        regs = self.regs
        flags = regs.flags
        for a in range(0x100):
            for n in range(0x100):
                regs.A = a
                regs.F = 0
                exp = expfn(a, n)
                testfn(regs, n)
                self.assertEqual(regs.A, exp)
                self.assertFalse(flags.N)
                self.assertFalse(flags.C)
                self.check8_SZP(exp)
                self.assertEqual(flags.H, H)

    def test_a_and_n(self):
        self.check_logic(util.a_and_n, op.__and__, H=True)

    def test_a_or_n(self):
        self.check_logic(util.a_or_n, op.__or__, H=False)

    def test_a_xor_n(self):
        self.check_logic(util.a_xor_n, op.__xor__, H=False)

    def check_shift(self, testfn, expfn):
        regs = self.regs
        flags = regs.flags
        for a in range(0x200):
            c = int(bool(a & 0x100))
            a &= 0xFF
            regs.F = 0
            regs.A = a
            regs.flags.C = c
            expa, expc = expfn(a, c)
            res = testfn(regs, a)
            self.assertEqual(res, expa)
            self.assertEqual(bool(flags.C), bool(expc))
            self.check8_SZP(expa)

    def test_rlc(self):
        def expfn(a, c):
            expc = ((a >> 7) & 1)
            expa = ((a << 1) & 0xFF) | expc
            return expa, expc

        self.check_shift(util.rotate_left_carry, expfn)

    def test_rl(self):
        def expfn(a, c):
            expc = (a & 0x80) >> 7
            expa = ((a << 1) & 0xFF) | c
            return expa, expc

        self.check_shift(util.rotate_left, expfn)

    def test_rrc(self):
        def expfn(a, c):
            expc = a & 1
            expa = ((a >> 1) & 0xFF) | (expc << 7)
            return expa, expc

        self.check_shift(util.rotate_right_carry, expfn)

    def test_rr(self):
        def expfn(a, c):
            expc = a & 1
            expa = ((a >> 1) & 0xFF) | (c << 7)
            return expa, expc

        self.check_shift(util.rotate_right, expfn)

    def test_sl(self):
        def expfn(a, c):
            expc = (a & 0x80) >> 7
            expa = (a << 1) & 0xFF
            return expa, expc

        self.check_shift(util.shift_left, expfn)

    def test_sll(self):
        def expfn(a, c):
            expc = (a & 0x80) >> 7
            expa = (a << 1) & 0xFF | 0x01
            return expa, expc

        self.check_shift(util.shift_left_logical, expfn)

    def test_sr(self):
        def expfn(a, c):
            expc = a & 1
            expa = ((a >> 1) & 0xFF) | (a & 0x80)
            return expa, expc

        self.check_shift(util.shift_right, expfn)

    def test_srl(self):
        def expfn(a, c):
            expc = a & 1
            expa = ((a >> 1) & 0xFF)
            return expa, expc

        self.check_shift(util.shift_right_logical, expfn)

    def test_offset_pc(self):
        regs = self.regs
        for i in range(0x100):
            for j in range(0, 0x10000, 5):
                regs.PC = j
                util.offset_pc(regs, i)
                exp = (j + signext8(i)) & 0xFFFF
                self.assertEqual(regs.PC, exp)

    def test_set_f5_f3(self):
        flags = self.regs.flags
        for i in range(0x100):
            util.set_f5_f3(self.regs, i)
            self.assertEqual(flags.F3, bool(i & (1 << 3)))
            self.assertEqual(flags.F5, bool(i & (1 << 5)))

    def test_set_f5_f3_from_a(self):
        flags = self.regs.flags
        for i in range(0x100):
            self.regs.A = i
            util.set_f5_f3_from_a(self.regs)
            self.assertEqual(flags.F3, bool(i & (1 << 3)))
            self.assertEqual(flags.F5, bool(i & (1 << 5)))


if __name__ == '__main__':
    unittest.main()
