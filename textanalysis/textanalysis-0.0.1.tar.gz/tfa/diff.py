import sys
import collections
from textwrap import dedent
from Levenshtein import distance, editops
from tf.advanced.helpers import dm


class DiffCode:
    def __init__(self, app):
        """Connect to a corpus.

        Parameters
        ----------
        app: object
            Text-Fabric object that holds a corpus. It is the result of
            `A = use(corpus)` where `use()` is defined in `tf.app`.
        """
        self.app = app

    def collectWords(self, otype, feature):
        """Read the words of the corpus and store them in an occurrence dict.

        Parameters
        ----------
        otype: string
            Object type in the corpus that corresponds to the words we want to
            collect.
        feature: string
            Feature in the corpus that provides a string value for each word occurrence
            in the corpus.
        """
        app = self.app
        F = app.api.F
        Fs = app.api.Fs

        getText = Fs(feature).v

        wordOccs = collections.defaultdict(list)
        self.wordOccs = wordOccs

        allWords = F.otype.s(otype)
        nWords = len(allWords)

        nWords = 0

        for w in allWords:
            text = getText(w)
            if text:
                wordOccs[text].append(w)
                nWords += 1

        print(f"{nWords} {otype} occurrences of {len(wordOccs)} distinct words")

    def collectCommon(self, frequencyThreshold=6, sizeThreshold=5):
        """Collect the common, not too short words of the corpus.

        Parameters
        ----------
        frequencyThreshold: int, optional 6
            Only words that are at least as frequent as this threshold
        sizeThreshold: int, optional 5
            Only words that are at least as long as this threshold

        Returns
        -------
        wordsCommon: list
            sorted list of distinct relevant words.
        """

        self.frequencyThreshold = frequencyThreshold
        self.sizeThreshold = sizeThreshold

        wordOccs = self.wordOccs

        wordsCommon = sorted(
            word
            for (word, occs) in wordOccs.items()
            if len(occs) >= frequencyThreshold and len(word) >= sizeThreshold
        )
        self.wordsCommon = wordsCommon
        print(f"{len(wordsCommon)} common words")

    def collectClose(self, distThreshold=5):
        """Collect the close pairs of common words.

        Parameters
        ----------
        distThreshold: int, optional 5
            Only pairs of words whose distance is at most this threshold

        Returns
        -------

        nPairs: int
            number of pairs that have been collected

        wordsUsed: set
            set of words that are member of a collected pair of words

        wordMatrix: dict
            dict of dict, keyed by source word then destination word,
            and valued by the edit distance of these words
        """

        self.distThreshold = distThreshold

        wordsCommon = self.wordsCommon

        wordUsed = set()
        self.wordUsed = wordUsed

        wordMatrix = collections.defaultdict(dict)
        self.wordMatrix = wordMatrix

        nWords = len(wordsCommon)
        total = nWords * (nWords - 1) // 2
        print(f"Computing {total} comparisons")

        k = 0
        c = 0
        nPairs = 0
        chunkSize = int(round(total / 100))

        for i in range(nWords - 1):
            word1 = wordsCommon[i]

            for j in range(i + 1, nWords):
                if c == chunkSize:
                    c = 0
                    sys.stdout.write(f"\r{k:>9} = {int(round(k / chunkSize)):>3} %")
                k += 1
                c += 1
                word2 = wordsCommon[j]
                dist = distance(word1, word2)
                if dist <= distThreshold:
                    nPairs += 1
                    wordMatrix[word1][word2] = dist
                    wordUsed.add(word1)
                    wordUsed.add(word2)

        self.nPairs = nPairs
        sys.stdout.write(f"\r{k:>9} = {int(round(k / chunkSize)):>3} %")
        print(f"\nStored {nPairs} word pairs between {len(wordUsed)} words")

    def computeDiffs(self):
        """Compute all relevant diffs and store them by diff code.

        We use the function `codeDiff` to compute a diff code for
        each pair of words collected by `collectClose()`.

        Returns
        -------
        wordDiff: dict
            keyed by diff codes and valued by pairs
            whose difference is characterized by that diff code.
        """
        nPairs = self.nPairs
        wordMatrix = self.wordMatrix

        wordDiff = collections.defaultdict(list)
        self.wordDiff = wordDiff

        print(f"Computing {nPairs} diffs between word pairs")
        k = 0
        c = 0
        chunkSize = int(round(nPairs / 100))

        for (word1, words2) in wordMatrix.items():
            for word2 in words2:
                if c == chunkSize:
                    c = 0
                    sys.stdout.write(f"\r{k:>9} = {int(round(k / chunkSize)):>3} %")
                k += 1
                c += 1
                diff = codeDiff(word1, word2)
                wordDiff[diff].append((word1, word2))

        sys.stdout.write(f"\r{k:>9} = {int(round(k / chunkSize)):>3} %")
        print(f"\n{len(wordDiff)} distinct differences")

    def showDiffs(self, fro, to):
        """Lists part of the differences between word pairs.

        The diff codes are sorted by their frequency among word pairs.

        Parameters
        ----------
        fro: int
            start index in the sorted list of differences
        to: int
            end index (not-inclusive) in the sorted list of differences

        Returns
        -------
        None
            But shows a formatted list of the diff codes between fro and to
            with a limited amount of examples.
        """
        wordDiff = self.wordDiff
        if not hasattr(self, "wordDiffList"):
            wordDiffList = sorted(
                wordDiff.items(), key=lambda x: (-len(x[1]), x[0])
            )
            self.wordDiffList = wordDiffList

        wordDiffList = self.wordDiffList
        md = [dedent("""\
        seq | freq | `-` | `+` | examples
        --- | ---  | --- | --- | ---\
        """)]

        for (i, ((d, a), pairs)) in enumerate(wordDiffList[fro:to]):
            freq = len(pairs)
            exampleRep = " ` ` ".join(" `~` ".join(pair) for pair in pairs[0:3])
            aRep = a if a else " "
            dRep = d if d else " "
            md.append(f"*{i + 1}* | **{freq}** | `{dRep}` | `{aRep}` | {exampleRep}")
        dm("\n".join(md))

    def getDiffs(self):
        """Returns the word diff dictionary.

        It is keyed by diff code and valued by all word pairs that have
        that diff code.
        """
        return self.wordDiff


