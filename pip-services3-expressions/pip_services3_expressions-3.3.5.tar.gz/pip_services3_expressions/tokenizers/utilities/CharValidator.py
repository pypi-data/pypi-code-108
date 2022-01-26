# -*- coding: utf-8 -*-

class CharValidator:
    Eof: int = 0xffff
    Zero: int = ord('0')
    Nine: int = ord('9')

    @staticmethod
    def is_eof(value: int) -> bool:
        return value == CharValidator.Eof or value == -1

    @staticmethod
    def is_eol(value: int) -> bool:
        return value == 10 or value == 13

    @staticmethod
    def is_digit(value: int) -> bool:
        return CharValidator.Zero <= value <= CharValidator.Nine
