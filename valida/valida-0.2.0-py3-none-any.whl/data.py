import operator

import valida.datapath


class Data:
    def __init__(self, data):

        if not isinstance(data, (list, dict)) or not data:
            raise TypeError(f"Data is not filterable: {data!r}.")

        try:
            keys, values = zip(*data.items())
            is_list = False
        except AttributeError:
            keys, values = range(len(data)), data
            is_list = True

        self._keys = keys
        self._values = values
        self._is_list = is_list

    def __len__(self):
        return len(self.keys())

    def __eq__(self, other):
        if not isinstance(other, Data):
            return False
        if self.is_list != other.is_list:
            return False
        if self.keys() != other.keys():
            return False
        if self.values() != other.values():
            return False
        return True

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(keys={self.keys()!r}, values={self.values()!r})"
        )

    def __iter__(self):
        for idx in range(len(self)):
            yield self.keys()[idx]

    def __getitem__(self, idx):
        # Note we always expect a values *index* regardless of `self.is_list`
        return self.values()[idx]

    def extract_paths(self):
        values, concrete_paths = list(zip(*self.values()))
        self._values = list(values)
        return concrete_paths

    @property
    def original(self):
        if self.is_list:
            return self.values()
        else:
            return {i: j for i, j in zip(self.keys(), self.values())}

    @property
    def is_list(self):
        return self._is_list

    def keys(self):
        return self._keys

    def values(self):
        return self._values

    def items(self):
        return iter(zip(self.keys(), self.values()))

    def filter(self, condition_like):
        return condition_like.filter(self)

    def get(self, *path_parts, return_paths=False):
        """Get a subset of data from this data.

        Parameters
        ----------
        path_parts : DataPath or tuple of path parts

        Examples
        --------

        For "concrete paths" whose parts are dict keys or list indices, a single
        value is returned:

        >>> data = Data({'a': {'b': [1, 2.5, 3]}})
        >>> data.get('a')
        >>> {'b', [1, 2.5, 3]}

        >>> data.get('a', 'b')
        >>> [1, 2.5, 3]

        >>> data.get('a', 'b', 1)
        >>> 2.5

        For "non-concrete paths" whose parts include `MapValue` and `ListValue`
        objects, a dict or list of values is returned:

        >>> data_path = DataPath(MapValue('a'), 'b')
        >>> data.get(data_path)
        >>> [[1, 2.5, 3]]

        >>> data_path = DataPath('a', 'b', ListValue(value=Value.equal_to(1)))
        >>> data.get(data_path)
        >>> [1]

        >>> data_path = DataPath('a', 'b', ListValue(index=Index.in_([1, 2])))
        >>> data.get(data_path)
        >>> [2.5, 3]

        """
        if not path_parts:
            data_path = valida.datapath.DataPath()
        elif isinstance(path_parts[0], valida.datapath.DataPath):
            data_path = path_parts[0]
        else:
            data_path = valida.datapath.DataPath(*path_parts)

        return data_path.get_data(self, return_paths=return_paths)


class FilteredDataLike:
    @property
    def data(self):
        return [i for idx, i in enumerate(self.source.values()) if self.result[idx]]

    @property
    def keys(self):
        """These are list indices for the case of a list-like data."""
        return [k for idx, k in enumerate(self.source.keys()) if self.result[idx]]

    def __iter__(self):
        for idx, _ in enumerate(self.result):
            yield FilteredDataItem(self, idx)

    def __getitem__(self, index):
        return FilteredDataItem(self, index)

    def __and__(self, other):
        return FilteredDataAnd(self, other)

    def __or__(self, other):
        return FilteredDataOr(self, other)

    def __xor__(self, other):
        return FilteredDataXor(self, other)

    @property
    def failure_indices(self):
        return [idx for idx, i in enumerate(self.result) if not i]

    def get_all_failures(self):
        failures = []
        for fail_idx in self.failure_indices:
            failures.append(self.get_failure_by_index(fail_idx))
        return failures

    def get_failure_by_index(self, idx):

        if self.result[idx]:
            return None

        else:

            truth_table_error_messages = (
                (
                    self.truth_table_pre_processor_error,
                    "Condition pre-processor raised an exception: `{}`.",
                ),
                (
                    self.truth_table_callable_error,
                    "Condition callable raised an exception: `{}`.",
                ),
                (
                    self.truth_table_callable_false,
                    "Condition callable returned False: `{}`.",
                ),
            )

            failure = []
            for cnd_idx, (cnd_name, _) in enumerate(self.truth_table):

                if cnd_name in ("and", "or"):
                    # xor condition returns False if both child conditions are True
                    continue

                for truth_table, err_msg in truth_table_error_messages:
                    if truth_table[cnd_idx][1][idx]:
                        failure.append(err_msg.format(cnd_name))
                        break

        return tuple(failure)


