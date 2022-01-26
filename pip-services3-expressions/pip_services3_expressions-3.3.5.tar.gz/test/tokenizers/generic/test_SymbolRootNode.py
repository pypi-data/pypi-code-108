# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.SymbolRootNode import SymbolRootNode


class TestSymbolRootNode:

    def test_next_token(self):
        node = SymbolRootNode()
        node.add("<", TokenType.Symbol)
        node.add("<<", TokenType.Symbol)
        node.add("<>", TokenType.Symbol)

        scanner = StringScanner("<A<<<>")

        token = node.next_token(scanner)
        assert "<" == token.value

        token = node.next_token(scanner)
        assert "A" == token.value

        token = node.next_token(scanner)
        assert "<<" == token.value

        token = node.next_token(scanner)
        assert "<>" == token.value

    def test_single_token(self):
        node = SymbolRootNode()

        scanner = StringScanner("<A")

        token = node.next_token(scanner)
        assert "<" == token.value
        assert TokenType.Symbol == token.type
