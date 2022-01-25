
import typing as t
from collections.abc import Sequence
from nr.util.generic import T


def longest_common_substring(
  seq1: Sequence[T],
  seq2: Sequence[T],
  *args: Sequence[T],
  start_only: bool = False,
) -> Sequence[T]:
  """ Finds the longest common contiguous sequence of elements in *seq1* and *seq2* and returns it. """

  longest: tuple[int, int] = (0, 0)
  for i in (0,) if start_only else range(len(seq1)):
    for j in (0,) if start_only else range(len(seq2)):
      k = 0
      while (i + k < len(seq1) and (j + k) < len(seq2)) and seq1[i + k] == seq2[j + k]:
        k += 1
      if k > longest[1] - longest[0]:
        longest = (i, i + k)

  result = seq1[longest[0]:longest[1]]
  if args:
    result = longest_common_substring(result, *args, start_only=start_only)
  return result
