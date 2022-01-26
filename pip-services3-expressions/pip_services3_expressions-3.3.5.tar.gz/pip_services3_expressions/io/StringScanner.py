# -*- coding: utf-8 -*-

from pip_services3_expressions.io.IScanner import IScanner


class StringScanner(IScanner):
    """
    Scan characters in a string that allows tokenizers
    to look ahead through stream to perform lexical analysis.
    """
    Eof: int = -1

    def __init__(self, content: str):
        """
        Creates an instance of this class.

        :param content: A text content to be read.
        """
        if content is None:
            raise Exception("Content cannot be null")

        self.__content: str = content
        self.__position: int = -1
        self.__line: int = 1
        self.__column: int = 0

    def __char_at(self, position: int) -> int:
        """
        Returns character from a specified position in the stream

        :param position: a position to read character
        :return: a character from the specified position or EOF (-1)
        """
        if position < 0 or position >= len(self.__content):
            return StringScanner.Eof

        return ord(self.__content[position])

    def is_line(self, char_before: int, char_at: int, char_after: int) -> bool:
        """
        Checks if the current character represents a new line

        :param char_before: the character before the current one
        :param char_at: the current character
        :param char_after: the character after the current one
        :return: **true** if the current character is a new line, or **false** otherwise.
        """
        if char_at != 10 and char_at != 13:
            return False
        if char_at == 13 and (char_before == 10 or char_after == 10):
            return False

        return True

    def is_column(self, char_at: int) -> bool:
        """
        Checks if the current character represents a column

        :param char_at: the current character
        :return: **true** if the current character is a column, or **false** otherwise.
        """
        if char_at == 10 or char_at == 13:
            return False

        return True

    def line(self) -> int:
        """
        Gets the current line number

        :return: The current line number in the stream
        """
        return self.__line

    def column(self) -> int:
        """
        Gets the column in the current line

        :return: The column in the current line in the stream
        """
        return self.__column

    def read(self) -> int:
        """
        Reads character from the top of the stream.
        A read character or **-1** if stream processed to the end.
        """
        # Skip if we are at the end
        if (self.__position + 1) > len(self.__content):
            return StringScanner.Eof

        # Update the current position
        self.__position += 1

        if self.__position >= len(self.__content):
            return StringScanner.Eof

        # Update line and columns
        char_before = self.__char_at(self.__position - 1)
        char_at = self.__char_at(self.__position)
        char_after = self.__char_at(self.__position + 1)

        if self.is_line(char_before, char_at, char_after):
            self.__line += 1
            self.__column = 0

        if self.is_column(char_at):
            self.__column += 1

        return char_at

    def peek(self) -> int:
        """
        Returns the character from the top of the stream without moving the stream pointer.

        :return: A character from the top of the stream or **-1** if stream is empty.
        """
        return self.__char_at(self.__position + 1)

    def peek_line(self) -> int:
        """
        Gets the next character line number

        :return: The next character line number in the stream
        """
        char_before = self.__char_at(self.__position)
        char_at = self.__char_at(self.__position + 1)
        char_after = self.__char_at(self.__position + 2)

        return self.__line + 1 if self.is_line(char_before, char_at, char_after) else self.__line

    def peek_column(self) -> int:
        """
        Gets the next character column number

        :return: The next character column number in the stream
        """
        char_before = self.__char_at(self.__position)
        char_at = self.__char_at(self.__position + 1)
        char_after = self.__char_at(self.__position + 2)

        if self.is_line(char_before, char_at, char_after):
            return 0

        return self.__column + 1 if self.is_column(char_at) else self.__column

    def unread(self):
        """
        Puts the one character back into the stream stream.

        :return: A character to be pushed back.
        """
        # Skip if we are at the beginning
        if self.__position < -1:
            return

        # Update the current position
        self.__position -= 1

        # Update line and columns (optimization)
        if self.__column > 0:
            self.__column -= 1
            return

        # Update line and columns (full version)
        self.__line = 1
        self.__column = 0

        char_before = StringScanner.Eof
        char_at = StringScanner.Eof
        char_after = self.__char_at(0)

        for position in range(self.__position + 1):
            char_before = char_at
            char_at = char_after
            char_after = self.__char_at(position + 1)

            if self.is_line(char_before, char_at, char_after):
                self.__line += 1
                self.__column = 0

            if self.is_column(char_at):
                self.__column += 1

    def unread_many(self, count: int):
        """
        Pushes the specified number of characters to the top of the stream.

        :param count: A number of characters to be pushed back.
        """
        while count > 0:
            self.unread()
            count -= 1

    def reset(self):
        """
        Resets scanner to the initial position
        """
        self.__position = -1
        self.__line = 1
        self.__column = 0
