from __future__ import annotations

__all__ = ("Flags", "Registers")

from typing import Any


class Flags:
    __slots__ = ("_regs")
    _regs: Registers

    # ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]

    def __init__(self, regs: Registers):
        self._regs = regs

    @property
    def S(self):
        return (self._regs.AF >> 7) & 1

    @property
    def Z(self):
        return (self._regs.AF >> 6) & 1

    @property
    def notZ(self):
        return ((self._regs.AF >> 6) & 1) ^ 1

    @property
    def F5(self):
        return (self._regs.AF >> 5) & 1

    @property
    def H(self):
        return (self._regs.AF >> 4) & 1

    @property
    def F3(self):
        return (self._regs.AF >> 3) & 1

    @property
    def PV(self):
        return (self._regs.AF >> 2) & 1

    @property
    def N(self):
        return (self._regs.AF >> 1) & 1

    @property
    def C(self):
        return self._regs.AF & 1

    @S.setter
    def S(self, val):
        if val:
            self._regs.AF |= 0x0080
        else:
            self._regs.AF &= 0xFF7F

    @Z.setter
    def Z(self, val):
        if val:
            self._regs.AF |= 0x0040
        else:
            self._regs.AF &= 0xFFBF

    @notZ.setter
    def notZ(self, val):
        if val:
            self._regs.AF &= 0xFFBF
        else:
            self._regs.AF |= 0x0040

    @F5.setter
    def F5(self, val):
        if val:
            self._regs.AF |= 0x0020
        else:
            self._regs.AF &= 0xFFDF

    @H.setter
    def H(self, val):
        if val:
            self._regs.AF |= 0x0010
        else:
            self._regs.AF &= 0xFFEF

    @F3.setter
    def F3(self, val):
        if val:
            self._regs.AF |= 0x0008
        else:
            self._regs.AF &= 0xFFF7

    @PV.setter
    def PV(self, val):
        if val:
            self._regs.AF |= 0x0004
        else:
            self._regs.AF &= 0xFFFB

    @N.setter
    def N(self, val):
        if val:
            self._regs.AF |= 0x0002
        else:
            self._regs.AF &= 0xFFFD

    @C.setter
    def C(self, val):
        if val:
            self._regs.AF |= 0x0001
        else:
            self._regs.AF &= 0xFFFE

    @property
    def SHN(self):
        raise NotImplementedError()

    @property
    def HN(self):
        raise NotImplementedError()

    @property
    def HNC(self):
        raise NotImplementedError()

    @property
    def NC(self):
        raise NotImplementedError()

    @SHN.setter
    def SHN(self, val):
        # ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]
        if val:
            self._regs.AF |= 0x0092
        else:
            self._regs.AF &= 0xFF6D

    @HN.setter
    def HN(self, val):
        # ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]
        if val:
            self._regs.AF |= 0x0012
        else:
            self._regs.AF &= 0xFFED

    @HNC.setter
    def HNC(self, val):
        # ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]
        if val:
            self._regs.AF |= 0x0013
        else:
            self._regs.AF &= 0xFFEC

    @NC.setter
    def NC(self, val):
        # ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]
        if val:
            self._regs.AF |= 0x0003
        else:
            self._regs.AF &= 0xFFFC


class Registers:
    __slots__ = ("PC", "SP", "IX", "IY", "I", "R",
                 "AF", "AF_",
                 "BC", "BC_",
                 "DE", "DE_",
                 "HL", "HL_",
                 "condition", "flags",
                 "HALT", "IFF", "IFF2", "IM",
                 "power")

    power: Any

    def __init__(self, **kwargs):
        self.PC = 0  # Program Counter (16bit)
        self.SP = 0  # Stack Pointer (16bit)
        self.IX = 0  # Index Register X (16bit)
        self.IY = 0  # Index Register Y (16bit)
        self.I = 0  # Interrupt Page Address (8bit)
        self.R = 0  # Memory Refresh (8bit)

        self.AF = 0  # Accumulator + Flags (16bit)
        self.AF_ = 0  # Accumulator + Flags (16bit)

        self.BC = 0  # General (16bit)
        self.BC_ = 0  # General (16bit)

        self.DE = 0  # General (16bit)
        self.DE_ = 0  # General (16bit)

        self.HL = 0  # General (16bit)
        self.HL_ = 0  # General (16bit)

        self.condition = Flags(self)
        self.flags = self.condition

        self.HALT = False  #
        self.IFF = False  # Interrupt flip flop
        self.IFF2 = False  # NM Interrupt flip flop
        self.IM = False  # Interrupt mode

        for key, value in kwargs.items():
            setattr(self, key, value)

    def reset(self):
        self.__init__()

    @property
    def A(self) -> int:
        return self.AF >> 8

    @property
    def F(self) -> int:
        return self.AF & 0xFF

    @property
    def B(self) -> int:
        return self.BC >> 8

    @property
    def C(self) -> int:
        return self.BC & 0xFF

    @property
    def D(self) -> int:
        return self.DE >> 8

    @property
    def E(self) -> int:
        return self.DE & 0xFF

    @property
    def H(self) -> int:
        return self.HL >> 8

    @property
    def L(self) -> int:
        return self.HL & 0xFF

    @property
    def IXH(self) -> int:
        return self.IX >> 8

    @property
    def IXL(self) -> int:
        return self.IX & 0xFF

    @property
    def IYH(self) -> int:
        return self.IY >> 8

    @property
    def IYL(self) -> int:
        return self.IY & 0xFF

    @A.setter
    def A(self, val):
        self.AF = (self.AF & 0x00FF) | ((val & 0xFF) << 8)

    @F.setter
    def F(self, val):
        self.AF = (self.AF & 0xFF00) | (val & 0xFF)

    @B.setter
    def B(self, val):
        self.BC = (self.BC & 0x00FF) | ((val & 0xFF) << 8)

    @C.setter
    def C(self, val):
        self.BC = (self.BC & 0xFF00) | (val & 0xFF)

    @D.setter
    def D(self, val):
        self.DE = (self.DE & 0x00FF) | ((val & 0xFF) << 8)

    @E.setter
    def E(self, val):
        self.DE = (self.DE & 0xFF00) | (val & 0xFF)

    @H.setter
    def H(self, val):
        self.HL = (self.HL & 0x00FF) | ((val & 0xFF) << 8)

    @L.setter
    def L(self, val):
        self.HL = (self.HL & 0xFF00) | (val & 0xFF)

    @IXH.setter
    def IXH(self, val):
        self.IX = (self.IX & 0x00FF) | ((val & 0xFF) << 8)

    @IXL.setter
    def IXL(self, val):
        self.IX = (self.IX & 0xFF00) | (val & 0xFF)

    @IYH.setter
    def IYH(self, val):
        self.IY = (self.IY & 0x00FF) | ((val & 0xFF) << 8)

    @IYL.setter
    def IYL(self, val):
        self.IY = (self.IY & 0xFF00) | (val & 0xFF)

    def __getitem__(self, reg):
        return getattr(self, reg)

    def __setitem__(self, reg, val):
        return setattr(self, reg, val)

    @classmethod
    def create(cls):
        return cls()
