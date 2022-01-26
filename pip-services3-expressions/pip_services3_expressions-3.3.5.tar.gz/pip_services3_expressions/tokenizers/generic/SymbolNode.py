# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.utilities.CharReferenceMap import CharReferenceMap
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class SymbolNode:
    """
    A **SymbolNode** object is a member of a tree that contains all possible prefixes
    of allowable symbols. Multi-character symbols appear in a **SymbolNode** tree
    with one node for each character.

    For example, the symbol **=:~** will appear in a tree as three nodes. The first
    node contains an equals sign, and has a child; that child contains a colon and has a child;
    this third child contains a tilde, and has no children of its own. If the colon node had
    another child for a dollar sign character, then the tree would contain the symbol **=:$**.

    A tree of **SymbolNode** objects collaborate to read a (potentially multi-character)
    symbol from an input stream. A root node with no character of its own finds an initial node
    that represents the first character in the input. This node looks to see if the next character
    in the stream matches one of its children. If so, the node delegates its reading task to its child.
    This approach walks down the tree, pulling symbols from the input that match the path down the tree.

    When a node does not have a child that matches the next character, we will have read the longest
    possible symbol prefix. This prefix may or may not be a valid symbol.
    Consider a tree that has had **=:~** added and has not had **=:** added.
    In this tree, of the three nodes that contain **=:~**, only the first and third contain
    complete symbols. If, say, the input contains **=:a**, the colon node will not have
    a child that matches the 'a' and so it will stop reading. The colon node has to "unread": it must
    push back its character, and ask its parent to unread. Unreading continues until it reaches
    an ancestor that represents a valid symbol.
    """

    def __init__(self, parent: Optional['SymbolNode'], character: int):
        """
        Constructs a SymbolNode with the given parent, representing the given character.

        :param parent: This node's parent
        :param character: This node's associated character.
        """
        self.__children: CharReferenceMap = None
        self.__token_type: TokenType = TokenType.Unknown
        self.__valid: bool = None
        self.__ancestry: str = None
        self.__parent: SymbolNode = parent
        self.__character: int = character

    def ensure_child_with_char(self, value: int):
        """
        Find or create a child for the given character.
        """
        if not self.__children:
            self.__children = CharReferenceMap()

        child_node = self.__children.lookup(value)
        if not child_node:
            child_node = SymbolNode(self, value)
            self.__children.add_interval(value, value, child_node)

        return child_node

    def add_descendant_line(self, value: str, token_type: TokenType):
        """
        Add a line of descendants that represent the characters in the given string.

        :param value:
        :param token_type:
        """
        if len(value) > 0:
            child_node = self.ensure_child_with_char(ord(value[0]))
            child_node.add_descendant_line(value[1:], token_type)
        else:
            self.__valid = True
            self.__token_type = token_type

    def deepest_read(self, scanner: IScanner) -> 'SymbolNode':
        """
        Find the descendant that takes as many characters as possible from the input.

        :param scanner:
        """
        nex_symbol = scanner.read()
        child_node = self.find_child_with_char(nex_symbol) if not CharValidator.is_eof(nex_symbol) else None
        if not child_node:
            scanner.unread()
            return self
        return child_node.deepest_read(scanner)

    def find_child_with_char(self, value) -> 'SymbolNode':
        """
        Find a child with the given character.

        :param value:
        """
        return self.__children.lookup(value) if self.__children is not None else None

    def unread_to_valid(self, scanner: IScanner) -> 'SymbolNode':
        """
        Unwind to a valid node; this node is "valid" if its ancestry represents a complete symbol.
        If this node is not valid, put back the character and ask the parent to unwind.

        :param scanner:
        """
        if not self.__valid and self.__parent is not None:
            scanner.unread()
            return self.__parent.unread_to_valid(scanner)

        return self

    @property
    def valid(self) -> bool:
        return self.__valid

    @valid.setter
    def valid(self, value: bool):
        self.__valid = value

    @property
    def token_type(self) -> TokenType:
        return self.__token_type

    @token_type.setter
    def token_type(self, value: bool):
        self.__token_type = value

    def ancestry(self) -> str:
        """
        Show the symbol this node represents.
        
        :return: The symbol this node represents.
        """
        if self.__ancestry is None:
            self.__ancestry = (self.__parent.ancestry() if self.__parent is not None else "") + \
                              (chr(self.__character) if self.__character != 0 else "")

        return self.__ancestry
