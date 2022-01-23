import collections
import configparser
import functools
import logging
import math
import os
import re
import string

import numpy as np
import pandas as pd
import scipy.sparse

from rcounting import counters, parsing
from rcounting import thread_navigation as tn
from rcounting import utils
from rcounting.models import comment_to_dict
from rcounting.units import DAY, HOUR, MINUTE

printer = logging.getLogger(__name__)

alphanumeric = string.digits + string.ascii_uppercase


class CountingRule:
    """
    A rules class. It knows how to do two things:

    - Get enough history to see whether a given comment is valid
    - Determine whether all counts in a history of counts are valid.

    Examples of things it's intended to validate are:
      - That users waited enough time since their own last comment before commenting again
      - That users waited enough time since the global last comment
      - That users let enough other counters go before them
    """

    def __init__(self, wait_n=1, thread_time=0, user_time=0):
        self.n = wait_n
        self.thread_time = thread_time
        self.user_time = user_time

    def _valid_skip(self, history):
        n = self.n if self.n is not None else len(history)
        history = history.reset_index()
        skips = history.groupby("username")["index"].diff()
        return skips.isna() | (skips > n)

    def _valid_thread_time(self, history):
        if not self.thread_time:
            return True
        elapsed_time = history["timestamp"].diff()
        valid_time = elapsed_time.isna() | (elapsed_time >= self.thread_time)
        return valid_time

    def _valid_user_time(self, history):
        if not self.user_time:
            return True
        elapsed_user_time = history.groupby("username")["timestamp"].diff()
        valid_user_time = elapsed_user_time.isna() | (elapsed_user_time >= self.user_time)
        return valid_user_time

    def is_valid(self, history):
        return (
            self._valid_skip(history)
            & self._valid_thread_time(history)
            & self._valid_user_time(history)
        )

    def get_history(self, comment):
        comments = comment.walk_up_tree(limit=self.n + 1)
        max_time = max(self.thread_time, self.user_time)
        while (
            not comments[-1].is_root
            and (comment.created_utc - comments[-1].created_utc) < max_time
        ):
            comments = comments[:-1] + comments[-1].walk_up_tree(limit=9)
        return pd.DataFrame([comment_to_dict(x) for x in comments[:0:-1]])


class OnlyDoubleCounting:
    """
    Only double counting is sufficiently strange that it gets its own class.

    A thread is valid if every user in the chain counts exactly twice in a row.
    """

    def is_valid(self, history):
        history = history.set_index("comment_id")
        history["mask"] = True
        unshifted = history.username.iloc[::2]
        up_shift = history.username.shift(-1).iloc[::2]
        up_mask = up_shift.isna() | (up_shift == unshifted)
        down_shift = history.username.shift().iloc[::2]
        down_mask = down_shift.isna() | (down_shift == unshifted)
        mask = up_mask if (up_mask.sum() > down_mask.sum()) else down_mask
        history.loc[mask.index, "mask"] = mask
        history.reset_index(inplace=True)
        return history["mask"]

    def get_history(self, comment):
        comments = comment.walk_up_tree(limit=2)[:0:-1]
        return pd.DataFrame([comment_to_dict(x) for x in comments])


def validate_from_character_list(valid_characters, strip_links=True):
    def looks_like_count(comment_body):
        body = comment_body.upper()
        if strip_links:
            body = parsing.strip_markdown_links(body)
        return any(character in body for character in valid_characters)

    return looks_like_count


def base_n(n=10, strip_links=True):
    return validate_from_character_list(alphanumeric[:n], strip_links)


def permissive(comment):
    return True


balanced_ternary = validate_from_character_list("T-0+")
brainfuck = validate_from_character_list("><+-.,[]")
roman_numeral = validate_from_character_list("IVXLCDMↁↂↇ")
mayan_form = validate_from_character_list("Ø1234|-")
twitter_form = validate_from_character_list("@")
parentheses_form = validate_from_character_list("()")


def d20_form(comment_body):
    return "|" in comment_body and base_10(comment_body)


def reddit_username_form(comment_body):
    return "u/" in comment_body


def throwaway_form(comment_body):
    return reddit_username_form(comment_body) and base_10(comment_body)


