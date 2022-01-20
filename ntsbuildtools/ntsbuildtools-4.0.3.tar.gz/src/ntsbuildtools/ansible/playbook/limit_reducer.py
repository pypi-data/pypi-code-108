import itertools
import os
from typing import List, Set

from ntsbuildtools.ansible.inventory import InventoryTree


class PlaybookLimit:

    def __init__(self, hosts_path=None):
        self.ct = InventoryTree(hosts_path)

    def infer_playbook_limit(self, file_paths: List[str]) -> List[str]:
        """Given a list of file paths, return the list of 'ansible inventory groups or hosts' that can be inferred
        from those file paths. As an example, assume the only filepath provided is `inventory/group_vars/databases/config.yaml`
        then the output will simply be `databases`.

        Args:
            file_paths (List[strings]): A list of filepaths to be parsed to determine the playbook limit.
        """
        limits = set()
        for changed_file_path in file_paths:
            split_file_path = changed_file_path.split(os.path.sep)
            # Looking for paths that are of format "inventory/[host_vars|group_vars]/{targeted_host}"
            if len(split_file_path) < 3:
                continue
            if split_file_path[0] == 'inventory' and (
                    split_file_path[1] == 'group_vars' or split_file_path[1] == 'host_vars'):
                limits.add(split_file_path[2].strip())

        optimized_limits = list(self._optimize_limits(limits))
        # Sort the optimized_limits (so that the order doesn't change on repeated runs, e.g. to enable automated testing)
        optimized_limits.sort()
        return optimized_limits

    def _optimize_limits(self, limits: Set[str]) -> Set[str]:
        """Optimize the limits provided.

        :param limits: The playbook limit to be optimized.
        :return: The optimized playbook limit.

        Discussion: This happens in two phases.
        1. First iterate through each limit and compare it to all other limits.
            1. If a common ancestor is found that is in the current list of limit, mark the current limit for removal.
            2. Or, if the current limit is an only child, add the parent to the only_child_parent set and add to limits after
                interation.
        2. For the remaining limits, find their lowest common ancestor, then check to see if the children of that ancestor
        are a subset of the current limits.

        """
        # phase 1
        changes_made = True
        while changes_made:
            to_be_removed = set()
            only_child_parents = set()
            for lim in limits:
                l_ancestors = set([a.name for a in self.ct.get_node(lim).get_ancestors([])])
                if limits.intersection(l_ancestors):
                    to_be_removed.add(lim)
                # corner case where an edge node as a single parent and no siblings
                else:
                    l_node = self.ct.get_node(lim)
                    for l_a in l_ancestors:
                        if set([l_node]) == self.ct.get_node(l_a).get_children():
                            to_be_removed.add(lim)
                            only_child_parents.add(l_a)
            limits = limits.union(only_child_parents)

            # phase2
            # iterate through all possible combinations.
            best_parent = None
            for a, b in itertools.combinations(limits, 2):
                # only compare parents.
                a_parents = self.ct.get_node(a).get_parents()
                b_parents = self.ct.get_node(b).get_parents()
                for a_p in a_parents:
                    for b_p in b_parents:
                        if a_p == b_p:
                            # don't add parents that have no ancestors.
                            if limits.issuperset(set([c.name for c in a_p.get_children()])) and len(
                                    a_p.get_parents()) > 0:
                                best_parent = a_p

                if best_parent:
                    # mark children for removal
                    to_be_removed.add(a)
                    to_be_removed.add(b)
                    # add ancestor to limits.
                    limits.add(best_parent.name)
                    best_parent = None
            if not to_be_removed:
                changes_made = False
            else:
                limits -= to_be_removed
                changes_made = True
        return limits


def infer_playbook_limit(source_path, hosts_path):
    pl = PlaybookLimit(hosts_path=hosts_path)
    with open(source_path) as f:
        return pl.infer_playbook_limit(f.readlines())
