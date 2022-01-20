import typing


class PostingList:
    """
    Stores the positions of "postings" of some term for a specific doc_id.

    In practice this is used by the InvertedList to group all occurrences
    of a term for a specific file.
    TODO: ~~MAKE INTO DATACLASS~~ Maintain sorted order via bisect()
    """
    def __init__(
            self,
            doc_id: int,
            postings: typing.List[int] = None,
    ):
        self.doc_id = doc_id
        self.postings = postings if postings else []

    def append(
            self,
            term_position: int,
    ):
        self.postings.append(term_position)

    def to_json(self):
        """Serializes to a dict which can be JSON-ified"""
        return {
            'doc_id': self.doc_id,
            'postings': self.postings,
        }

    @staticmethod
    def from_json(json_data) -> 'PostingList':
        return PostingList(json_data['doc_id'], postings=json_data['postings'])

    def __repr__(self):
        return str(self.postings)