planets = ["MERCURY", "VENUS", "EARTH", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE"]
planetary_octal_form = validate_from_character_list(planets)


def ignore_revivals(chain, was_revival):
    return chain if was_revival is None else [x for x, y in zip(chain, was_revival) if not y]


def update_from_title(update_function):
    @functools.wraps(update_function)
    def wrapper(old_count, chain, was_revival=None):
        chain = ignore_revivals(chain, was_revival)
        title = chain[-1].title
        return update_function(title)

    return wrapper


def permutation_order(word, alphabet, no_leading_zeros=False):
    word_length = len(word)
    if word_length == 0:
        return 0
    index = alphabet.index(word[0])
    position = index - int(no_leading_zeros)
    n_digits = len(alphabet)
    new_alphabet = alphabet[:index] + alphabet[index + 1 :]
    first_place_counts = position * math.perm(n_digits - 1, word_length - 1)
    return first_place_counts + permutation_order(word[1:], new_alphabet)


@update_from_title
def update_binary_coded_decimal(title):
    count = "".join(x for x in title.split("|")[-1] if x in ["0", "1"])
    digits = [str(int("".join(y for y in x)), 2) for x in utils.chunked(4, count)]
    return int("".join(digits))


@update_from_title
def update_no_repeating(title):
    count = parsing.find_count_in_text(title.split("|")[-1])
    word = str(count)
    result = 9 * sum([math.perm(9, i - 1) for i in range(1, len(word))])
    return result + permutation_order(word, string.digits, no_leading_zeros=True)


@update_from_title
def update_powerball(title):
    count_string = title.split("|")[-1]
    balls, powerball = count_string.split("+")
    balls = balls.split()
    alphabet = [str(x) for x in range(1, 70)]
    return permutation_order(balls, alphabet) * 26 + int(powerball) - 1


@update_from_title
def update_no_successive(title):
    count = parsing.find_count_in_text(title.split("|")[-1])
    word = str(count)
    result = sum([9 ** i for i in range(1, len(word))])
    previous_i = "0"
    for ix, i in enumerate(word[:-1]):
        result += 9 ** (len(word) - ix - 1) * (int(i) - (i >= previous_i))
        previous_i = i
    return result


collatz_dict = {}


def collatz(n):
    if n == 1:
        return 1
    if n in collatz_dict:
        return collatz_dict[n]
    if n % 2 == 0:
        return 1 + collatz(n // 2)
    return 1 + collatz(3 * n + 1)


@update_from_title
def update_collatz(title):
    regex = r".*\((.*)\)"
    contents = re.match(regex, title).groups()[0]
    current, steps = [int(x) for x in contents.split("|")]
    return sum([collatz(i) for i in range(1, current)]) + steps


base_10 = base_n(10)
default_rule = CountingRule()

wave_regex = r"(-?\d+).*\((\d+)\+?\)"  # an int, then a bracketed int, maybe with a plus after it
double_wave_regex = r"(-?\d+).*\((\d+)\).*\((\d+)\)"


@update_from_title
def update_wave(title):
    a, b = parsing.parse_submission_title(title, wave_regex)
    return 2 * b ** 2 - a


def update_increasing_type(n):
    regex = r"(-?\d+)" + r".*\((\d+)\)" * n

    @update_from_title
    def update(title):
        total = 0
        values = parsing.parse_submission_title(title, regex)
        for ix, value in enumerate(values):
            total += triangle_n_dimension(ix + 1, value)
        return total

    return update


def triangle_n_dimension(n, value):
    if value == 1:
        return 0
    return math.comb(value - 2 + n, n)


@update_from_title
def update_2i(title):
    digits = title.split("|")[-1].strip()
    corner = sum([(-4) ** ix * int(digit) for ix, digit in enumerate(digits[::-2])])
    return (2 * corner + 1) ** 2


def update_dates(count, chain, was_revival=None):
    chain = ignore_revivals(chain, was_revival)[:-1]
    regex = r"([,\d]+)$"  # All digits at the end of the line, plus optional separators
    for submission in chain:
        year = int(re.search(regex, submission.title).group().replace(",", ""))
        length = 1095 + any(map(utils.is_leap_year, range(year, year + 3)))
        count += length
    return count


def update_from_traversal(old_count, chain, was_revival):
    new_thread = chain[-1]
    count = old_count
    for thread in chain[:-1][::-1]:
        urls = filter(
            lambda x, t=thread: x[0] == t.id, parsing.find_urls_in_text(new_thread.selftext)
        )
        submission_id, comment_id = next(urls)
        comments = tn.fetch_comments(comment_id)
        count += len(comments)
        new_thread = thread
    return count


class SideThread:
    """
    A side thread class, which consists of a validation part and an update part
    In addition to checking whether a collection of counts is valid according
    to the side thread rule, the class can determine how many total counts have
    been made in a given side thread using one of:
      - A standard thread length
      - A way of parsing titles to determine the current count
      - Walking back through all the comments since the last checkpoint and adding them up
    """

    def __init__(self, rule=default_rule, form=permissive, length=1000, update_function=None):
        self.form = form
        self.rule = rule
        self.length = length
        if update_function is not None:
            self.update_count = update_function
        else:
            self.update_count = self.update_from_length

    def update_from_length(self, old_count, chain, was_revival=None):
        chain = ignore_revivals(chain, was_revival)[1:]
        if self.length is not None:
            return old_count + self.length * (len(chain))
        return None

    def is_valid_thread(self, history):
        mask = self.rule.is_valid(history)
        if mask.all():
            return (True, "")
        return (False, history.loc[~mask, "comment_id"].iloc[0])

    def is_valid_count(self, comment, history):
        history = history.append(comment_to_dict(comment), ignore_index=True)
        valid_history = self.is_valid_thread(history)[0]
        valid_count = self.looks_like_count(comment)
        valid_user = not counters.is_ignored_counter(str(comment.author))
        return valid_history and valid_count and valid_user, history

    def get_history(self, comment):
        """Fetch enough previous comments to be able to determine whether replies to
        `comment` are valid according to the side thread rules.
        """
        return self.rule.get_history(comment)

    def looks_like_count(self, comment):
        return comment.body in utils.deleted_phrases or self.form(comment.body)


class OnlyRepeatingDigits(SideThread):
    """
    A class that describes the only repeating digits side thread.

    The rule and form attributes of the side thread are the same as for base n;
    no validation that each digit actually occurs twice is currently done.

    The main aspect of this class is the update function, which is mathematically
    quite heavy. To count the number of possible only repeating digits strings,
    we build a transition matrix where the states for each digits are
      - Seen 0 times
      - Seen 1 time
      - Seen 2 or more times
    The success states are 0 and 2.

    For strings of length n, we count the success states by looking at the
    nth power of the transition matrix.
    """

    def __init__(self, n=10, rule=default_rule):
        form = base_n(n)
        self.n = n
        self.lookup = {"0": "1", "1": "2", "2": "2"}
        self.indices = self._indices(self.n)
        self.transition_matrix = self.make_dfa()
        super().__init__(rule=rule, form=form, update_function=self.update_function)

    def connections(self, i):
        base3 = np.base_repr(i, 3).zfill(self.n)
        js = [int(base3[:ix] + self.lookup[x] + base3[ix + 1 :], 3) for ix, x in enumerate(base3)]
        result = collections.defaultdict(int)
        for j in js:
            if j == 1:
                continue
            result[j] += 1
        return (
            len(result),
            np.array(list(result.keys()), dtype=int),
            np.array(list(result.values()), dtype=int),
        )

    def make_dfa(self):
        data = np.zeros(self.n * 3 ** self.n, dtype=int)
        x = np.zeros(self.n * 3 ** self.n, dtype=int)
        y = np.zeros(self.n * 3 ** self.n, dtype=int)
        ix = 0
        for i in range(3 ** self.n):
            length, js, new_data = self.connections(i)
            x[ix : ix + length] = i
            y[ix : ix + length] = js
            data[ix : ix + length] = new_data
            ix += length
        return scipy.sparse.coo_matrix(
            (data[:ix], (x[:ix], y[:ix])), shape=(3 ** self.n, 3 ** self.n)
        )

    def _indices(self, n):
        if n == 0:
            return [0]
        partial = [3 * x for x in self._indices(n - 1)]
        return sorted(partial + [x + 2 for x in partial])

    def count_only_repeating_words(self, k):
        """The number of words of length k where no digit is present exactly once"""
        # The idea is to use the inclusion-exclusion principle, starting with
        # all n ^ k possible words. We then subtract all words where a given
        # symbol occurrs only once. For each symbol there are k * (n-1) ^ (k-1)
        # such words since there are k slots for the symbol of interest, and
        # the remaining slots must be filled with one of the remaining symbols.
        # There are thus n * k * (n-1)^ *(k-1) words where one symbol occurs
        # only once. But this double counts all the cases where two symbols
        # occur only once, so we have to add them back in. In general, there
        # are (n-i)^(n-i) * C(n,i) * P(k,i) words where i symbols occur only
        # once, giving the expression:

        # The correction factor (n-1)/n accounts for the words which would
        # start with a 0

        return (
            sum(
                [
                    (-1) ** i * (self.n - i) ** (k - i) * math.comb(self.n, i) * math.perm(k, i)
                    for i in range(0, min(self.n, k) + 1)
                ]
            )
            * (self.n - 1)
            // self.n
        )

    def get_state(self, prefix):
        result = ["0"] * self.n
        for char in prefix:
            index = (self.n - 1) - int(char, self.n)
            result[index] = self.lookup[result[index]]
        return int("".join(result), 3)

    def update_function(self, old_count, chain, was_revival=None):
        chain = ignore_revivals(chain, was_revival)
        count = parsing.find_count_in_text(chain[-1].title.split("|")[-1])
        word = str(count)
        word_length = len(word)
        if word_length < 2:
            return 0
        result = sum([self.count_only_repeating_words(i) for i in range(1, word_length)])
        result += (
            (int(word[0], self.n) - 1)
            * self.count_only_repeating_words(word_length)
            // (self.n - 1)
        )
        current_matrix = scipy.sparse.identity(3 ** self.n, dtype=int, format="csr")
        for i in range(word_length - 1, 0, -1):
            prefix = word[:i]
            current_char = word[i].upper()
            suffixes = alphanumeric[: string.digits.index(current_char)]
            states = [self.get_state(prefix + suffix) for suffix in suffixes]
            result += sum([current_matrix[state, self.indices].sum() for state in states])
            current_matrix *= self.transition_matrix
        return result


known_threads = {
    "roman": SideThread(form=roman_numeral),
    "balanced ternary": SideThread(form=balanced_ternary, length=729),
    "base 16 roman": SideThread(form=roman_numeral),
    "binary encoded hexadecimal": SideThread(form=base_n(2), length=1024),
    "binary encoded decimal": SideThread(
        form=base_n(2), update_function=update_binary_coded_decimal
    ),
    "base 2i": SideThread(form=base_n(4), update_function=update_2i),
    "bijective base 2": SideThread(form=base_n(3), length=1024),
    "cyclical bases": SideThread(form=base_n(16)),
    "wait 2": SideThread(form=base_10, rule=CountingRule(wait_n=2)),
    "wait 2 - letters": SideThread(rule=CountingRule(wait_n=2)),
    "wait 3": SideThread(form=base_10, rule=CountingRule(wait_n=3)),
    "wait 9": SideThread(form=base_10, rule=CountingRule(wait_n=9)),
    "wait 10": SideThread(form=base_10, rule=CountingRule(wait_n=10)),
    "once per thread": SideThread(form=base_10, rule=CountingRule(wait_n=None)),
    "slow": SideThread(form=base_10, rule=CountingRule(thread_time=MINUTE)),
    "slower": SideThread(form=base_10, rule=CountingRule(user_time=HOUR)),
    "slowestest": SideThread(form=base_10, rule=CountingRule(thread_time=HOUR, user_time=DAY)),
    "unicode": SideThread(form=base_n(16), length=1024),
    "valid brainfuck programs": SideThread(form=brainfuck),
    "only double counting": SideThread(form=base_10, rule=OnlyDoubleCounting()),
    "mayan numerals": SideThread(length=800, form=mayan_form),
    "reddit usernames": SideThread(length=722, form=reddit_username_form),
    "twitter handles": SideThread(length=1369, form=twitter_form),
    "wave": SideThread(form=base_10, update_function=update_wave),
    "increasing sequences": SideThread(form=base_10, update_function=update_increasing_type(1)),
    "double increasing": SideThread(form=base_10, update_function=update_increasing_type(2)),
    "triple increasing": SideThread(form=base_10, update_function=update_increasing_type(3)),
    "dates": SideThread(form=base_10, update_function=update_dates),
    "invisible numbers": SideThread(form=base_n(10, strip_links=False)),
    "parentheses": SideThread(form=parentheses_form),
    "dollars and cents": SideThread(form=base_n(4)),
    "throwaways": SideThread(form=throwaway_form),
    "by 3s in base 7": SideThread(form=base_n(7)),
    "unary": SideThread(form=validate_from_character_list("|")),
    "four fours": SideThread(form=validate_from_character_list("4")),
    "using 12345": SideThread(form=validate_from_character_list("12345")),
    "japanese": SideThread(form=validate_from_character_list("一二三四五六七八九十百千")),
    "roman progressbar": SideThread(form=roman_numeral),
    "symbols": SideThread(form=validate_from_character_list("!@#$%^&*()")),
    "2d20 experimental v theoretical": SideThread(form=d20_form),
    "no repeating digits": SideThread(update_function=update_no_repeating),
    "powerball": SideThread(update_function=update_powerball, form=base_10),
    "collatz conjecture": SideThread(update_function=update_collatz, form=base_10),
    "only repeating digits": OnlyRepeatingDigits(),
    "no successive digits": SideThread(update_function=update_no_successive, form=base_10),
    "planetary octal": SideThread(length=1024, form=planetary_octal_form),
    "decimal encoded sexagesimal": SideThread(length=900, form=base_10),
}

# fmt: off
base_n_lengths = [
    None,
    1000, 1024,  729, 1024, 1000, 1296, 1029, 1024,  729, 1000,  # noqa E241
    1000,  864, 1014, None, None, 1024, 1156, None, None,  800,  # noqa E241
    882, None, None, None, None,  None,  729, None, None, None,  # noqa E241
    None, None, None, None, None, 1296,
]
# fmt: on

base_n_threads = {
    f"base {i}": SideThread(form=base_n(i), length=length)
    for i, length in enumerate(base_n_lengths)
    if length is not None
}
known_threads.update(base_n_threads)

# See: https://www.reddit.com/r/counting/comments/o7ko8r/free_talk_friday_304/h3c7433/?context=3

default_threads = [
    "decimal",
    "age",
    "palindromes",
    "rational numbers",
    "n read as base n number",
    "by 8s",
    "by 69s",
    "powers of 2",
    "california license plates",
    "by 0.02s",
    "by 2s even",
    "by one-hundredths",
    "by 2s odd",
    "by 3s",
    "by 4s",
    "by 5s",
    "by 7s",
    "by 8s",
    "by 10s",
    "by 12s",
    "by 20s",
    "by 23s",
    "by 29s",
    "by 40s",
    "by 50s",
    "by 64s",
    "by 99s",
    "by 123s",
    "by meters",
    "negative numbers",
    "previous dates",
    "prime factorization",
    "scientific notation",
    "street view counting",
    "3 or fewer palindromes",
    "four squares",
    "69, 420, or 666",
    "all even or all odd",
    "no consecutive digits",
    "unordered consecutive digits",
    "prime numbers",
    "triangular numbers",
    "thread completion",
    "sheep",
    "top subreddits",
    "william the conqueror",
    "10 at a time",
    "rotational symmetry",
]
known_threads.update(
    {thread_name: SideThread(form=base_10, length=1000) for thread_name in default_threads}
)

default_threads = {
    "time": 900,
    "permutations": 720,
    "factoradic": 720,
    "seconds minutes hours": 1200,
    "feet and inches": 600,
    "lucas numbers": 200,
    "hoi4 states": 806,
    "eban": 800,
    "ipv4": 1024,
}
known_threads.update(
    {key: SideThread(form=base_10, length=length) for key, length in default_threads.items()}
)


no_validation = {
    "base 40": 1600,
    "base 60": 900,
    "base 62": 992,
    "base 64": 1024,
    "base 93": 930,
    "youtube": 1024,
    "previous_dates": None,
    "qwerty alphabet": 676,
    "acronyms": 676,
    "letters": 676,
    "palindromes - letters": 676,
    "cards": 676,
    "musical notes": 1008,
    "octal letter stack": 1024,
    "permutations - letters": None,
    "iterate each letter": None,
}

known_threads.update({k: SideThread(length=v) for k, v in no_validation.items()})

default_thread_varying_length = [
    "tug of war",
    "by day of the week",
    "by day of the year",
    "by gme increase/decrease",
    "by length of username",
    "by number of post upvotes",
    "by random number",
    "by digits in total karma",
    "by timestamp seconds",
    "comment karma",
    "post karma",
    "total karma",
    "nim",
    "pick from five",
    "2d tug of war",
    "boost 5",
    "by random number (1-1000)",
]

default_thread_unknown_length = [
    "base of previous digit",
    "by number of digits squared",
    "by list size",
    "divisors",
]


def get_side_thread(thread_name):
    """Return the properties of the side thread with first post thread_id"""
    if thread_name in known_threads:
        return known_threads[thread_name]
    if thread_name in default_thread_unknown_length:
        return SideThread(length=None, form=base_10)
    if thread_name in default_thread_varying_length:
        return SideThread(update_function=update_from_traversal, form=base_10)
    if thread_name != "default":
        printer.info(
            (
                "No rule found for %s. Not validating comment contents. "
                "Assuming n=1000 and no double counting."
            ),
            thread_name,
        )
    return SideThread()


module_dir = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(module_dir, "side_threads.ini"))
known_thread_ids = config["threads"]
