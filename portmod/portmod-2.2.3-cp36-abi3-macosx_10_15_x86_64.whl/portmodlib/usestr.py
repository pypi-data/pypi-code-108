# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import re
from typing import AbstractSet, Any, Callable, List, Optional, Type

from portmodlib.atom import Atom, InvalidAtom, useflag_re
from portmodlib.l10n import l10n


class UseParserError(Exception):
    """Error indicating a failure to parse a use-conditional string"""


def use_reduce(
    depstr: str,
    uselist: AbstractSet[str] = set(),
    masklist: AbstractSet[str] = set(),
    matchall: bool = False,
    excludeall: AbstractSet[str] = set(),
    is_src_uri: bool = False,
    opconvert: bool = False,
    flat: bool = False,
    is_valid_flag: Optional[Callable[[str], bool]] = None,
    token_class: Optional[Type] = None,
    matchnone: bool = False,
) -> List:
    """
    Takes a dep string and reduces the use? conditionals out, leaving an array
    with subarrays. All redundant brackets are removed.
    Adapted from portage's use_reduce

    args:
        depstr: depstring
        uselist: List of use enabled flags
        masklist: List of masked flags (always treated as disabled)
        param matchall: Treat all conditionals as active. Used by inquisitor.
        excludeall: List of flags for which negated conditionals are always treated
                    as inactive.
        is_src_uri: Indicates if depstr represents a SRC_URI
        opconvert: Put every operator as first element into it's argument list
        flat: Create a flat list of all tokens
        is_valid_flag: Function that decides if a given use flag might be used in
                       use conditionals
        token_class: Convert all non operator tokens into this class
        matchnone: Treat all conditionals as inactive. Used by digestgen().

    returns:
        The use reduced depend array
    """

    if opconvert and flat:
        raise ValueError(
            "portage.dep.use_reduce: 'opconvert' and 'flat' are mutually exclusive"
        )

    if matchall and matchnone:
        raise ValueError(
            "portage.dep.use_reduce: 'matchall' and 'matchnone' are mutually exclusive"
        )

    def is_active(conditional):
        """
        Decides if a given use conditional is active.
        """
        if conditional.startswith("!"):
            flag = conditional[1:-1]
            is_negated = True
        else:
            flag = conditional[:-1]
            is_negated = False

        if is_valid_flag:
            if not is_valid_flag(flag):
                msg = (
                    "USE flag '{}' referenced in conditional '{}' "
                    "is not in IUSE".format(flag, conditional)
                )
                raise UseParserError(msg)
        else:
            if useflag_re.match(flag) is None:
                raise UseParserError(
                    "invalid use flag '{}' in conditional '{}'".format(
                        flag, conditional
                    )
                )

        if is_negated and flag in excludeall:
            return False

        if flag in masklist:
            return is_negated

        if matchall:
            return True

        if matchnone:
            return False

        return (flag in uselist and not is_negated) or (
            flag not in uselist and is_negated
        )

    def missing_white_space_check(token, pos):
        """
        Used to generate good error messages for invalid tokens.
        """
        for x in (")", "(", "||"):
            if token.startswith(x) or token.endswith(x):
                raise UseParserError(
                    "missing whitespace around '%s' at '%s', token %s"
                    % (x, token, pos + 1)
                )

    mysplit = depstr.split()
    # Count the bracket level.
    level = 0
    # We parse into a stack.
    # Every time we hit a '(', a new empty list is appended to the stack.
    # When we hit a ')', the last list in the stack is merged with list one level up.
    stack: List[List[Any]] = [[]]
    # Set need_bracket to True after use conditionals or ||. Other tokens need to ensure
    # that need_bracket is not True.
    need_bracket = False
    # Set need_simple_token to True after a SRC_URI arrow. Other tokens need to ensure
    # that need_simple_token is not True.
    need_simple_token = False

    for pos, token in enumerate(mysplit):
        if token == "(":
            if need_simple_token:
                raise UseParserError(
                    "expected: file name, got: '%s', token %s" % (token, pos + 1)
                )
            if len(mysplit) >= pos + 2 and mysplit[pos + 1] == ")":
                raise UseParserError(
                    "expected: dependency string, got: ')', token %s" % (pos + 1,)
                )
            need_bracket = False
            stack.append([])
            level += 1
        elif token == ")":
            if need_bracket:
                raise UseParserError(
                    "expected: '(', got: '%s', token %s" % (token, pos + 1)
                )
            if need_simple_token:
                raise UseParserError(
                    "expected: file name, got: '%s', token %s" % (token, pos + 1)
                )
            if level > 0:
                level -= 1
                ll = stack.pop()

                is_single = (
                    len(ll) == 1
                    or (opconvert and ll and ll[0] == "||")
                    or (not opconvert and len(ll) == 2 and ll[0] == "||")
                )
                ignore = False

                if flat:
                    # In 'flat' mode, we simply merge all lists into a single large one.
                    if stack[level] and stack[level][-1][-1] == "?":
                        # The last token before the '(' that matches the current ')'
                        # was a use conditional. The conditional is removed in any case.
                        # Merge the current list if needed.
                        if is_active(stack[level][-1]):
                            stack[level].pop()
                            stack[level].extend(ll)
                        else:
                            stack[level].pop()
                    else:
                        stack[level].extend(ll)
                    continue

                if stack[level] and isinstance(stack[level][-1], str):
                    if stack[level][-1] == "||" and not ll:
                        # Optimize: || ( ) -> .
                        ll.append((token_class or str)("empty-any-of"))
                        stack[level].pop()
                    elif stack[level][-1][-1] == "?":
                        # The last token before the '(' that matches the current ')'
                        # was a use conditional, remove it and decide if we
                        # have to keep the current list.
                        if not is_active(stack[level][-1]):
                            ignore = True
                        stack[level].pop()

                def ends_in_any_of_dep(k):
                    return k >= 0 and stack[k] and stack[k][-1] == "||"

                def last_any_of_operator_level(k):
                    # Returns the level of the last || operator if it is in effect for
                    # the current level. It is not in effect, if there is a level, that
                    # ends in a non-operator. This is almost equivalent to
                    # stack[level][-1]=="||", expect that it skips empty levels.
                    while k >= 0:
                        if stack[k] and isinstance(stack[k][-1], str):
                            if stack[k][-1] == "||":
                                return k
                            elif stack[k][-1][-1] != "?":
                                return -1
                        k -= 1
                    return -1

                def special_append():
                    """
                    Use extend instead of append if possible.
                    This kills all redundant brackets.
                    """
                    if is_single:
                        # Either [A], [[...]] or [|| [...]]
                        if ll[0] == "||" and ends_in_any_of_dep(level - 1):
                            if opconvert:
                                stack[level].extend(ll[1:])
                            else:
                                stack[level].extend(ll[1])
                        elif len(ll) == 1 and isinstance(ll[0], list):
                            # l = [[...]]
                            last = last_any_of_operator_level(level - 1)
                            if last == -1:
                                if (
                                    opconvert
                                    and isinstance(ll[0], list)
                                    and ll[0]
                                    and ll[0][0] == "||"
                                ):
                                    stack[level].append(ll[0])
                                else:
                                    stack[level].extend(ll[0])
                            else:
                                if opconvert and ll[0] and ll[0][0] == "||":
                                    stack[level].extend(ll[0][1:])
                                else:
                                    stack[level].append(ll[0])
                        else:
                            stack[level].extend(ll)
                    else:
                        if opconvert and stack[level] and stack[level][-1] == "||":
                            stack[level][-1] = ["||"] + ll
                        else:
                            stack[level].append(ll)

                if ll and not ignore:
                    # The current list is not empty and we don't want to ignore it
                    # because of an inactive use conditional.
                    if not ends_in_any_of_dep(level - 1) and not ends_in_any_of_dep(
                        level
                    ):
                        # Optimize: ( ( ... ) ) -> ( ... ).
                        # Make sure there is no '||' hanging around.
                        stack[level].extend(ll)
                    elif not stack[level]:
                        # An '||' in the level above forces us to keep to brackets.
                        special_append()
                    elif is_single and ends_in_any_of_dep(level):
                        # Optimize: || ( A ) -> A,  || ( || ( ... ) ) -> || ( ... )
                        stack[level].pop()
                        special_append()
                    elif ends_in_any_of_dep(level) and ends_in_any_of_dep(level - 1):
                        # Optimize: || ( A || ( B C ) ) -> || ( A B C )
                        stack[level].pop()
                        stack[level].extend(ll)
                    else:
                        if opconvert and ends_in_any_of_dep(level):
                            # In opconvert mode, we have to move the operator from the
                            # level above into the current list.
                            stack[level].pop()
                            stack[level].append(["||"] + ll)
                        else:
                            special_append()

            else:
                raise UseParserError(
                    "no matching '%s' for '%s', token %s" % ("(", ")", pos + 1)
                )
        elif token == "||":
            if is_src_uri:
                raise UseParserError(
                    "any-of dependencies are not allowed in SRC_URI: token %s"
                    % (pos + 1,)
                )
            if need_bracket:
                raise UseParserError(
                    "expected: '(', got: '%s', token %s" % (token, pos + 1)
                )
            need_bracket = True
            stack[level].append(token)
        elif token == "->":
            if need_simple_token:
                raise UseParserError(
                    "expected: file name, got: '%s', token %s" % (token, pos + 1)
                )
            if not is_src_uri:
                raise UseParserError(
                    "SRC_URI arrow are only allowed in SRC_URI: token %s" % (pos + 1,)
                )
            need_simple_token = True
            stack[level].append(token)
        else:
            if need_bracket:
                raise UseParserError(
                    "expected: '(', got: '%s', token %s" % (token, pos + 1)
                )

            if need_simple_token and "/" in token:
                # The last token was a SRC_URI arrow,
                # make sure we have a simple file name.
                raise UseParserError(
                    "expected: file name, got: '%s', token %s" % (token, pos + 1)
                )

            if token[-1] == "?":
                need_bracket = True
            else:
                need_simple_token = False
                if token_class and not is_src_uri:
                    # Add a hack for SRC_URI here, to avoid conditional code at the
                    # consumer level
                    try:
                        token = token_class(token)
                    except InvalidAtom as e:
                        missing_white_space_check(token, pos)
                        raise UseParserError(
                            "Invalid atom (%s), token %s" % (e, pos + 1)
                        )
                    except SystemExit:
                        raise
                    except UseParserError:
                        missing_white_space_check(token, pos)
                        raise UseParserError(
                            "Invalid token '%s', token %s" % (token, pos + 1)
                        )

                    if not matchall and isinstance(token, Atom):
                        token = token.evaluate_conditionals(uselist)

            stack[level].append(token)

    if level != 0:
        raise UseParserError("Missing '%s' at end of string" % (")",))

    if need_bracket:
        raise UseParserError("Missing '%s' at end of string" % ("(",))

    if need_simple_token:
        raise UseParserError("Missing file name at end of string")

    return stack[0]


