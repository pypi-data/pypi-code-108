import typing
from stefansearch.engine.posting_list import PostingList


class InvertedList:
    def __init__(
            self,
            term: str,
            posting_lists: typing.List[PostingList] = None,
    ):
        # TODO: INVERTEDLISTS MUST REMAIN SORTED. THIS IS A KEY TO EFFICIENT OPERATIONS. LOOK INTO USING BYSECT()
        # TODO: efficiency and other general improvements. Maintain a current pointer and use binary search to move to an arbitrary file
        # NOTE: ONLY ITERATES FORWARD (for now). Call `reset()` between usages.
        self.term = term
        # list of PostingLists RENAME TO SOMETHING ELSE
        self.posting_lists = posting_lists if posting_lists else []
        self.num_docs = len(self.posting_lists)
        self.num_postings = sum([len(posting_list.postings) for posting_list in self.posting_lists])
        self.curr_index = 0

    def reset_pointer(self):
        self.curr_index = 0

    def add_posting(
            self,
            doc_id: int,
            term_position: int,
    ):
        if len(self.posting_lists) == 0:
            self.posting_lists.append(PostingList(doc_id, [term_position]))
            self.num_docs = 1
        elif self.posting_lists[self.curr_index].doc_id == doc_id:
            self.posting_lists[self.curr_index].append(term_position)
        else:
            self.posting_lists.append(PostingList(doc_id, [term_position]))
            self.curr_index += 1
            self.num_docs += 1
        self.num_postings += 1

    def is_finished(self) -> bool:
        return self.curr_index >= self.num_docs

    def get_curr_doc_id(self) -> int:
        return self.posting_lists[self.curr_index].doc_id if self.curr_index < self.num_docs else None

    def has_document(self, doc_id: int) -> bool:
        self.reset_pointer()
        found = self.move_to(doc_id)
        self.reset_pointer()
        return found

    # iterate forward through the list until reaching doc_id >= the given doc_id
    # returns whether the doc_id was found in the list
    def move_to(self, doc_id):
        while self.curr_index < self.num_docs and \
                self.posting_lists[self.curr_index].doc_id < doc_id:
            self.curr_index += 1
        return self.curr_index < self.num_docs and \
                self.posting_lists[self.curr_index].doc_id == doc_id

    # iterate through the list until the next doc_id
    def move_to_next(self):
        self.curr_index += 1
        return self.curr_index < self.num_docs

    def move_past(self, doc_id):
        while self.curr_index < self.num_docs and \
              self.posting_lists[self.curr_index].doc_id <= doc_id:
            self.curr_index += 1

    # get number of term occurrences in the current doc_id
    def get_term_freq(self):
        return len(self.posting_lists[self.curr_index].postings) if self.curr_index < self.num_docs else 0

    def __repr__(self):
        return '{}: curr_index {} / {}, curr_id {}' .format(
            self.term,
            self.curr_index,
            self.num_docs - 1,
            self.posting_lists[self.curr_index].doc_id if self.curr_index < self.num_docs else None,
        )

    # Serializes to a dict which can be JSON-ified
    def to_json(self):
        return {
            'term': self.term,
            'posting_list': [posting_list.to_json() for posting_list in self.posting_lists],
        }

    @staticmethod
    def from_json(json_data):
        return InvertedList(
            term=json_data['term'],
            posting_lists=[PostingList.from_json(p_list) for p_list in json_data['posting_list']],
        )
