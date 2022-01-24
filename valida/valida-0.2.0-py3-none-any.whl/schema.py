from pathlib import Path

from ruamel.yaml import YAML

from valida.rules import Rule


class Schema:
    def __init__(self, rules):
        self.rules = rules
        self.rule_tests = None  # Assigned by `self.validate`

    def __len__(self):
        return len(self.rules)

    def __eq__(self, other):
        if (
            type(self) == type(other)
            and self.rules == other.rules
            and self.rule_tests == other.rule_tests
        ):
            return True
        return False

    @staticmethod
    def init_rules(rules_dat):
        rules = []
        for i in rules_dat:
            rule = Rule.from_spec(i)
            rules.append(rule)
        return rules

    @classmethod
    def from_yaml(cls, yaml_str):
        yaml = YAML()
        schema_dat = yaml.load(yaml_str)
        rules = cls.init_rules(schema_dat["rules"])
        return cls(rules)

    @classmethod
    def from_yaml_file(cls, path):
        yaml = YAML(
            typ="safe"
        )  # need Python-native containers e.g. for rules that check container types
        with Path(path).open("r") as fh:
            schema_dat = yaml.load(fh)
        rules = cls.init_rules(schema_dat["rules"])
        return cls(rules)

    def validate(self, data):
        return ValidatedData(self, data)


class ValidatedData:
    def __init__(self, schema, data):
        self.schema = schema
        self.rule_tests = tuple(rule.test(data) for rule in self.schema.rules)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"is_valid={self.is_valid!r}, "
            f"num_failures={self.num_failures}, "
            f"frac_rules_tested={self.frac_rules_tested}"
            f")"
        )

    @property
    def is_valid(self):
        return all(i.is_valid for i in self.rule_tests)

    @property
    def num_rules_tested(self):
        return sum(i.tested for i in self.rule_tests)

    @property
    def frac_rules_tested(self):
        return self.num_rules_tested / len(self.schema)

    @property
    def num_failures(self):
        return sum(i.num_failures for i in self.rule_tests)

    def print_failures(self):

        rules_tested_msg = (
            f"{self.num_rules_tested}/{len(self.schema)} rules were tested."
        )
        if self.is_valid:
            print(f"Data is valid. {rules_tested_msg}")
            return

        print(
            f"{self.num_failures} rule{'s' if self.num_failures > 1 else ''} "
            f"failed validation. {rules_tested_msg}\n"
        )

        for rule_idx, rule_test in enumerate(self.rule_tests, start=1):
            if not rule_test.is_valid:
                rule_msg = f"Rule #{rule_idx}"
                print(rule_msg + "\n" + "-" * len(rule_msg))
                rule_test.print_failures()
                print()


class _TestDataSchema:
    def __init__(self, data, schema):

        rules = Schema.init_rules(schema["rules"])

        self.data = data
        self.schema = Schema(rules)

    @classmethod
    def from_yaml_file(cls, path):
        yaml = YAML(
            typ="safe"
        )  # need Python-native containers e.g. for rules that check container types
        with Path(path).open("r") as fh:
            all_dat = yaml.load(fh)
        test_data_schema = cls(all_dat["data"], all_dat["schema"])
        return test_data_schema

    @property
    def data_and_schema(self):
        return self.data, self.schema
