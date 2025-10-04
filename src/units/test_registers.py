import unittest
from typing import Iterable

from src.z80 import registers

FLAGS = [f if isinstance(f, list) else [f] for f in
         ("S", "Z", "F5", "H", "F3", ["PV", "P", "V"], "N", "C")]
PAIRS = ("AF", "BC", "DE", "HL")


def flatten(items):
    """Yield items from any nested iterable; see https://stackoverflow.com/a/40857703/1329652."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x


class TestZ80Registers(unittest.TestCase):

    def setUp(self):
        self.registers = registers.Registers(power=None)

    def test_register_power(self):
        # not sure what it's for yet, but it should exist
        self.assertTrue(hasattr(self.registers, "power"))

    def test_register_pair_writes(self):
        for pair in PAIRS:
            h = pair[0]
            l = pair[1]
            for i in range(0x10000):
                setattr(self.registers, pair, i)
                self.assertEqual(getattr(self.registers, h), i >> 8)
                self.assertEqual(getattr(self.registers, l), i & 0xFF)

    def test_register_pair_reads(self):
        for pair in PAIRS:
            h = pair[0]
            l = pair[1]
            for i in range(0x10000):
                setattr(self.registers, h, i >> 8)
                setattr(self.registers, l, i & 0xFF)
                self.assertEqual(getattr(self.registers, pair), i)

    def test_condition_set(self):
        for i, reg in enumerate(FLAGS):
            for r in reg:
                self.registers.F = 0x0
                setattr(self.registers.condition, r, True)
                self.assertEqual(self.registers.F, 0x01 << (7 - i))

            for reg2 in flatten(FLAGS):
                if reg2 not in reg:
                    self.assertEqual(bool(getattr(self.registers.condition, reg2)), False)

    def test_condition_clear(self):
        for i, reg in enumerate(FLAGS):
            for r in reg:
                self.registers.F = 0xFF
                setattr(self.registers.condition, r, False)
                self.assertEqual(self.registers.F, 0xFF - (0x01 << (7 - i)))

            for reg2 in flatten(FLAGS):
                if reg2 not in reg:
                    self.assertEqual(bool(getattr(self.registers.condition, reg2)), True)

    def test_condition_set_notZ(self):
        self.registers.F = 0
        self.registers.condition.notZ = False
        self.assertEqual(self.registers.F, 0x01 << (7 - 1))

        for reg2 in flatten(FLAGS):
            if reg2 != "Z":
                self.assertEqual(bool(getattr(self.registers.condition, reg2)), False)

    def test_condition_clear_notZ(self):
        self.registers.F = 0xFF
        self.registers.condition.notZ = True
        self.assertEqual(self.registers.F, 0xFF - (0x01 << (7 - 1)))

        for reg2 in flatten(FLAGS):
            if reg2 != "Z":
                self.assertEqual(bool(getattr(self.registers.condition, reg2)), True)

    def check_condition_group(self, group: str):
        condition = self.registers.condition

        setattr(condition, group, True)
        for reg in group:
            self.assertTrue(getattr(condition, reg))

        setattr(condition, group, False)
        for reg in group:
            self.assertFalse(getattr(condition, reg))

    def test_condition_groups(self):
        self.check_condition_group("SHN")
        self.check_condition_group("HN")
        self.check_condition_group("HNC")
        self.check_condition_group("NC")


if __name__ == '__main__':
    unittest.main()
