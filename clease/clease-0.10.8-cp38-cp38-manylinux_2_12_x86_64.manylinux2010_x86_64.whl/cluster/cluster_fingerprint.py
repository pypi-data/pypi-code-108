from typing import Any, Iterable
from functools import total_ordering
import numpy as np
import attr

__all__ = ('ClusterFingerprint',)


def _fingerprint_converter(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        return x
    if isinstance(x, Iterable):
        x = np.array(x)
    return x


@total_ordering
@attr.s(eq=False, order=False)
class ClusterFingerprint:
    """Container for a Cluster Fingerprint."""

    fp: np.ndarray = attr.ib(converter=_fingerprint_converter,
                             validator=attr.validators.instance_of(np.ndarray))
    tol: float = attr.ib(default=1e-9)

    def __lt__(self, other) -> bool:
        if not isinstance(other, ClusterFingerprint):
            return NotImplemented

        self_len = len(self.fp)
        other_len = len(other.fp)

        if self_len < other_len:
            return True
        if self_len > other_len:
            return False

        diff = self.fp - other.fp
        for value in diff:
            if value < -self.tol:
                return True
            if value > self.tol:
                return False

        return False

    def __eq__(self, other) -> bool:
        if not isinstance(other, ClusterFingerprint):
            return NotImplemented

        if len(self.fp) != len(other.fp):
            return False
        # We disable rtol, as it is otherwise messing with the numerical
        # accuracy we're trying to achieve.
        return np.allclose(self.fp, other.fp, atol=self.tol, rtol=0)

    def __getitem__(self, i):
        return self.fp[i]

    def __len__(self):
        return len(self.fp)

    @fp.validator
    def _validate_fp(self, attribute, value) -> None:
        """The Fingerprint must be a 1d array."""
        # pylint: disable=unused-argument, no-self-use
        if not value.ndim == 1:
            raise ValueError(f"Fingerprint must be a 1d array, got {value.ndim}")
