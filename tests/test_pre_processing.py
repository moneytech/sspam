"""Test pre-processing passes.

- TestShiftMult
- TestSubToMult
"""

import ast
import unittest

from sspam import pre_processing
from sspam.tools import asttools


class AstCompCase(unittest.TestCase):
    """
    Generic method to compare obfuscated ast and original ast.
    """

    def generic_AstCompTest(self, *args):
        """Args: (tests, transformer) with tests a list,
        or (input_string, refstring, transformer)"""

        if len(args) != 2 and len(args) != 3:
            raise Exception("generic_AstTest should be " +
                            "called with 3 or 4 arguments")
        if len(args) == 2:
            tests = args[0]
            transformer = args[1]
        else:
            tests = [(args[0], args[1])]
            transformer = args[2]
        for origstring, refstring in tests:
            orig = ast.parse(origstring)
            ref = ast.parse(refstring)
            orig = transformer.visit(orig)
            self.assertTrue(asttools.Comparator().visit(orig, ref))


class TestShiftMult(AstCompCase):
    """
    Test pre-processing that transforms shifts in mults.
    """

    def test_Basics(self):
        'Simple tests for shift -> mult replacement'
        tests = [("x << 1", "x*2"), ("(y*32) << 1", "(y*32)*2"),
                 ("var << 4", "var*16"), ("3 << var", "3 << var"),
                 ("(x ^ y) + (x << 1)", "(x ^ y) + 2*x")]
        self.generic_AstCompTest(tests, pre_processing.ShiftToMult())


class TestSubToMult(AstCompCase):
    """
    Test pre-processing that transforms subs in mults of -1.
    """

    def test_Basics(self):
        'Simple tests for sub -> -1 mult replacement'
        tests = [("-x", "(-1)*x"), ("x - 3", "x + (-1)*3"),
                 ("- x - y", "(-1)*x + (-1)*y")]
        self.generic_AstCompTest(tests, pre_processing.SubToMult())


class RemoveUselessAnd(AstCompCase):
    """
    Test pre-processing removing AND 0xFF...FF
    """

    def test_Basics(self):
        'Simple tests for removing useless ands'
        tests = [("x & 255", "x", 8), ("x & 255", "x & 255", 32),
                 ("x & 65535", "x", 16), ("x & 255", "x & 255", 16)]
        for instring, refstring, nbits in tests:
            remov = pre_processing.RemoveUselessAnd(ast.parse(refstring),
                                                    nbits)
            self.generic_AstCompTest(instring, refstring, remov)



if __name__ == '__main__':
    unittest.main()