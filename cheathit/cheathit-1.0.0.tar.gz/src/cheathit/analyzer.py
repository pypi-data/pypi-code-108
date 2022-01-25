from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable, Optional, Union

from .file_finder import search
from .ngram import Ngram
from .ngram_collector import NgramCollection
from .parser import parse
from .shared import ATTEMPT, GROUP, Mapping, PROBLEM, STUDENT

__all__ = [
    'Analysis',
    'analyze',
    'ProgressTracker',
    'Student',
]

STUDENT_JOINER = '/'

Student = str
Problem = Optional[tuple[str, ...]]
Group = tuple[str, ...]
StudentData = dict[Problem, list[tuple[Path, NgramCollection]]]
Data = dict[Student, StudentData]
UpperLimits = defaultdict[tuple[Path, Path], int]

ProgressTracker = Callable[[str], None]


@dataclass(frozen=True)
class SubmissionMatch:
    a: Path
    b: Path
    common_tokens: int
    longest_ngram: list[str]


@dataclass(frozen=True)
class StudentMatch:
    a: Student
    b: Student
    common_tokens: int
    submission_matches: list[SubmissionMatch]


@dataclass(frozen=True)
class Analysis:
    submission_count: int
    problem_count: int
    student_count: int
    group_count: int
    student_matches: list[StudentMatch]


def naturalize_single(value: str) -> tuple[Union[str, int], ...]:
    return tuple(int(section) if section.isdigit() else section
                 for section in re.split(r'(?!^)(?<!\d)(?=\d)|(?<=\d)(?!\d)(?!$)', value))


def naturalize(data: tuple[str, ...]) -> tuple[Union[str, int], ...]:
    return sum((naturalize_single(value) for value in data), ())


def get_search_result_key(result: tuple[Path, Mapping]) -> tuple[Union[str, int], ...]:
    _, mapping = result
    return naturalize(sum((mapping.get(key, ()) for key in (GROUP, STUDENT, PROBLEM, ATTEMPT)), ()))


def sorted_search(root: Path, components: tuple[str, ...]) -> list[tuple[Path, Mapping]]:
    return sorted(search(root, components), key=get_search_result_key)


def get_student(mapping: Mapping) -> Student:
    return STUDENT_JOINER.join(mapping.get(GROUP, ()) + mapping[STUDENT])


def get_problem(mapping: Mapping) -> Problem:
    return mapping.get(PROBLEM, None)


def zero_if_less_than(anchor: float, value: int) -> int:
    return value if value >= anchor else 0


def compare_students(a: StudentData, b: StudentData, upper_limits: UpperLimits, min_ratio: float,
                     excluded: set[Ngram]) -> list[SubmissionMatch]:
    matches: list[SubmissionMatch] = []
    for problem, a_attempts in a.items():
        if problem in b:
            b_attempts = b[problem]
            if max_correspondence := max((
                (zero_if_less_than(limit, min(
                    a_ngrams.count_common_tokens(b_ngrams, excluded),
                    b_ngrams.count_common_tokens(a_ngrams, excluded),
                )), a_path, b_path, a_ngrams, b_ngrams)
                for a_path, a_ngrams in a_attempts
                for b_path, b_ngrams in b_attempts
                if (a_path, b_path) in upper_limits and upper_limits[(a_path, b_path)] >=
                   (limit := max(len(a_ngrams.tokens), len(b_ngrams.tokens)) * min_ratio)
            ), default=None):
                common_tokens, a_path, b_path, a_ngrams, b_ngrams = max_correspondence
                if common_tokens > 0:
                    matches.append(SubmissionMatch(
                        a_path,
                        b_path,
                        common_tokens,
                        a_ngrams.longest_common(b_ngrams, excluded) or [],
                    ))
    return matches


def compare_all(data: Data, upper_limits: UpperLimits, min_ratio: float,
                excluded: set[Ngram], tracker: ProgressTracker) -> list[StudentMatch]:
    student_matches: list[StudentMatch] = []
    students = list(data.items())
    for a_index in range(len(students)):
        a_student, a_data = students[a_index]
        tracker(f'Processing student {a_student} ({a_index + 1} of {len(students)})...')
        for b_index in range(a_index + 1, len(students)):
            b_student, b_data = students[b_index]
            if submission_matches := compare_students(a_data, b_data, upper_limits, min_ratio, excluded):
                student_matches.append(StudentMatch(
                    a_student,
                    b_student,
                    sum(match.common_tokens for match in submission_matches),
                    submission_matches,
                ))
    return student_matches


def analyze(root: Path, components: tuple[str, ...], min_n: int, max_n: int, min_ratio: float, max_clique: int,
            tracker: ProgressTracker) -> Analysis:
    tracker('Discovering submissions...')
    submissions = sorted_search(root, components)
    ngrams_by_group: defaultdict[Ngram, set[Group]] = defaultdict(set)
    ngrams_by_path: defaultdict[Ngram, set[Path]] = defaultdict(set)
    data: Data = {}
    problems: set[Problem] = set()
    groups: set[Group] = set()

    for index, (file, mapping) in enumerate(submissions):
        tracker(f'Loading {file} ({index + 1} of {len(submissions)})...')
        tokens = parse(file.read_text())
        ngrams = NgramCollection(tokens, min_n, max_n)

        group = mapping.get(GROUP, mapping[STUDENT])
        groups.add(group)
        student = get_student(mapping)

        for ngram in ngrams:
            ngrams_by_group[ngram].add(group)
            ngrams_by_path[ngram].add(file)

        if student not in data:
            data[student] = {}
        problem = get_problem(mapping)
        problems.add(problem)
        if problem not in data[student]:
            data[student][problem] = []
        data[student][problem].append((file, ngrams))

    tracker('Preprocessing ngrams...')
    excluded = {ngram for ngram, groups in ngrams_by_group.items() if len(groups) > max_clique}
    upper_limits: UpperLimits = defaultdict(int)
    for ngram, paths in ngrams_by_path.items():
        if ngram not in excluded:
            for a_path in paths:
                for b_path in paths:
                    if a_path != b_path:
                        upper_limits[(a_path, b_path)] += ngram.length
    matches = sorted(compare_all(data, upper_limits, min_ratio, excluded, tracker),
                     key=lambda match: match.common_tokens, reverse=True)
    return Analysis(len(submissions), len(problems), len(data), len(groups), matches)
