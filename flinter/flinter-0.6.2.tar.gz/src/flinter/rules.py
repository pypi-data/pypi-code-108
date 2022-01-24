"""Module containing base functions to lint and dectect broken formatting rules.
"""

import re
import os
import warnings

from flinter.utils import load_default_rules
from flinter.utils import load_rule


class RuleSets:
    def __init__(self):
        self.sets = []

    def add(self, rules):
        self.sets.insert(0, rules)

    def get_from_ext(self, ext):
        for rules in self.sets:
            if re.fullmatch(rules["extension"], ext, re.I):
                return rules
        return None

    def get_from_fname(self, fname):
        return self.get_from_ext(os.path.splitext(fname)[-1][1:])

    def is_ext_available(self, ext):
        for rules in self.sets:
            if re.fullmatch(rules["extension"], ext, re.I):
                return True

        return False


def init_languages_specs(user_rc_list=None):
    """Load format rules from resources.
    """

    if user_rc_list is None:
        user_rc_list = ()

    # collect rules
    all_rules = load_default_rules()

    for user_rc in user_rc_list:
        name = os.path.split(user_rc)[-1]
        all_rules[name] = load_rule(user_rc)

    # create rule sets
    rule_sets = RuleSets()
    for name, rules in all_rules.items():
        rule_sets.add(_init_format_rules(rules, name=name))

    return rule_sets


def _init_format_rules(rules, name=None):

    extension = rules.get("extension", r"f\d\d")

    # create syntax reference
    syntax = rules.get("fortran-syntax") or rules["syntax"]
    if "fortran-syntax" in rules:
        warnings.warn("Deprecated use of \"fortran-syntax\" , use the more generic \"syntax\" qualifier")
    if "extension" not in rules:
        warnings.warn("Rule file with no extension field default to fortran, prefer explicitely specifying one")
    if "namespace_blocks" not in syntax or "context_blocks" not in syntax:
        if "blocks" in syntax:
            warnings.warn("Deprecated use of \"blocks\" in syntax, use instead \"namespace_blocks\" and \"context_blocks\"")
        else:
            warnings.warn("\"namespace_blocks\" and \"context_blocks\" are not defined in the syntax")
        syntax["namespace_blocks"] = ["program", "module"]
        syntax["context_blocks"] = ["subroutine", "function"]
    else:
        syntax["blocks"] = syntax.get("blocks", []) + syntax["namespace_blocks"] + syntax["context_blocks"]
    syntax.setdefault("ignore_blocks", [])

    # create syntax copy for regular expression replacement
    syntax_re = dict()
    for key, value in syntax.items():
        syntax_re[key] = r"|".join(value).lower()
        syntax_re[key + "_upper"] = syntax_re[key].upper()
        syntax_re[key + "_lower"] = syntax_re[key].lower()

    # select active rules
    # compile the rules
    regexp_rules = dict()
    default_rule = {
        "replacement": None,
        "active": True,
        "include-comments": False,
        "case-sensitive": False,
    }
    for rule_name, rule in rules["regexp-rules"].items():
        for key, value in default_rule.items():
            rule.setdefault(key, value)
        if rule["active"]:
            regexp_rules[rule_name] = _compile_format_rule(rule, syntax_re)

    struct_rules = rules["structure-rules"]
    if "var-declaration" not in struct_rules:
        warnings.warn("\"var-declaration\" is not defined in the rules")
        struct_rules["var-declaration"] = r"(?:{types}|{types_upper})\s*(?:\(.*\))?\s*(?:::| )\s*(\w+(?:\s*,\s*\w+)*)"
    for key, value in struct_rules.items():
        if isinstance(value, str):
            struct_rules[key] = re.compile(value.format(**syntax_re), re.I)

    out = {
        "syntax": syntax,
        "regexp-rules": regexp_rules,
        "struct-rules": struct_rules,
        "extension": extension,
    }

    # TODO: is it required?
    if name is not None:
        out["name"] = name

    return out


def _compile_format_rule(rule, syntax):
    """Compile the regexp action for a rule
    :param rule: dict
        - message
        - regexp
        - replacement
        the rules to be implemented
        some rules a based upon lists stored in syntax
    :param syntax: dict
        - types
        - operators
        - structs
        - punctuation
        language specific lists of items

    """
    if rule["message"] is not None:
        rule["message"] = rule["message"].format(**syntax)
    else:
        rule["message"] = None

    flags = 0
    if not rule["case-sensitive"]:
        flags |= re.I
    rule["regexp"] = re.compile(rule["regexp"].format(**syntax), flags)

    return rule