def check_required_use(
    required_use: str, use: AbstractSet[str], iuse_match: Callable[[str], bool]
) -> bool:
    """
    Adapted from portage's check_required_use
    Checks if the use flags listed in 'use' satisfy all
    constraints specified in 'constraints'.

    args:
        required_use: REQUIRED_USE string
        use: Enabled use flags
        iuse_match: Callable that takes a single flag argument and returns
            True if the flag is matched, false otherwise,
    returns:
        Indicates if REQUIRED_USE constraints are satisfied
    """

    valid_operators = ("||", "^^", "??")

    def is_active(token):
        if token.startswith("!"):
            flag = token[1:]
            is_negated = True
        else:
            flag = token
            is_negated = False

        if not flag or not iuse_match(flag):
            raise UseParserError("USE flag '%s' is not in IUSE" % (flag,))

        return (flag in use and not is_negated) or (flag not in use and is_negated)

    def is_satisfied(operator, argument):
        if operator == "||":
            return True in argument
        elif operator == "^^":
            return argument.count(True) == 1
        elif operator == "??":
            return argument.count(True) <= 1
        elif operator[-1] == "?":
            return False not in argument

    mysplit = required_use.split()
    level = 0
    stack: List[List[str]] = [[]]
    need_bracket = False

    for token in mysplit:
        if token == "(":
            need_bracket = False
            stack.append([])
            level += 1
        elif token == ")":
            if need_bracket:
                raise UseParserError("malformed syntax: '%s'" % required_use)
            if level > 0:
                level -= 1
                ll = stack.pop()
                op = None
                if stack[level]:
                    if stack[level][-1] in valid_operators:
                        op = stack[level].pop()
                        satisfied = is_satisfied(op, ll)
                        stack[level].append(satisfied)

                    elif (
                        not isinstance(stack[level][-1], bool)
                        and stack[level][-1][-1] == "?"
                    ):
                        op = stack[level].pop()
                        if is_active(op[:-1]):
                            satisfied = is_satisfied(op, ll)
                            stack[level].append(satisfied)
                        else:
                            continue

                if op is None:
                    satisfied = False not in ll
                    if ll:
                        stack[level].append(satisfied)
            else:
                raise UseParserError("malformed syntax: '%s'" % required_use)
        elif token in valid_operators:
            if need_bracket:
                raise UseParserError("malformed syntax: '%s'" % required_use)
            need_bracket = True
            stack[level].append(token)
        else:
            if need_bracket:
                raise UseParserError("malformed syntax: '%s'" % required_use)

            if token[-1] == "?":
                need_bracket = True
                stack[level].append(token)
            else:
                satisfied = is_active(token)
                stack[level].append(satisfied)

    if level != 0 or need_bracket:
        raise UseParserError("malformed syntax: '%s'" % required_use)

    return False not in stack[0]


