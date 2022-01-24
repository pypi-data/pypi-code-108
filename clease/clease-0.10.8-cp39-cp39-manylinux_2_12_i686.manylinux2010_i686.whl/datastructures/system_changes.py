from typing import NamedTuple, Sequence
import typing
import ase

__all__ = ('SystemChange', 'SystemChanges')


class SystemChange(NamedTuple):
    index: int
    old_symb: str
    new_symb: str
    name: str

    def apply_change(self, atoms: ase.Atoms) -> None:
        """Apply the change to the atoms object. The atoms object is mutated in place.
        Note, no check is performed to ensure that the 'old_symb' is correct.

        :param atoms: ASE Atoms object to be mutated.
        """
        atoms.symbols[self.index] = self.new_symb

    def undo_change(self, atoms: ase.Atoms) -> None:
        """Undo the change to the atoms object. The atoms object is mutated in place.
        Note, that no check is performed to ensure that the changed symbol is what is expected.

        :param atoms: ASE Atoms object to be mutated.
        """
        atoms.symbols[self.index] = self.old_symb


# Type alias for multiple SystemChange objects
SystemChanges = Sequence[SystemChange]


def get_inverted_changes(system_changes: SystemChanges) -> typing.Iterator[SystemChange]:
    """Invert system changes by doing old_symbs -> new_symbs."""
    yield from (SystemChange(index=change.index,
                             old_symb=change.new_symb,
                             new_symb=change.old_symb,
                             name=change.name) for change in system_changes)
