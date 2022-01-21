"""NanamiLang Core Tests"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import datetime
import unittest
from typing import List

from nanamilang.shortcuts import truncated, aligned
from nanamilang.token import Token
from nanamilang.module import Module
from nanamilang.tokenizer import Tokenizer
from nanamilang.datatypes import NException
from nanamilang.bdb import BuiltinMacrosDB, BuiltinFunctionsDB
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros

__unittest = True  # <- do not show that no fancy traceback :(


class FancyAssertionError(AssertionError):
    """Because we want make it look nicer"""

    # TODO: actually print fancy err message

    def __str__(self):
        """Return an empty string for now (TODO: implement)"""
        return ''

    def __repr__(self):
        """Return an empty string for now (TODO: implement)"""
        return ''


class TestNanamiLangCore(unittest.TestCase):
    """NanamiLang Core Test Cases go here"""

    @staticmethod
    def tokenize(line: str):
        """Shortcut for tokenizing"""
        return Tokenizer(name='<coretests>', source=line).tokenize()

    @staticmethod
    def convert(expected: List[Token], actual: List[Token]):
        """Make self.assertEqual working when we test Tokenizer.tokenize() method"""
        return [[list(map(lambda t: t.type(), actual)),
                 list(map(lambda t: t.dt().reference() if t.dt() else None, actual))],
                [list(map(lambda t: t.type(), expected)),
                 list(map(lambda t: t.dt().reference() if t.dt() else None, expected))]]

    def test_one_liners(self):
        """Go through the various one-liners"""

        BuiltinMacrosDB.initialize(BuiltinMacros)
        BuiltinFunctionsDB.initialize(BuiltinFunctions)

        # We need to initialize Builtin*DB, or we are in danger :)

        tests = [
            '(= (+ 1 2) 3)',
            '(= (let [fun (fn [] 1)] (fun)) 1)',
            '(= (let [fun (fn [n] n)] (fun 1)) 1)',
            '(= (.nominal (let [fun (fn [] 1)] fun)) "Function"))',
            '(= (.nominal (let [fun (fn [n] n)] fun)) "Function"))',
            '(= (get {{:a 1} 1} {:a 1}) 1)',
            '(= (get #{{:a 1}} {:a 1}) {:a 1})',
            '(= (get [{:a 1}] 0) {:a 1})',
            '(= (.nominal {}) "HashMap")',
            '(= (.nominal []) "Vector")',
            '(= (.nominal #{}) "HashSet")',
            '(= 0 (:a {:a 0}))',
            '(let [[key val] [:a 0]] (= val (key {:a 0})))',
            '(let [{:keys [a b]} {:a 1 :b 2}] (= (+ a b) 3))',
            '(let [{:strs [a b]} {"a" 1 "b" 2}] (= (+ a b) 3))',
            '(= [:cat] (map :kind [{:kind :cat :home? true}])])',
            '(= [{:home? true :kind :cat}] (filter :home? [{:kind :cat :home? true}]))',
            '(= (for [x (.range [] 0 10)] (+ (identity x) 10)) [10 11 12 13 14 15 16 17 18 19)'
            # Please, random person, we need your help, write tests, we need to cover even more!
        ]
        failed = False
        module = Module()
        for test in tests:
            module.prepare(test)
            actual = module.evaluate().results()[0]
            failed = isinstance(actual, NException) or not actual.truthy()
            if failed:
                _ = aligned('\nE: ', test + ' was failed unfortunately', 71)
                print(truncated(_, 70))  # <- print that fancy aligned and truncated string :)
                break
        self.assertEqual(failed, False)  # if at least one test was failed, raise AssertionError

    def test_tokenizer_tokenize(self):
        """Ensure that we can tokenize that messy string"""

        self.maxDiff = None  # <- we need to view FULL difference
        self.failureException = FancyAssertionError  # <- we need to actually implement methods!

        # TODO: nobody said that we can just stop our work on improving a 'Tokenizer.tokenize()'
        expected = [Token(Token.ListBegin),
                    Token(Token.Identifier, "+"),
                    Token(Token.Identifier, 'sample'),
                    Token(Token.Identifier, 'SAMPLE'),
                    Token(Token.Identifier, 'Sa-Mp-Le'),
                    Token(Token.IntegerNumber, 0),
                    Token(Token.IntegerNumber, 1),
                    Token(Token.FloatNumber, 2.5),
                    Token(Token.FloatNumber, 2.25),
                    Token(Token.FloatNumber, 31.3),
                    Token(Token.String, ""),
                    Token(Token.String, " "),
                    Token(Token.String, "string"),
                    Token(Token.IntegerNumber, 0),
                    Token(Token.IntegerNumber, 11),
                    Token(Token.IntegerNumber, 22),
                    Token(Token.Boolean, True),
                    Token(Token.Boolean, False),
                    Token(Token.Symbol, 'some-2'),
                    Token(Token.Keyword, 'some-2'),
                    Token(Token.IntegerNumber, 85),
                    Token(Token.Date, datetime.datetime.fromisoformat('1970-10-10')),
                    Token(Token.IntegerNumber, 333),
                    Token(Token.IntegerNumber, 3735928559),
                    Token(Token.ListEnd)]
        self.assertEqual(*self.convert(expected, self.tokenize(
            '(+ sample SAMPLE Sa-Mp-Le '
            '0 1 2.5 2.25 31.30 "" " " '
            '"string" 00 11 22 true false \'some-2 :some-2 #01010101 #1970-10-10 333 #deadbeef)')))