def parse_usestr(usestr: str, token_class: Type = str):
    """
    Adapted from portage's check_required_use
    Converts usestring into structure containing lists of tokens,
    possibly preceeded by an operator that can be one of || ?? ^^ or a use conditional
    """

    valid_operators = ("||", "^^", "??")

    mysplit = usestr.split()
    level = 0
    stack: List[List[Any]] = [[]]
    need_bracket = False

    for token in mysplit:
        if token == "(":
            need_bracket = False
            stack.append([])
            level += 1
        elif token == ")":
            if need_bracket:
                raise UseParserError(f"malformed syntax: '{usestr}'")
            if level > 0:
                level -= 1
                ll = stack.pop()
                stack[level].append(ll)
            else:
                raise UseParserError(f"malformed syntax: '{usestr}'")
        elif token in valid_operators:
            if need_bracket:
                raise UseParserError(f"malformed syntax: '{usestr}'")
            need_bracket = True
            stack[level].append(token)
        else:
            if need_bracket:
                raise UseParserError(f"malformed syntax: '{usestr}'")

            if token[-1] == "?":
                need_bracket = True
                stack[level].append(token)
            else:
                stack[level].append(token_class(token))

    if level != 0 or need_bracket:
        raise UseParserError(f"malformed syntax: '{usestr}'")

    def opconvert(tokenlist):
        index = 0
        while index < len(tokenlist):
            token = tokenlist[index]
            if (
                token in valid_operators
                or isinstance(token, str)
                and token.endswith("?")
            ):
                tokenlist[index] = [token] + opconvert(tokenlist[index + 1])
                del tokenlist[index + 1]
            index += 1
        return tokenlist

    # Nested ||, ^^, and ?? groups can be combined
    # use-conditionals cannot (tokens ending in ?)
    def flatten(parent):
        index = 0
        while index < len(parent):
            token = parent[index]
            if isinstance(token, list):
                token = flatten(token)
                if token[0] in valid_operators and token[0] == parent[0]:
                    parent += token[1:]
                    del parent[index]
                    index -= 1
                elif (
                    token[0] not in valid_operators
                    and parent[0] not in valid_operators
                    and not token[0].endswith("?")
                ):
                    parent += token
                    del parent[index]
                    index -= 1
            index += 1
        return parent

    return flatten(opconvert(stack[0]))


def human_readable_required_use(required_use: List[Any]) -> str:
    """Takes a (recursive) list of tokens and turns it into a readable string"""
    if isinstance(required_use[0], list):
        string = "( " + human_readable_required_use(required_use[0]) + " )"
    else:
        string = required_use[0]

    for token in required_use[1:]:
        if isinstance(token, list):
            string += " ( " + human_readable_required_use(token) + " )"
        else:
            string += " " + token
    return re.sub(
        r"\( (\!?\w+\?)",  # Move use-conditionals in front of brackets
        r"\1 (",
        string.replace("( ^^", l10n("exactly-one-of") + " (")
        .replace("( ||", l10n("any-of") + " (")
        .replace("( ??", l10n("at-most-one-of") + " ("),
    )
