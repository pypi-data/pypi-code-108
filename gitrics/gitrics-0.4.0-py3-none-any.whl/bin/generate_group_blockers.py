#!/usr/bin/env python3

import argparse

import networkx as nx

from gitrics import configuration
from gitrics.group.issues import gitricsGroupIssues
from gitrics.bin.parameters import param_api, param_group, param_token

def main(group_id: str = None, issues: list = None) -> list:
    """
    Generate list of blockers in directional network of blocking issues.

    Args:
        group_id (string): GitLab Group id
        issues (list): dictionaries where each is a GitLab Issue

    Returns:
        A list of x.
    """

    result = None

    # parse arguments
    opt = parse_args()

    # get issues in group
    ggi = gitricsGroupIssues(
        group_id=group_id if group_id else opt.group,
        issues=issues,
        token=opt.token,
        version=opt.api
    )

    # check for issues
    if ggi.nested:

        # calculate degree centrality
        dc = nx.degree_centrality(ggi.nested)

        # remove root node
        dc.pop(0)

        # get max value
        max_block_centrality = max(dc, key=dc.get)

        # get any nodes with max value
        result = sorted([
            d for d in ggi.issues
            if d.id in dc and
            dc[d.id] == dc[max_block_centrality]
        ], key=lambda d: nx.descendants(ggi.nested, d.id), reverse=True)

    return result

def parse_args():
    """
    Parse user input.

    Returns:
        A Namespace with attributes for each provided argument.
    """

    # create arguments
    parser = argparse.ArgumentParser()

    # define optional values
    param_api(parser)
    param_group(parser)
    param_token(parser)

    # parse user input
    args, unknown = parser.parse_known_args()

    return args

if __name__ == "__main__":
    main()
