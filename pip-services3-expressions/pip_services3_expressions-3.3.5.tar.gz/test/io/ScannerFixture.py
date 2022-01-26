# -*- coding: utf-8 -*-


class ScannerFixture:

    def __init__(self, scanner, content):
        self.__scanner = scanner
        self.__content = content

    def test_read(self):
        self.__scanner.reset()

        for i in range(len(self.__content)):
            char = self.__scanner.read()
            assert ord(self.__content[i]) == char

        char = self.__scanner.read()
        assert -1 == char

        char = self.__scanner.read()
        assert -1 == char

    def test_unread(self):
        self.__scanner.reset()

        char = self.__scanner.peek()
        assert ord(self.__content[0]) == char

        char = self.__scanner.read()
        assert ord(self.__content[0]) == char

        char = self.__scanner.read()
        assert ord(self.__content[1]) == char

        self.__scanner.unread()
        char = self.__scanner.read()
        assert ord(self.__content[1]) == char

        self.__scanner.unread_many(2)
        char = self.__scanner.read()
        assert ord(self.__content[0]) == char
        char = self.__scanner.read()
        assert ord(self.__content[1]) == char

    def test_line_column(self, position, char_at, line, column):
        self.__scanner.reset()

        # Get in position
        while position > 1:
            self.__scanner.read()
            position -= 1

        # Test forward scanning
        char = self.__scanner.read()
        assert char == char_at
        ln = self.__scanner.line()
        assert line == ln
        col = self.__scanner.column()
        assert column == col

        # Moving backward
        char = self.__scanner.read()
        if char != -1:
            self.__scanner.unread()
        self.__scanner.unread()

        # Test backward scanning
        char = self.__scanner.read()
        assert char_at == char
        ln = self.__scanner.line()
        assert line == ln
        col = self.__scanner.column()
        assert col == column
