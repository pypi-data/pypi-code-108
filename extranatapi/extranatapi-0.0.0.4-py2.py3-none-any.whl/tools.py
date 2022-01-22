# -*- coding: utf-8 -*-
"""Tools package."""


class Tools():
    """Class : Tools"""

    @staticmethod
    def convertnage(text):
        """Convert nage."""
        text = text.replace(' Dames', '')
        text = text.replace(' Messieurs', '')
        text = text.replace('Nage Libre', 'NL')
        text = text.replace('Brasse', 'Bra.')
        text = text.replace('Papillon', 'Pap.')
        text = text.replace('4 Nages', '4 N.')

        return text

    @staticmethod
    def age_to_category(age):  # pylint: disable=too-many-branches
        """Convert age to category."""
        result = None
        age = int(age)

        if age < 25:
            result = 'C0'
        elif age <= 29:
            result = 'C1'
        elif age <= 34:
            result = 'C2'
        elif age <= 39:
            result = 'C3'
        elif age <= 44:
            result = 'C4'
        elif age <= 49:
            result = 'C5'
        elif age <= 54:
            result = 'C6'
        elif age <= 59:
            result = 'C7'
        elif age <= 64:
            result = 'C8'
        elif age <= 69:
            result = 'C9'
        elif age <= 74:
            result = 'C10'
        elif age <= 79:
            result = 'C11'
        elif age <= 84:
            result = 'C12'
        elif age <= 89:
            result = 'C13'
        elif age <= 94:
            result = 'C14'
        elif age <= 99:
            result = 'C15'
        else:
            result = 'C16'

        return result
