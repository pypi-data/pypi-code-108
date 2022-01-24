# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/15 4:09 PM
# LAST MODIFIED ON:
# AIM:
from sentence_spliter.architect.graph_component import Operation
from sentence_spliter.en_cutter.en_sequence import Sequence


class Indolent(Operation):
    def __init__(self, name: str = 'Indolent'):
        super(Indolent, self).__init__(name)

    def run(self, seq: Sequence) -> None:
        return


class EndState(Operation):
    def __init__(self, name: str = 'EndState', min_length: int = -1):
        super(EndState, self).__init__(name)
        self.min_len = min_length

    def run(self, seq: Sequence) -> None:
        # if seq.sentence_start != len(seq):
        #     if seq.sentence_list_idx:
        #         seq.add_to_results()
        #     else:
        #         last = (seq.sentence_start, len(seq))
        #         seq.sentence_list_idx.append(last)
        last_sentence_len = len(seq) - seq.sentence_start
        if seq.sentence_start != len(seq):
            if last_sentence_len > self.min_len or not seq.sentence_list_idx:
                seq.add_to_results()
            else:
                last = seq.sentence_list_idx.pop(-1)
                last = (last[0], len(seq))
                seq.sentence_list_idx.append(last)
        return


class Proceed(Operation):
    def __init__(self, name: str = 'Proceed'):
        super(Proceed, self).__init__(name)

    def run(self, seq: Sequence) -> None:
        seq.next()


class Cut(Operation):
    def __init__(self, name: str = 'Cut'):
        super(Cut, self).__init__(name)

    def run(self, seq: Sequence) -> None:
        return seq.add_to_results()


# ----- long short --- #

class BackToSentenceStart(Operation):
    def __init__(self, name: str = 'BackToSentenceStart'):
        super(BackToSentenceStart, self).__init__(name)

    def run(self, seq: Sequence) -> None:
        seq.i = seq.sentence_start


class ResetNumWords(Operation):
    def __init__(self, name: str = 'RestNumWords'):
        super(ResetNumWords, self).__init__(name)

    def run(self, seq: Sequence) -> None:
        seq.n_words -= 1
        # cnt = 1
        # while cnt > 0:
        #     seq.next()
        #     if seq.word_pattern.match(seq.current_token):
        #         cnt -= 1
