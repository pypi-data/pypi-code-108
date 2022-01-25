import argparse
from pathlib import Path
import sys

from .analyzer import analyze
from .shared import GROUP, STUDENT, PROBLEM, ATTEMPT

ALLOWED_COMPONENTS = [STUDENT, GROUP, PROBLEM, ATTEMPT]
COMPONENT_DELIMITER = '/'
DEFAULT_PATH = STUDENT
COMPONENT_DESCRIPTION = f'{", ".join(map(repr, ALLOWED_COMPONENTS))}'f' separated with {repr(COMPONENT_DELIMITER)}'

DEFAULT_MIN_NGRAM = 1
DEFAULT_MAX_NGRAM = 20

DEFAULT_CLIQUE_INDIVIDUAL = 5
DEFAULT_CLIQUE_GROUP = 2

DEFAULT_MIN_RATIO = 0.2

STUDENT_MATCH_DELIMITER = '-' * 20 + '\n\n' + '-' * 20
STUDENT_SUBMISSION_DELIMITER = '-' * 5
SUBMISSION_MATCH_DELIMITER = '+'


def parse_path(path: str) -> tuple[str, ...]:
    components = path.split(COMPONENT_DELIMITER)
    if not all(component in ALLOWED_COMPONENTS for component in components):
        raise argparse.ArgumentTypeError(f'Expected {COMPONENT_DESCRIPTION}, got {repr(path)}')
    if STUDENT not in components:
        raise argparse.ArgumentTypeError(f'Expected {repr(STUDENT)} among the path components, got {repr(path)}')
    return tuple(components)


def parse_positive_integer(value: str) -> int:
    try:
        size = int(value)
    except ValueError:
        size = None
    if size is None or size <= 0:
        raise argparse.ArgumentTypeError(f'Expected positive integer, got {repr(value)}')
    return size


def parse_ratio(value: str) -> float:
    try:
        ratio = float(value)
    except ValueError:
        ratio = None
    if ratio is None or not 0.0 <= ratio <= 1.0:
        raise argparse.ArgumentTypeError(f'Expected a number between 0.0 and 1.0, got {repr(value)}')
    return ratio


def numeral(n: int, word: str, plural_suffix: str = 's') -> str:
    return f'{n} {word}{"" if n == 1 else plural_suffix}'


def log(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path, help='directory with submissions')
    parser.add_argument('--path', type=parse_path, nargs='?', default=DEFAULT_PATH,
                        help=f'template for the path to individual submissions: {COMPONENT_DESCRIPTION}')
    parser.add_argument('--min-ngram', type=parse_positive_integer, nargs='?', default=DEFAULT_MIN_NGRAM,
                        help='minimum size of ngrams to analyze')
    parser.add_argument('--max-ngram', type=parse_positive_integer, nargs='?', default=DEFAULT_MAX_NGRAM,
                        help='maximum size of ngrams to analyze')
    parser.add_argument('--min-ratio', type=parse_ratio, nargs='?', default=DEFAULT_MIN_RATIO,
                        help='minimum ratio of the number of shared tokens'
                             ' to the number of tokens in the longer of the two submissions')
    parser.add_argument('--max-clique', type=parse_positive_integer, nargs='?', default=None,
                        help=f'if an ngram occurs in submissions of more than so many students (or in submissions'
                             f' of students from more than so many groups), it is excluded from analysis')
    arguments = parser.parse_args()
    root: Path = arguments.root
    if not root.exists():
        parser.error(f'{root} does not exist')
    if not root.is_dir():
        parser.error(f'{root} is not a directory')
    path: tuple[str, ...] = arguments.path
    has_groups = GROUP in path
    min_ngram: int = arguments.min_ngram
    max_ngram: int = arguments.max_ngram
    if min_ngram > max_ngram:
        parser.error(f'Min ngram size exceeds max ngram size: {min_ngram} > {max_ngram}')
    min_ratio: float = arguments.min_ratio
    max_clique: int = (arguments.max_clique if arguments.max_clique is not None
                       else (DEFAULT_CLIQUE_GROUP if has_groups else DEFAULT_CLIQUE_INDIVIDUAL))
    if max_clique == 1 and not has_groups:
        parser.error('Max clique size must be greater than 1 if students are not assigned groups')
    log(f'Running with '
        f'path={COMPONENT_DELIMITER.join(path)}, '
        f'min-ngram={min_ngram}, '
        f'max-ngram={max_ngram}, '
        f'min-ratio={min_ratio}, '
        f'max-clique={max_clique}')
    analysis = analyze(root, path, min_ngram, max_ngram, min_ratio, max_clique, log)
    print(', '.join(filter(None, [
        numeral(analysis.submission_count, 'submission'),
        numeral(analysis.problem_count, 'problem'),
        numeral(analysis.student_count, 'student'),
        numeral(analysis.group_count, 'group') if has_groups else None,
    ])) + ' discovered')
    print(numeral(len(analysis.student_matches), 'student-to-student match', 'es') + ' found')
    for student_match in analysis.student_matches:
        print(STUDENT_MATCH_DELIMITER)
        print(student_match.a)
        print(student_match.b)
        print(numeral(student_match.common_tokens, 'common token'))
        for index, submission_match in enumerate(student_match.submission_matches):
            print(STUDENT_SUBMISSION_DELIMITER if index == 0 else SUBMISSION_MATCH_DELIMITER)
            print(submission_match.a)
            print(submission_match.b)
            print(numeral(submission_match.common_tokens, 'common token')
                  + ' / ' + numeral(len(submission_match.longest_ngram), 'token') + ' in the longest match:')
            print(' '.join(submission_match.longest_ngram))
    log('Analysis complete')
