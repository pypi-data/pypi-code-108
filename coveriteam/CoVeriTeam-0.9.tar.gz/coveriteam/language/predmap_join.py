#!/usr/bin/env python3

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse
from collections import defaultdict
import hashlib
import logging
from typing import List, Set, Dict, Tuple

debug = False


class JoinerException(Exception):
    pass


def compute_hash(path):
    blocksize = 65536
    hasher = hashlib.sha256()
    with open(path, "rb") as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()


def parse(argv):
    # Taken from https://stackabuse.com/command-line-arguments-in-python/
    # Initiate the parser
    desc = "Merge two predmaps given as txt file.\n "
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-V", "--version", help="show program version", action="version", version="0.1"
    )
    parser.add_argument("-f", "--first", required=True, help="The first predmap")
    parser.add_argument("-s", "--second", required=True, help="The second predmap")
    parser.add_argument(
        "-t",
        "--target",
        default="merged.txt",
        help="The path for the merged predmap to be stored to. Default is current "
        "directory, filename is 'merged.txt'",
    )
    # Read arguments from the command line
    return parser.parse_args(argv)


def is_empty(file_content: List[str]) -> bool:
    return all(v.isspace() for v in file_content)


def merge_predmap(first_path, second_path, target_path) -> int:
    with open(first_path) as first:
        first_file: List[str] = first.readlines()
        with open(second_path) as sec:
            second_file: List[str] = sec.readlines()
            hash1 = compute_hash(first_path)
            hash2 = compute_hash(second_path)
            if hash1 == hash2:
                logging.info("Both witnesses are equal, hence returning the first one")
                write_file_to_target(first_file, target_path)
                return 0
            elif is_empty(second_file):
                logging.info("Second predmap is empty, returning first")
                write_file_to_target(first_file, target_path)
                return 0
            elif is_empty(first_file):
                logging.info("First predmap is empty, returning second")
                write_file_to_target(second_file, target_path)
                return 0

            # we have two non empty file:
            # start merging the head section (definitions of vars and functions)
            definitions1: Set[str]
            node_name_to_predicates1: Dict[str, list]
            definitions1, node_name_to_predicates1 = parse_predmap(first_file)
            definitions2: Set[str]
            node_name_to_predicates2: Dict[str, list]
            definitions2, node_name_to_predicates2 = parse_predmap(second_file)

            definitions: List[str] = list(definitions2.union(definitions1))
            node_name_to_predicates: Dict[str, list] = {
                k: list(set(node_name_to_predicates1[k] + node_name_to_predicates2[k]))
                for k in (
                    list(node_name_to_predicates1.keys())
                    + list(node_name_to_predicates2.keys())
                )
            }
            logging.info("All predicates:\n%s", node_name_to_predicates)

            predicates: List[str] = definitions
            predicates.append("\n")
            for node, preds in node_name_to_predicates.items():
                predicates.append(node + "\n")
                for predicate in preds:
                    predicates.append("{}\n".format(predicate))
                predicates.append("\n")

            write_file_to_target(predicates, target_path)
            return 0


def parse_predmap(content: List[str]) -> Tuple[Set[str], Dict[str, list]]:
    definitions: Set[str] = set()
    node_name_to_predicates: Dict[str, list] = defaultdict(list)
    current_node: str = ""
    at_header = True
    for s in content:
        if at_header:
            if s.isspace() or not s.startswith("("):
                at_header = False  # we left the header
                continue
            if s.startswith("(set-info"):
                continue  # ignore this line
            definitions.add(s)
        else:
            if s.startswith("("):  # A new predicate for the current Node
                assert current_node
                predicate = s.strip()
                if predicate not in node_name_to_predicates[current_node]:
                    node_name_to_predicates[current_node].append(predicate)
            elif s.isspace():
                current_node = ""
            else:
                current_node = s[:-1]
    return definitions, node_name_to_predicates


def write_file_to_target(file_content, target_path):
    with open(target_path, "w") as target:
        target.writelines(file_content)


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]
    args = parse(argv)
    first_path, second_path, target_path = args.first, args.second, args.target

    try:
        return_value = merge_predmap(first_path, second_path, target_path)
        logging.info("The merged result is stored at %s", target_path)
        return return_value
    except JoinerException as e:
        logging.error(e)
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
