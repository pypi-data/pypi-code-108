
from collections.abc import Sequence
from nr.util.generic import T


def longest_common_substring(seq1: Sequence[T], seq2: Sequence[T]) -> Sequence[T]:
  """ Finds the longest common contiguous sequence of elements in *seq1* and *seq2* and returns it. """

  longest: tuple[int, int] = (0, 0)
  for i in range(len(seq1)):
    for j in range(len(seq2)):
      k = 0
      while (i + k < len(seq1) and (j + k) < len(seq2)) and seq1[i + k] == seq2[j + k]:
        k += 1
      if k > longest[1] - longest[0]:
        longest = (i, i + k)
  return seq1[longest[0]:longest[1]]
