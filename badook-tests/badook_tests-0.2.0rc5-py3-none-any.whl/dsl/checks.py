import shortuuid


class Check(object):

    def __init__(self, from_dataset, calc_name, check_fn, ctx, to_dataset=None, to_calc_name=None, join_keys=None):

        self.id = shortuuid.uuid()
        self.project_id = ctx.project_name
        self.calc_name = calc_name
        self.from_dataset = from_dataset

        if not to_dataset is None:
            self.to_dataset = to_dataset
            if not to_calc_name is None:
                self.to_calc_name = to_calc_name

        if join_keys:
            self.join_keys = join_keys

        self.check_fn = check_fn
        self.test_name = ctx.test_name
        self._ctx = ctx

    def assert_with_tolerance(self, tolerance: int = 0) -> None:
        if self._ctx is None:
            raise ValueError(
                "context is not set, make sure your summery was added to a summary table correctly")
        if tolerance is not None:
            self.tolerance = tolerance
        self._ctx.assert_check(self)
        self._ctx.run_mgr.add_waiting_execution(
            f'running check for {self.test_name}', self.id)

    def assert_all(self) -> None:
        self.assert_with_tolerance()


class Calculation(object):

    def __init__(self, from_dataset, name, ctx):
        self.from_dataset = from_dataset
        self.name = name
        self._ctx = ctx
        self.to_calc_name = None

    def compare_to(self, summary, calculation=None):
        if not calculation and not summary:
            return None
        if 'parent' in summary.__dict__:
            summary = ToSummaryData(summary.dataset, summary.name, summary.parent, summary.run_id,
                                    summary.groups, summary.time_window, summary.type)
        self.to_dataset = summary
        if calculation:
            self.to_calc_name = calculation

        return self

    def join_on(self, on=None, keys_l=None, keys_r=None):
        """
        on, keys_l, keys_r: Can be string with single column name, or list with several columns name
        Examples:
            1. join_on('Suburb')
            2. join_on(['Suburb','Type'])
            3. join_on(keys_l = 'Suburb', keys_r = 'Suburb_copy')
            4. join_on(keys_l = ['Suburb', 'Rooms'], keys_r = ['Suburb_copy', 'Rooms']

        :return: join_keys = {'keys_l': keys_l, 'keys_r': keys_r}
        """
        if on:
            if type(on) is str:
                on = [on]
            self.join_keys = {
                'keys_l': on,
                'keys_r': on
            }

        elif keys_l and keys_r:
            if type(keys_l) is str:
                keys_l = [keys_l]
            if type(keys_r) is str:
                keys_r = [keys_r]

            self.join_keys = {
                'keys_l': keys_l,
                'keys_r': keys_r
            }
        return self

    def check(self, check_fn):
        if hasattr(self, 'to_dataset'):
            if hasattr(self, 'join_keys'):
                return Check(self.from_dataset, self.name, check_fn, self._ctx, self.to_dataset, self.to_calc_name, self.join_keys)
            else:
                return Check(self.from_dataset, self.name, check_fn, self._ctx, self.to_dataset, self.to_calc_name)

        return Check(self.from_dataset, self.name, check_fn, self._ctx)


class ToSummaryData(object):

    def __init__(self, dataset, summary_name, name, run_id, join_on, time_window, summary_type):
        self.name = name
        self.summary_name = summary_name
        self.run_id = run_id
        self.join_on = join_on
        self.time_window = time_window
        self.dataset = dataset
        self.type = summary_type
