import sys
from typing import List, Sequence, Tuple, Dict
from copy import deepcopy
import numpy as np
from ase import Atoms
from ase.db import connect
from clease.settings import ClusterExpansionSettings

__all__ = ('ClusterCoverageChecker',)


class ClusterCoverageChecker:
    """
    Class for checking how large fraction of the possible configurational variation of
    all the clusters is captured by a set of template atoms. The origin of decrease in
    coverage is that for small cells, some clusters wraps around and thus interact with
    a periodic image. In a very large cell (much larger than the cluster diameters)
    there are no such "wrap-rounds".

    Example:

    In a huge cell a particular pair cluster consists of the figures
    [[0, 765], [0, 87], [0, 2], [0, 6]]

    When a small cell is used, some of the interactions will wrap around. If
    87, 765 is a periodic image of atom no. 4 and 6 is a periodic image of 2
    we have

    [[0, 4], [0, 4], [0, 2], [0, 2]]

    thus, no matter which species occupies the different sites in the small cell,
    one cannot cover all possible variation in this cluster. We define the
    coverage as <num unique figs>/<tot num figs>. Above we have two unique figs
    ([0, 4] and [0, 2]) and the total number of figures is 4. Thus, the covarage is 2/4 = 0.5.

    Some numeric examples:

    Figures                                    Coverage
    [[0, 1], [0, 5], [0, 3], [0, 7]]           1.0
    [[0, 0], [0, 0], [0, 0], [0, 0]]           0.25
    [[0, 1], [0, 1], [0, 4], [0, 8]]           0.75
    [[0, 1], [0, 1], [0, 1], [0, 3]]           0.5
    [[0, 1], [0, 1], [0, 3], [0, 3]]           0.5

    :param settings: ClusterExpansionSettings instance
    :param select_cond: Select condition used for DB query when extracing
        data from the DB. If not given, [('struct_type', '=', 'initial')]
        is used.
    """

    def __init__(self,
                 settings: ClusterExpansionSettings,
                 select_cond: Sequence[Tuple[str, str, str]] = None):
        # Make copy such that we don't alter the settings object
        self.settings = deepcopy(settings)

        if select_cond is None:
            self._select_cond = [('struct_type', '=', 'initial')]
        else:
            self._select_cond = select_cond

    def _unique_templates(self) -> List[Atoms]:
        unique_templates = []

        with connect(self.settings.db_name) as db:
            for row in db.select(self._select_cond):
                atoms = row.toatoms()
                if not _template_exists(unique_templates, atoms):
                    unique_templates.append(atoms)
        return unique_templates

    def coverage(self, template: Atoms) -> Dict[str, float]:
        """
        Return the cluster coverage for the passed atoms object.
        If the coverage is 1.0, then all possible figures in a cluster
        is covered. If it is for example 0.3, it means that the current
        template can only capture variations in 30% of the figures.

        :param template: Template
        """
        self.settings.set_active_template(atoms=template)
        coverages = {}
        for cluster in self.settings.cluster_list:
            if cluster.name.startswith(('c0', 'c1')):
                continue
            sorted_figs = []
            for figure in cluster.indices:
                sorted_figs.append(tuple(sorted(figure)))
            unique_figs = set(sorted_figs)

            coverages[cluster.name] = len(unique_figs) / len(sorted_figs)
        return coverages

    def max_coverage(self) -> Dict[str, float]:
        """
        Return the maximum cluster coverage among all templates in the database.
        If the coverage is 1.0, then all possible figures in a cluster
        is covered. If it is for example 0.3, it means that the current
        template can only capture variations in 30% of the figures.
        """
        coverages = {}
        for template in self._unique_templates():
            new_cov = self.coverage(template)
            coverages.update({k: v for k, v in new_cov.items() if v > coverages.get(k, 0.0)})
        return coverages

    def print_report(self, coverage: Dict[str, float] = None, file=sys.stdout) -> None:
        """
        Prints a nicely formatted report of coverage.

        :param coverage: dictionary with the coverage information. If not given,
            the coverage will be extracted from the database.
        :param file: a file-like object (stream); defaults to the current sys.stdout.
        """
        if coverage is None:
            coverage = self.max_coverage()

        # Add to tuple and sort from in ascending coverage order
        srt = sorted([(v, k) for k, v in coverage.items()])
        print("-" * 33, file=file)
        print("| Cluster name    | Coverage    |", file=file)
        print("-" * 33, file=file)
        for item in srt:
            print(f"| {item[1]:15} | {item[0]:8.2f}{_quality_indicator(item[0])} |", file=file)
        print("-" * 33, file=file)
        print("Explanation: ***: Insufficient, **: Poor, *: OK, '' Good", file=file)
        print(f"Cluster coverage: {_grade(coverage)}", file=file)


def _template_exists(current: Sequence[Atoms], new: Atoms) -> bool:
    """
    Check if the passed template already exists
    """
    for template in current:
        if len(template) != len(new):
            continue

        if np.allclose(template.get_positions(), new.get_positions()):
            return True
    return False


def _grade(coverage: Dict[str, float]) -> str:
    grade = "Very good (coverage > 0.75)"
    for v in coverage.values():
        if v < 0.75:
            grade = "OK (coverage > 0.5)"

        if v < 0.5:
            grade = "Insufficient (coverage < 0.5)"
            return grade
    return grade


def _quality_indicator(num: float) -> str:
    """
    Return a quality indicator. *** very bad, ** better, * even better and empty (best)
    """
    if num < 0.25:
        return '***'
    if num < 0.5:
        return '** '
    if num < 0.75:
        return '*  '
    return '   '
