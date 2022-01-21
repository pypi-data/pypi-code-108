#!/usr/bin/env python3
from behave.matchers import ParseMatcher
from behave.model_core import Argument

__author__ = """Filip Pokryvka <fpokryvk@redhat.com>"""

"""
Definition of "qecore" matcher.
This matcher splits decorators by '|' to allow all combinations in one line

USAGE::

    from qecore.step_matcher import use_step_matcher
    use_step_matcher("qecore")

    ... # definiton of steps

    use_step_matcher("parse") # stop using qecore matcher
"""

def use_step_matcher(matcher_name):
    """
    Overrides `behave.matchers.use_step_matcher()` function.
    Appends "qecore" matcher to behave matchers and selects matcher to be used.

    :type matcher_name: str
    :param matcher_name: name of behave matcher to be used
    """

    from behave.matchers import matcher_mapping
    from behave.matchers import use_step_matcher as usm
    matcher_mapping["qecore"] = QecoreMatcher
    usm(matcher_name)


class QecoreMatcher(ParseMatcher):
    """
    Uses :class:`~ParseMatcher` with additional '|' parsing
    """

    delimiter = "|"
    """
    Split delimiter (default "|").

    :type delimiter: str
    """

    start_phrase = "#__start__#"
    """
    Used internaly to match beginning of the step.

    :type start_phrase: str
    """

    def __init__(self, func, pattern, step_type=None):
        """
        Initiate :class:`~QecoreMatcher` instance.
        Split pattern by delimiter (default "|").
        Called by behave.

        :type func: <function>
        :param func: Step function.

        :type pattern: str
        :param pattern: Decorator of step function.

        :type step_type: str
        :param step_type: Type of behave step.
        """
        super(QecoreMatcher, self).__init__(func, pattern, step_type)
        # Note the space at the end of patterns (to make sure whole words are matched).
        self.patterns = [f"{self.start_phrase}{p.strip()} " for p in pattern.split(self.delimiter)]
        self.parsers = {}
        for patt in self.patterns:
            self.parsers[patt] = self.parser_class(patt, self.custom_types)


    def check_match(self, step):
        """
        Check if step matches definition and also for duplicit step definitions.
        Called by behave.

        :type step: str
        :param step: Step definiton to be matched

        :return: List of matched arguments if `step` matches, `None` otherwise.
        """

        args = []
        # Escaped quotes and append space (because patterns end with space).
        step_suffix = self.start_phrase + step.replace('\\"', "''") + " "
        # To calculate positions in step argument - used for keword highlights.
        offset = - len(self.start_phrase)


        def fix_escape_quotes(value, text_repr):
            """
            Replace two consecutive single qoutes ('') back to double quote.
            Do not escape double quotes.

            :type value: <any>
            :param value: If instance of str fix quotes.

            :type text_repr: str
            :param text_repr: Text represenation of parameter value.

            :return: Tuple of fixed value and text_repr.
            """

            if isinstance(value, str):
                value = value.replace("''", '"')
            text_repr = text_repr.replace("''", '"')
            return value, text_repr


        def process_result(step_suffix, offset, args, result, pattern):
            """
            Convert parse results into behave arguments.

            :type step_suffix: str
            :param step_suffix: Current prefix of step.

            :type offset: int
            :param offset: Current offset (length of already parsed step prefix).

            :type args: list
            :param args: List of already parsed <Argument>s.

            :type result: <parse.Result>
            :param result: Result of current match.

            :type pattern: str
            :param pattern: Currently matched pattern.

            :return: Tuple of updated step_suffix, offset, args.
            """

            for index, value in enumerate(result.fixed):
                start, end = result.spans[index]
                value, text_repr = fix_escape_quotes(value, step_suffix[start:end])
                args.append(Argument(start+offset, end+offset, text_repr, value))
            for name, value in result.named.items():
                start, end = result.spans[name]
                value, text_repr = fix_escape_quotes(value, step_suffix[start:end])
                args.append(Argument(start+offset, end+offset, text_repr, value, name))
            # Matched part of the step.
            pattern_filled = pattern.format_map(result.named)
            # Remove matched part and append start_phrase.
            old_len = len(step_suffix)
            step_suffix = self.start_phrase + step_suffix.replace(pattern_filled, "").lstrip(" |")
            new_len = len(step_suffix)
            # Calculate offset.
            offset += old_len - new_len
            return (step_suffix, offset, args)

        # Check that the first part is first, finish if step does not match.
        pattern = self.patterns[0]
        if len(self.patterns) == 1:
            result = self.parsers[pattern].parse(step_suffix)
        else:
            result = self.parsers[pattern].search(step_suffix)

        if result is None:
            return None
        step_suffix, offset, args = process_result(step_suffix, offset, args, result, pattern)

        # Match rest of the step.
        patterns = self.patterns[1:]
        while len(step_suffix) > len(self.start_phrase):
            found = False
            for pattern in patterns:
                result = self.parsers[pattern].search(step_suffix)
                if result is None:
                    continue
                # Remove pattern as it was used.
                patterns.remove(pattern)
                step_suffix, offset, args = process_result(step_suffix, offset,
                                                           args, result, pattern)
                found = True
            if not found:
                return None

        args.sort(key=lambda x: x.start)
        return args
