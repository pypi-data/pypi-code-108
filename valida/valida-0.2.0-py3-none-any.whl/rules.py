from valida.conditions import ConditionLike
from valida.data import Data
from valida.datapath import DataPath


class Rule:
    def __init__(self, path, condition):

        if not isinstance(path, DataPath):
            path = DataPath(*path)

        self.path = path
        self.condition = condition

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"path={self.path!r}, condition={self.condition!r}"
            f")"
        )

    def __eq__(self, other):
        if type(other) == type(self):
            if other.path == self.path and other.condition == self.condition:
                return True
        return False

    @classmethod
    def from_spec(cls, spec):
        path = DataPath.from_part_specs(*spec["path"])
        cond = ConditionLike.from_spec(spec["condition"])
        return cls(path=path, condition=cond)

    def test(self, data):
        return RuleTest(self, data)


class RuleTestFailureItem:
    def __init__(self, rule_test, index, value, path, reasons):

        self.rule_test = rule_test
        self.index = index
        self.value = value
        self.path = path
        self.reasons = reasons

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"value={self.value!r}, path={self.path!r}), reasons={self.reasons!r}"
            f")"
        )


class RuleTest:
    def __init__(self, rule, data):

        if not isinstance(data, Data):
            data = Data(data)

        self.rule = rule
        self.data = data

        self._tested = False  # assigned by `_test()` - True if the rule path existed
        self._is_valid = None  # assigned by `_test()`
        self._failures = None  # assigned by `_test()`

        self._test()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"is_valid={self.is_valid!r}, num_failures={self.num_failures!r}"
            f")"
        )

    def __eq__(self, other):
        if type(other) == type(self):
            if other.rule == self.rule and other.data is self.data:
                return True
        return False

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def tested(self):
        return self._tested

    @property
    def num_failures(self):
        return len(self.failures)

    @property
    def failures(self):
        return self._failures

    def print_failures(self):
        if not self.failures:
            print("Rule test is valid.")
        for fail in self.failures:
            print(f"Path: {fail.path!r}\nValue: {fail.value!r}\nReasons:")
            for reason in fail.reasons:
                print(" " + reason)

    def _test(self):

        sub_data = self.rule.path.get_data(self.data, return_paths=True)
        path_exists = sub_data not in [None, []]

        if self.rule.path.is_concrete:
            sub_data = [sub_data]

        self.sub_data = sub_data

        failures = []
        if path_exists:
            filtered_data = self.rule.condition.filter(
                sub_data,
                data_has_paths=True,
                source_data=self.data,
            )
            if all(filtered_data.result):
                self._is_valid = True

            else:
                self._is_valid = False
                for f_item in filtered_data:
                    if not f_item.result:
                        failure_item = RuleTestFailureItem(
                            rule_test=self,
                            index=f_item.index,
                            value=f_item.source,
                            path=f_item.concrete_path,
                            reasons=f_item.get_failure(),
                        )
                        failures.append(failure_item)

            self.filter = filtered_data
            self._tested = True

        else:
            self._is_valid = True
            self._tested = False
            self.filter = None

        self._failures = tuple(failures)
