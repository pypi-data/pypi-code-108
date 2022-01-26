import itertools
import json
import os
from argparse import ArgumentParser
from datetime import datetime
from functools import reduce
from os.path import exists, join

from dateutil.parser import parse as dateParse
from progress.bar import Bar


# Command line arguement parsing
def get_argparse() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        prog="ssl-metrics-git-commits-loc",
        usage="This program outputs the lines of code (LOC) per commit and the delta LOC of a Git repository in JSON format.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory containing repository root folder (.git)",
        default=".",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-b",
        "--branch",
        help="Git branch for analysis to be ran on",
        default="main",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output analysis to a JSON file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--cores",
        help="Number of cores to use for analysis",
        type=int,
        required=False,
        default=1,
    )
    return parser


def repoExists(directory: str = ".") -> bool:
    if exists(join(directory, ".git")) is False:
        return False
    return True


def parseCommitLineFromLog(line: str) -> dict:
    splitLine: list = line.split(";")
    name: str = splitLine[0]
    email: str = splitLine[1]
    hash: str = splitLine[2]
    date = splitLine[-1]
    return {
        "author_name": name,
        "author_email": email,
        "hash": hash,
        "date": dateParse(date),
    }


def analyzeCommits(commits: list, date0: datetime):
    loc_sum: int = 0
    commitCounter: int = 0
    with Bar("Processing commits... ", max=len(commits) - 1) as ib:
        for index in range(len(commits) - 1):
            authorName: str = commits[index]["author_name"]
            authorEmail: str = commits[index]["author_email"]
            hashX: str = commits[index]["hash"]
            hashY: str = commits[index + 1]["hash"]
            commitDate: str = commits[index]["date"].strftime("%m/%d/%Y")
            dateY: datetime = commits[index + 1]["date"]

            gdf: dict = gitDiffTree(hashX, hashY)

            loc = map(lambda info: info["loc"], gdf)

            delta_sum = reduce(lambda x, y: x + y, loc, 0)

            loc_sum += delta_sum
            commit_day = (dateY - date0).days
            result = {
                "commit_number": commitCounter,
                "author_name": authorName,
                "author_email": authorEmail,
                "hash": hashY,
                "delta_loc": delta_sum,
                "loc_sum": loc_sum,
                "kloc": float(loc_sum / 1000),
                "commit_date": commitDate,
                "days_since_0": commit_day,
            }

            commitCounter += 1
            ib.next()
            yield result


def gitDiffTree(hashX: str, hashY: str) -> dict:
    # git diff help page: https://www.git-scm.com/docs/git-diff
    with os.popen(f"git diff-tree -r {hashX} {hashY}") as diffTreePipe:
        for line in diffTreePipe:

            lineInfo: dict = parseDiffTreeLine(line)

            lineStatus: str = lineInfo.get("status")
            if lineStatus == "A":
                addLines(lineInfo)
            elif lineStatus == "D":
                deleteLines(lineInfo)
            elif lineStatus == "M":
                deltaLines(lineInfo)
            else:
                continue
            yield lineInfo


def parseDiffTreeLine(line: str) -> dict:
    tokens: list = line.split()
    try:
        (dstMode, sha1Src, sha1Dst, status, srcPath) = tokens[1:6]
    except ValueError:
        return {}
    return {
        "dstMode": dstMode,
        "sha1Src": sha1Src,
        "sha1Dst": sha1Dst,
        "status": status,
        "srcPath": srcPath,
    }


def addLines(line: dict) -> None:
    line["loc"] = countFileLines(line["sha1Dst"])


def deleteLines(line: dict) -> None:
    line["loc"] = -countFileLines(line["sha1Src"])


def deltaLines(line: dict) -> None:
    loc_before = countFileLines(line["sha1Src"])
    loc_after = countFileLines(line["sha1Dst"])
    line["loc"] = loc_after - loc_before


# TODO: Could replace this with cloc; make parametric
def countFileLines(blobHash: str):
    # Git show help page: https://www.git-scm.com/docs/git-show
    # wc help page: https://linux.die.net/man/1/wc
    with os.popen(f"git show {blobHash} | wc -l") as data:
        return int(data.read().split()[0])
    return -1


def exportJSON(filename, commitInfo):
    with open(filename, "w") as jsonf:
        json.dump(commitInfo, jsonf, indent=4)


def pairwise(
    iterable,
    coreCount: int,
    maxValue: int,
) -> list:
    data: list = []
    a, b = itertools.tee(iterable)
    next(b, None)

    x: tuple
    for x in zip(a, b):
        temp: list = [x[0], x[1]]
        if temp[0] == 0:
            pass
        else:
            temp[0] += 1
        data.append(temp)

    if len(data) < coreCount:
        data.append([data[-1][1] + 1, maxValue])
        print(data)

    if data[-1][1] != maxValue:
        data[-1][1] = maxValue

    return data


def main() -> bool:
    pwd = os.getcwd()
    args = get_argparse().parse_args()

    if repoExists(directory=args.directory) is False:
        return False

    os.chdir(args.directory)
    os.system(f"git checkout {args.branch}")

    # Git log help page: https://www.git-scm.com/docs/git-log
    with os.popen(r'git log --reverse --pretty=format:"%an;%ae;%H;%ci"') as gitLogPipe:
        commits: list = [parseCommitLineFromLog(line=commit) for commit in gitLogPipe]

        commit0AuthorName: str = commits[0]["author_name"]
        commit0AuthorEmail: str = commits[0]["author_email"]
        commit0Date: datetime = commits[0]["date"]
        commits = [
            {
                "author_name": commit0AuthorName,
                "author_email": commit0AuthorEmail,
                "hash": "--root",
                "date": commit0Date,
            }
        ] + commits

        commit_info_iter = analyzeCommits(commits=commits, date0=commits[0]["date"])
        commit_info = list(commit_info_iter)
        delta_loc_iter = map(lambda info: info["delta_loc"], commit_info)
        loc_sum = reduce(lambda x, y: x + y, delta_loc_iter, 0)

    if args.output:
        exportJSON(join(pwd, args.output), commit_info)

    os.chdir(pwd)
    return True


if __name__ == "__main__":
    main()
