# -*- coding: utf-8 -*-


class TokenizerFixture:
    """
    Implements test utilities to Tokenzier tests
    """

    @staticmethod
    def assert_are_equals_token_lists(expected_tokens, actual_tokens):
        """
        Checks is expected tokens matches actual tokens.
        :param expected_tokens: An array with expected tokens.
        :param actual_tokens: An array with actual tokens.
        """
        assert len(expected_tokens) == len(actual_tokens)

        for i in range(len(expected_tokens)):
            assert expected_tokens[i].type == actual_tokens[i].type
            assert expected_tokens[i].value == actual_tokens[i].value
