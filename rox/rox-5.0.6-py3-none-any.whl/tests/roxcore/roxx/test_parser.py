#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from rox.core.roxx.node import NodeTypes
from rox.core.roxx.parser import Parser
from rox.core.roxx.token_type import TokenTypes
from rox.core.roxx.tokenized_expression import TokenizedExpression
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.repositories.roxx.properties_extensions import PropertiesExtensions


class ParserTests(unittest.TestCase):
    def test_simple_tokenization(self):
        operators = {'eq', 'lt'}
        tokens = TokenizedExpression('eq(false, lt(-123, "123"))', operators).get_tokens()

        self.assertEqual(5, len(tokens))
        self.assertEqual(NodeTypes.RATOR, tokens[0].type)
        self.assertEqual('eq', tokens[0].value)
        self.assertEqual(NodeTypes.RAND, tokens[1].type)
        self.assertEqual(False, tokens[1].value)
        self.assertEqual(NodeTypes.RATOR, tokens[2].type)
        self.assertEqual('lt', tokens[2].value)
        self.assertEqual(NodeTypes.RAND, tokens[3].type)
        self.assertEqual(-123, tokens[3].value)
        self.assertEqual(NodeTypes.RAND, tokens[4].type)
        self.assertEqual('123', tokens[4].value)

    def test_token_type(self):
        self.assertEqual(TokenTypes.NUMBER, TokenTypes.from_token('123'))
        self.assertEqual(TokenTypes.NUMBER, TokenTypes.from_token('-123'))
        self.assertEqual(TokenTypes.NUMBER, TokenTypes.from_token('-123.23'))
        self.assertEqual(TokenTypes.NUMBER, TokenTypes.from_token('123.23'))

        self.assertNotEqual(TokenTypes.STRING, TokenTypes.from_token('-123'))
        self.assertEqual(TokenTypes.STRING, TokenTypes.from_token('"-123"'))
        self.assertEqual(TokenTypes.STRING, TokenTypes.from_token('"undefined"'))
        self.assertNotEqual(TokenTypes.STRING, TokenTypes.from_token('undefined'))

        self.assertEqual(TokenTypes.BOOLEAN, TokenTypes.from_token('false'))
        self.assertEqual(TokenTypes.BOOLEAN, TokenTypes.from_token('true'))
        self.assertNotEqual(TokenTypes.BOOLEAN, TokenTypes.from_token('undefined'))

        self.assertEqual(TokenTypes.UNDEFINED, TokenTypes.from_token('undefined'))
        self.assertNotEqual(TokenTypes.UNDEFINED, TokenTypes.from_token('false'))

    def test_simple_expression_evaluation(self):
        parser = Parser(None)

        self.assertEqual('', parser.evaluate_expression('\"\"').value)
        self.assertEqual(True, parser.evaluate_expression('true').value)
        self.assertEqual('red', parser.evaluate_expression('"red"').value)
        self.assertEqual(True, parser.evaluate_expression('and(true, or(true, true))').value)
        self.assertEqual(True, parser.evaluate_expression('and(true, or(false, true))').value)
        self.assertEqual(True, parser.evaluate_expression('not(and(false, or(false, true)))').value)

    def test_eq_expressions_evaluation(self):
        parser = Parser(None)

        self.assertEqual(True, parser.evaluate_expression('eq("la la", "la la")').value)
        self.assertEqual(False, parser.evaluate_expression('eq("la la", "la,la")').value)
        self.assertEqual(True, parser.evaluate_expression('eq("lala", "lala")').value)
        self.assertEqual(True, parser.evaluate_expression('ne(100.123, 100.321)').value)
        self.assertEqual(False, parser.evaluate_expression('not(eq(undefined, undefined))').value)
        self.assertEqual(True, parser.evaluate_expression('not(eq(not(undefined), undefined))').value)
        self.assertEqual(True, parser.evaluate_expression('not(undefined)').value)

        roxx_string = r'la \"la\" la'
        self.assertEqual(True, parser.evaluate_expression(r'eq("%s", "la \"la\" la")' % roxx_string).value)

    def test_compare_expressions_evaluation(self):
        parser = Parser(None)

        self.assertEqual(False, parser.evaluate_expression('lt(500, 100)').value)
        self.assertEqual(False, parser.evaluate_expression('lt(500, 500)').value)
        self.assertEqual(True, parser.evaluate_expression('lt(500, 500.54)').value)
        self.assertEqual(True, parser.evaluate_expression('lt(500, "500.54")').value)
        self.assertEqual(True, parser.evaluate_expression('lte(500, 500)').value)

        self.assertEqual(True, parser.evaluate_expression('gt(500, 100)').value)
        self.assertEqual(False, parser.evaluate_expression('gt(500, 500)').value)
        self.assertEqual(True, parser.evaluate_expression('gt(500.54, 500)').value)
        self.assertEqual(True, parser.evaluate_expression('gte(500, 500)').value)
        self.assertEqual(True, parser.evaluate_expression('gte("500", 500)').value)

    def test_num_eq_or_not_eq_expressions_evaluation(self):
        parser = Parser(None)

        self.assertEqual(True, parser.evaluate_expression('numeq(400, 400)').value)
        self.assertEqual(True, parser.evaluate_expression('numeq(400, "400")').value)
        self.assertEqual(False, parser.evaluate_expression('numeq(400, 500)').value)
        self.assertEqual(False, parser.evaluate_expression('numeq(400, "500")').value)

        self.assertEqual(False, parser.evaluate_expression('numne(400, 400)').value)
        self.assertEqual(False, parser.evaluate_expression('numne(400, "400")').value)
        self.assertEqual(True, parser.evaluate_expression('numne(400, 500)').value)
        self.assertEqual(True, parser.evaluate_expression('numne(400, "500")').value)

    def test_semver_comparison_evaluation(self):
        parser = Parser(None)

        self.assertEqual(False, parser.evaluate_expression('semverLt("1.1.0", "1.1")').value)
        self.assertEqual(False, parser.evaluate_expression('semverLte("1.1.0", "1.1")').value)
        self.assertEqual(True, parser.evaluate_expression('semverGte("1.1.0", "1.1")').value)

        self.assertEqual(False, parser.evaluate_expression('semverEq("1.0.0", "1")').value)
        self.assertEqual(True, parser.evaluate_expression('semverNe("1.0.1", "1.0.0.1")').value)

        self.assertEqual(True, parser.evaluate_expression('semverLt("1.1", "1.2")').value)
        self.assertEqual(True, parser.evaluate_expression('semverLte("1.1", "1.2")').value)
        self.assertEqual(False, parser.evaluate_expression('semverGt("1.1.1", "1.2")').value)
        self.assertEqual(True, parser.evaluate_expression('semverGt("1.2.1", "1.2")').value)

    def test_comparison_with_undefined_evaluation(self):
        parser = Parser(None)

        self.assertEqual(False, parser.evaluate_expression('gte(500, undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('gt(500, undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('lte(500, undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('lt(500, undefined)').value)

        self.assertEqual(False, parser.evaluate_expression('semverGte("1.1", undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('semverGt("1.1", undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('semverLte("1.1", undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('semverLt("1.1", undefined)').value)

    def test_unknown_operator_evaluation(self):
        parser = Parser(None)

        self.assertEqual(None, parser.evaluate_expression('NOT_AN_OPERATOR(500, 500)').value)
        self.assertEqual(None, parser.evaluate_expression('JUSTAWORD(500, 500)').value)

    def test_undefined_evaluation(self):
        parser = Parser(None)

        self.assertEqual(True, parser.evaluate_expression('isUndefined(undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('isUndefined(123123)').value)
        self.assertEqual(False, parser.evaluate_expression('isUndefined("undefined")').value)

    def test_now_evaluation(self):
        parser = Parser(None)

        self.assertEqual(True, parser.evaluate_expression('gte(now(), now())').value)
        self.assertEqual(True, parser.evaluate_expression('gte(now(), 2458.123)').value)
        self.assertEqual(True, parser.evaluate_expression('gte(now(), 1534759307565)').value)

    def test_regular_expression_evaluation(self):
        parser = Parser(None)

        self.assertEqual(False, parser.evaluate_expression('match("111", "222", "")').value)
        self.assertEqual(False, parser.evaluate_expression('match(".*", "222", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("22222", ".*", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("22222", "^2*$", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match(\"22222\", \"^2*$\", \"\")').value)
        self.assertEqual(True, parser.evaluate_expression('match(\"22222\", \"^2*$\", b64d(\"\"))').value)
        self.assertEqual(True, parser.evaluate_expression('match("test@shimi.com", ".*(com|ca)", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("test@jet.com", ".*jet\\.com$", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("US", ".*IL|US", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("US", "IL|US"), ""').value)
        self.assertEqual(True, parser.evaluate_expression('match("US", "(IL|US)", "")').value)

        # Test flags
        self.assertEqual(False, parser.evaluate_expression('match("Us", "(IL|US)", "")').value)
        self.assertEqual(True, parser.evaluate_expression('match("uS", "(IL|US)", "i")').value)
        self.assertEqual(True, parser.evaluate_expression('match("uS", "IL|US#Comment", "xi")').value)
        self.assertEqual(True, parser.evaluate_expression('match("\n", ".", "s")').value)
        self.assertEqual(True, parser.evaluate_expression('match("HELLO\nTeST\n#This is a comment", "^TEST$", "ixm")').value)

    def test_if_then_expression_evaluation_string(self):
        parser = Parser(None)

        self.assertEqual('AB', parser.evaluate_expression('ifThen(and(true, or(true, true)), "AB", "CD")').value)
        self.assertEqual('CD', parser.evaluate_expression('ifThen(and(false, or(true, true)), "AB", "CD")"').value)

        self.assertEqual('AB', parser.evaluate_expression('ifThen(and(true, or(true, true)), "AB", ifThen(and(true, or(true, true)), "EF", "CD"))').value)
        self.assertEqual('EF', parser.evaluate_expression('ifThen(and(false, or(true, true)), "AB", ifThen(and(true, or(true, true)), "EF", "CD"))').value)
        self.assertEqual('CD', parser.evaluate_expression('ifThen(and(false, or(true, true)), "AB", ifThen(and(true, or(false, false)), "EF", "CD"))').value)

        self.assertEqual(None, parser.evaluate_expression('ifThen(and(false, or(true, true)), "AB", ifThen(and(true, or(false, false)), "EF", undefined))').value)

    def test_if_then_expression_evaluation_int_number(self):
        parser = Parser(None)

        self.assertEqual(1, parser.evaluate_expression('ifThen(and(true, or(true, true)), 1, 2)').value)
        self.assertEqual(2, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1, 2)').value)

        self.assertEqual(1, parser.evaluate_expression('ifThen(and(true, or(true, true)), 1, ifThen(and(true, or(true, true)), 3, 2))').value)
        self.assertEqual(3, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1, ifThen(and(true, or(true, true)), 3, 2))').value)
        self.assertEqual(2, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1, ifThen(and(true, or(false, false)), 3, 2))').value)

        self.assertEqual(None, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1, ifThen(and(true, or(false, false)), 3, undefined))').value)

    def test_if_then_expression_evaluation_float_number(self):
        parser = Parser(None)

        self.assertEqual(1.1, parser.evaluate_expression('ifThen(and(true, or(true, true)), 1.1, 2.2)').value)
        self.assertEqual(2.2, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1.1, 2.2)').value)

        self.assertEqual(1.1, parser.evaluate_expression('ifThen(and(true, or(true, true)), 1.1, ifThen(and(true, or(true, true)), 3.3, 2.2))').value)
        self.assertEqual(3.3, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1.1, ifThen(and(true, or(true, true)), 3.3, 2.2))').value)
        self.assertEqual(2.2, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1.1, ifThen(and(true, or(false, false)), 3.3, 2.2))').value)

        self.assertEqual(None, parser.evaluate_expression('ifThen(and(false, or(true, true)), 1.1, ifThen(and(true, or(false, false)), 3.3, undefined))').value)

    def test_if_then_expression_evaluation_boolean(self):
        parser = Parser(None)

        self.assertEqual(True, parser.evaluate_expression('ifThen(and(true, or(true, true)), true, false)').value)
        self.assertEqual(False, parser.evaluate_expression('ifThen(and(false, or(true, true)), true, false)').value)

        self.assertEqual(False, parser.evaluate_expression('ifThen(and(true, or(true, true)), false, ifThen(and(true, or(true, true)), true, true))').value)
        self.assertEqual(True, parser.evaluate_expression('ifThen(and(false, or(true, true)), false, ifThen(and(true, or(true, true)), true, false))').value)
        self.assertEqual(False, parser.evaluate_expression('ifThen(and(false, or(true, true)), true, ifThen(and(true, or(false, false)), true, false))').value)

        self.assertEqual(True, parser.evaluate_expression('ifThen(and(false, or(true, true)), false, ifThen(and(true, or(false, false)), false, (and(true,true))))').value)
        self.assertEqual(False, parser.evaluate_expression('ifThen(and(false, or(true, true)), true, ifThen(and(true, or(false, false)), true, (and(true,false))))').value)

        self.assertEqual(None, parser.evaluate_expression('ifThen(and(false, or(true, true)), true, ifThen(and(true, or(false, false)), true, undefined))').value)

    def test_in_array(self):
        parser = Parser(None)
        custom_property_repository = CustomPropertyRepository()
        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        def merge_seed(parser, stack, context):
            seed1 = stack.pop()
            seed2 = stack.pop()
            stack.push("%s.%s" % (seed1, seed2))

        parser.add_operator('mergeSeed', merge_seed)

        self.assertEqual(False, parser.evaluate_expression('inArray("123", ["222", "233"])').value)
        self.assertEqual(True, parser.evaluate_expression('inArray("123", ["123", "233"])').value)
        self.assertEqual(False, parser.evaluate_expression('inArray("123", [123, "233"])').value)
        self.assertEqual(True, parser.evaluate_expression('inArray("123", [123, "123", "233"])').value)

        self.assertEqual(True, parser.evaluate_expression('inArray(123, [123, "233"])').value)
        self.assertEqual(False, parser.evaluate_expression('inArray(123, ["123", "233"])').value)

        self.assertEqual(False, parser.evaluate_expression('inArray("123", [])').value)
        self.assertEqual(True, parser.evaluate_expression('inArray("1 [23", ["1 [23", "]"])').value)
        self.assertEqual(False, parser.evaluate_expression('inArray("123", undefined)').value)
        self.assertEqual(False, parser.evaluate_expression('inArray(undefined, [])').value)
        self.assertEqual(True, parser.evaluate_expression('inArray(undefined, [undefined, 123])').value)
        self.assertEqual(False, parser.evaluate_expression('inArray(undefined, undefined)').value)

        self.assertEqual(True, parser.evaluate_expression('inArray(mergeSeed("123", "456"), ["123.456", "233"])').value)
        self.assertEqual(False, parser.evaluate_expression('inArray("123.456", [mergeSeed("123", "456"), "233"])').value)  # THIS CASE IS NOT SUPPORTED

        self.assertEqual('07915255d64730d06d2349d11ac3bfd8', parser.evaluate_expression('md5("stam")').value)
        self.assertEqual('stamstam2', parser.evaluate_expression('concat("stam","stam2")').value)
        self.assertEqual(True, parser.evaluate_expression('inArray(md5(concat("st","am")), ["07915255d64730d06d2349d11ac3bfd8"]').value)
        self.assertEqual(True, parser.evaluate_expression('eq(md5(concat("st",property("am"))), undefined)').value)

        self.assertEqual('stam', parser.evaluate_expression('b64d("c3RhbQ==")').value)
        self.assertEqual('𩸽', parser.evaluate_expression('b64d("8Km4vQ==")').value)
        self.assertEqual('', parser.evaluate_expression('b64d(\"\")').value)
        