from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.containers.Winners import Winners


class Scores(DictPrintingInOrder):
    """The scores of the candidates

    Examples
    --------
        >>> scores = Scores({'a': 0.7, 'b':0.7, 'c':0.3})
        >>> print(scores)
        {a: 0.7, b: 0.7, c: 0.3}
        >>> print(scores.winners)
        a, b
    """

    @property
    def winners(self):
        """Winners: The set of winners."""
        return Winners(k for k, v in self.items() if v == max(self.values()))
