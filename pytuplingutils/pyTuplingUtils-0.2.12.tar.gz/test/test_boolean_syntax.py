#!/usr/bin/env python3
#
# Authorop: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Jun 18, 2020 at 02:47 AM +0800

import unittest

from context import pyTuplingUtils as ptu

parser = ptu.boolean.syntax.boolean_parser.parse


class ArithmeticTest(unittest.TestCase):
    def test_var(self):
        self.assertEqual(
            parser('a').pretty(),
            "var\ta\n"
        )
        self.assertEqual(
            parser('-a').pretty(),
            "neg\n"
            "  var\ta\n"
        )
        self.assertEqual(
            parser('a1').pretty(),
            "var\ta1\n"
        )
        self.assertEqual(
            parser('a_1b').pretty(),
            "var\ta_1b\n"
        )

    def test_num(self):
        self.assertEqual(
            parser('1').pretty(),
            "num\t1\n"
        )
        self.assertEqual(
            parser('+1').pretty(),
            "num\t+1\n"
        )

    def test_negative_num(self):
        self.assertEqual(
            parser('-1.6').pretty(),
            "num\t-1.6\n"
        )
        self.assertEqual(
            parser('+1').pretty(),
            "num\t+1\n"
        )

    def test_add(self):
        self.assertEqual(
            parser('-1 +2.3').pretty(),
            "add\n"
            "  num\t-1\n"
            "  num\t2.3\n"
        )

    def test_add_sub(self):
        self.assertEqual(
            parser('-1 +2.3 - 10').pretty(),
            "sub\n"
            "  add\n"
            "    num\t-1\n"
            "    num\t2.3\n"
            "  num\t10\n"
        )

    def test_add_mul(self):
        self.assertEqual(
            parser('-1 +2.3 * 10').pretty(),
            "add\n"
            "  num\t-1\n"
            "  mul\n"
            "    num\t2.3\n"
            "    num\t10\n"
        )

    def test_add_mul_par(self):
        self.assertEqual(
            parser('-(1 +2.3) * 10').pretty(),
            "mul\n"
            "  neg\n"
            "    add\n"
            "      num\t1\n"
            "      num\t2.3\n"
            "  num\t10\n"
        )


class BooleanTest(unittest.TestCase):
    def test_comp(self):
        self.assertEqual(
            parser('!(-a_2 +2.3) ').pretty(),
            "comp\n"
            "  add\n"
            "    neg\n"
            "      var\ta_2\n"
            "    num\t2.3\n"
        )

    def test_eq(self):
        self.assertEqual(
            parser('a == b').pretty(),
            "eq\n"
            "  var\ta\n"
            "  var\tb\n"
        )
        self.assertEqual(
            parser('a == 1').pretty(),
            "eq\n"
            "  var\ta\n"
            "  num\t1\n"
        )
        self.assertEqual(
            parser('a <= -1+x').pretty(),
            "lte\n"
            "  var\ta\n"
            "  add\n"
            "    num\t-1\n"
            "    var\tx\n"
        )

    def test_bool(self):
        self.assertEqual(
            parser('a & 1').pretty(),
            "andop\n"
            "  var\ta\n"
            "  num\t1\n"
        )
        self.assertEqual(
            parser('True | False').pretty(),
            "orop\n"
            "  bool\tTrue\n"
            "  bool\tFalse\n"
        )
        self.assertEqual(
            parser('True | False & True').pretty(),
            "orop\n"
            "  bool\tTrue\n"
            "  andop\n"
            "    bool\tFalse\n"
            "    bool\tTrue\n"
        )
        self.assertEqual(
            parser('(True | False) & !True | false').pretty(),
            "orop\n"
            "  andop\n"
            "    orop\n"
            "      bool\tTrue\n"
            "      bool\tFalse\n"
            "    comp\n"
            "      bool\tTrue\n"
            "  bool\tfalse\n"
        )

    def test_comb(self):
        self.assertEqual(
            parser('a >= !(-1+x)*3').pretty(),
            "gte\n"
            "  var\ta\n"
            "  comp\n"
            "    mul\n"
            "      add\n"
            "        num\t-1\n"
            "        var\tx\n"
            "      num\t3\n"
        )
        self.assertEqual(
            parser('a >= !(-1+x)*3 | x<8 & y != -(z+3)').pretty(),
            "orop\n"
            "  gte\n"
            "    var\ta\n"
            "    comp\n"
            "      mul\n"
            "        add\n"
            "          num\t-1\n"
            "          var\tx\n"
            "        num\t3\n"
            "  andop\n"
            "    lt\n"
            "      var\tx\n"
            "      num\t8\n"
            "    neq\n"
            "      var\ty\n"
            "      neg\n"
            "        add\n"
            "          var\tz\n"
            "          num\t3\n"
        )
        self.assertEqual(
            parser('a >= !(-1+x)*3 | x<8 & y != -(z+3)').pretty(),
            parser('a >= !(-1+x)*3 | (x<8 & y != -(z+3))').pretty()
        )


class FunctionCallTest(unittest.TestCase):
    def test_func_call_zero_arg(self):
        self.assertEqual(
            parser('(some_func0())').pretty(),
            "func_call\tsome_func0\n"
        )

    def test_func_call_one_arg(self):
        self.assertEqual(
            parser('some_func1(arg1)').pretty(),
            "func_call\n"
            "  some_func1\n"
            "  arglist\n"
            "    var\targ1\n"
        )

    def test_func_call_two_args(self):
        self.assertEqual(
            parser('some_func2(arg1, arg2)').pretty(),
            "func_call\n"
            "  some_func2\n"
            "  arglist\n"
            "    var\targ1\n"
            "    var\targ2\n"
        )

    def test_func_call_arithmetic(self):
        self.assertEqual(
            parser('arith_func((arg1+2)*val3, arg2)').pretty(),
            "func_call\n"
            "  arith_func\n"
            "  arglist\n"
            "    mul\n"
            "      add\n"
            "        var\targ1\n"
            "        num\t2\n"
            "      var\tval3\n"
            "    var\targ2\n"
        )

    def test_func_call_nested(self):
        self.assertEqual(
            parser('arith_func(inner(arg1+2)*val3, arg2)').pretty(),
            "func_call\n"
            "  arith_func\n"
            "  arglist\n"
            "    mul\n"
            "      func_call\n"
            "        inner\n"
            "        arglist\n"
            "          add\n"
            "            var\targ1\n"
            "            num\t2\n"
            "      var\tval3\n"
            "    var\targ2\n"
        )

    def test_func_call_nested_boolean_op(self):
        self.assertEqual(
            parser('arith_func(inner(arg1+2)*val3, arg2) > stuff(a)').pretty(),
            "gt\n"
            "  func_call\n"
            "    arith_func\n"
            "    arglist\n"
            "      mul\n"
            "        func_call\n"
            "          inner\n"
            "          arglist\n"
            "            add\n"
            "              var\targ1\n"
            "              num\t2\n"
            "        var\tval3\n"
            "      var\targ2\n"
            "  func_call\n"
            "    stuff\n"
            "    arglist\n"
            "      var\ta\n"
        )


if __name__ == '__main__':
    unittest.main()