def codeDiff(source, dest):
    """Compute the diff code between strings.

    In order to produce a handy diff between words,
    we use the function
    [editops(word1, word2)](https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html)
    of the
    [Levenshtein module](https://pypi.org/project/python-Levenshtein/#documentation).

    It gives a sequence of edit operations to change the `source` word into
    the `dest` word.
    We take that sequence and represent it by identifying
    which pieces of `source` must be left out and
    which pieces of `dest` will be added to `source`.
    We also mark whether these pieces occur at the begin or end of
    `source` / `dest`.
    If several non-adjacent pieces have to be added or deleted
    we separate them by a `.`
    """
    opMin = []
    opPlus = []
    for (op, iS, iD) in editops(source, dest):
        if op == "replace":
            opMin.append(iS)
            opPlus.append(iD)
        elif op == "insert":
            opPlus.append(iD)
        elif op == "delete":
            opMin.append(iS)
    materialMin = ""
    prevI = len(source)
    endI = len(source) - 1
    for i in sorted(opMin):
        pre = "(" if i == 0 else "." if i > prevI + 1 else ""
        post = ")" if i == endI else ""
        materialMin += f"{pre}{source[i]}{post}"
        prevI = i

    materialPlus = ""
    prevI = len(dest)
    endI = len(dest) - 1
    for i in sorted(opPlus):
        pre = "(" if i == 0 else "." if i > prevI + 1 else ""
        post = ")" if i == endI else ""
        materialPlus += f"{pre}{dest[i]}{post}"
        prevI = i

    return (materialMin, materialPlus)


def collectDiffs(
    app, otype, feature, frequencyThreshold=6, sizeThreshold=5, distThreshold=5
):
    """Compute codes pairwise differences between pairs of common words.

    Parameters
    ----------
    app: object
        Text-Fabric object that holds a corpus. It is the result of
        `A = use(corpus)` where `use()` is defined in `tf.app`.
    otype: string
        Object type in the corpus that corresponds to the words we want to
        collect.
    feature: string
        Feature in the corpus that provides a string value for each word occurrence
        in the corpus.
    frequencyThreshold: int, optional 6
        Only words that are at least as frequent as this threshold
    sizeThreshold: int, optional 5
        Only words that are at least as long as this threshold
    distThreshold: int, optional 5
            Only pairs of words whose distance is at most this threshold

    Returns
    -------
    object
        DiffCode which holds the result as data and contains methods
        to show the results.
    """
    D = DiffCode(app)
    D.collectWords(otype, feature)
    D.collectCommon(frequencyThreshold=frequencyThreshold, sizeThreshold=sizeThreshold)
    D.collectClose(distThreshold=distThreshold)
    D.computeDiffs()
    return D
