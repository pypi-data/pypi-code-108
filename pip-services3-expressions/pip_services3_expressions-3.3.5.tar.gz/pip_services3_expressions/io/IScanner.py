# -*- coding: utf-8 -*-

from abc import ABC


class IScanner(ABC):
    """
    Defines scanner that can read and unread characters and count lines.
    This scanner is used by tokenizers to process input streams.
    """

    def read(self) -> int:
        """
        Reads character from the top of the stream.

        :return: A read character or **-1** if stream processed to the end.
        """

    def line(self) -> int:
        """
        Gets the current line number

        :return: The current line number in the stream
        """

    def column(self) -> int:
        """
        Gets the column in the current line

        :return: The column in the current line in the stream
        """

    def peek(self) -> int:
        """
        Returns the character from the top of the stream without moving the stream pointer.

        :return: A character from the top of the stream or **-1** if stream is empty.
        """

    def peek_line(self) -> int:
        """
        Gets the next character line number

        :return: The next character line number in the stream
        """

    def peek_column(self) -> int:
        """
        Gets the next character column number

        :return: The next character column number in the stream
        """

    def unread(self):
        """
        Puts the one character back into the stream stream.

        :return: A character to be pushed back.
        """

    def unread_many(self, count: int):
        """
        Pushes the specified number of characters to the top of the stream.

        :param count: A number of characters to be pushed back.
        """

    def reset(self):
        """
        Resets scanner to the initial position
        """