class FilteredData(FilteredDataLike):
    def __init__(
        self,
        condition,
        source: Data,
        processed,
        pre_processor_error,
        callable_error,
        callable_false,
        data_has_paths=False,
    ):

        self.condition = condition
        self.processed = processed

        self.pre_processor_error = pre_processor_error
        self.callable_error = callable_error
        self.callable_false = callable_false

        self.result = [
            False if i else (False if j else (False if k else True))
            for i, j, k in zip(
                self.pre_processor_error, self.callable_error, self.callable_false
            )
        ]

        self.concrete_paths = None
        self.source = source

        if data_has_paths:
            self.concrete_paths = self.source.extract_paths()

    def __eq__(self, other):
        if type(self) == type(other):
            if self.condition == other.condition:
                if self.source == other.source:
                    return True
        return False

    def _get_truth_table(self, attribute):
        return [(repr(self.condition), getattr(self, attribute))]

    @property
    def truth_table(self):
        return self.truth_table_result

    @property
    def truth_table_result(self):
        return self._get_truth_table("result")

    @property
    def truth_table_pre_processor_error(self):
        return self._get_truth_table("pre_processor_error")

    @property
    def truth_table_callable_error(self):
        return self._get_truth_table("callable_error")

    @property
    def truth_table_callable_false(self):
        return self._get_truth_table("callable_false")


class FilteredDataItem:
    def __init__(self, filtered_data_like, index):
        self.filtered_data_like = filtered_data_like
        self.index = index

        self.source = self.filtered_data_like.source[self.index]
        self.result = self.filtered_data_like.result[self.index]
        self.concrete_path = self.filtered_data_like.concrete_paths[self.index]

    def get_failure(self):
        return self.filtered_data_like.get_failure_by_index(self.index)


class FilteredDataBinaryOp(FilteredDataLike):
    def __init__(self, fd1, fd2, binary_op):

        if fd1.source is not fd2.source:
            raise RuntimeError(
                f"The two Data `source` objects in a `{self.__class__.__name__}` must be "
                f"the same object."
            )

        self.source = fd1.source
        self.children = [fd1, fd2]
        self.result = [binary_op(i, j) for i, j in zip(fd1.result, fd2.result)]
        self.concrete_paths = fd1.concrete_paths

        self.pre_processor_error = [
            any((i, j))
            for i, j in zip(fd1.pre_processor_error, fd2.pre_processor_error)
        ]
        self.callable_error = [
            any((i, j)) for i, j in zip(fd1.callable_error, fd2.callable_error)
        ]
        self.callable_false = [not i for i in self.result]

    def _get_truth_table(self, attribute):
        return (
            self.children[0]._get_truth_table(attribute)
            + self.children[1]._get_truth_table(attribute)
            + [(self.TRUTH_TABLE_SYMBOL, getattr(self, attribute))]
        )

    @property
    def truth_table(self):
        return self.truth_table_result

    @property
    def truth_table_result(self):
        return self._get_truth_table("result")

    @property
    def truth_table_pre_processor_error(self):
        return self._get_truth_table("pre_processor_error")

    @property
    def truth_table_callable_error(self):
        return self._get_truth_table("callable_error")

    @property
    def truth_table_callable_false(self):
        return self._get_truth_table("callable_false")


class FilteredDataAnd(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "and"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.and_)


class FilteredDataOr(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "or"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.or_)


class FilteredDataXor(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "xor"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.xor)
