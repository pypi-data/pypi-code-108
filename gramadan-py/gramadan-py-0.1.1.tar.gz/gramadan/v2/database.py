import sys
import os
from typing import Optional, Union, TypedDict, Iterable
from gramadan.noun import Noun
from gramadan.adjective import Adjective
from gramadan.preposition import Preposition
from gramadan.np import NP
from gramadan.verb import Verb

EntityType = Union[
    Noun,
    Adjective,
    Preposition,
    NP,
    Verb
]

ENTITY_TYPE_MAP = {
    "noun": Noun, "adjective": Adjective, "preposition": Preposition,
    "nounPhrase": NP, "verb": Verb
}

class DatabaseDictionary:

    def __init__(self):
        self.noun: dict[str, Noun] = {}
        self.adjective: dict[str, Adjective] = {}
        self.preposition: dict[str, Preposition] = {}
        self.nounPhrase: dict[str, NP] = {}
        self.verb: dict[str, Verb] = {}

    def __getitem__(self, key):
        if key not in ENTITY_TYPE_MAP:
            raise KeyError()

        return self.__dict__[key]

    def keys(self) -> Iterable[str]:
        return ENTITY_TYPE_MAP.keys()

    def values(self) -> Iterable[dict[str, EntityType]]:
        return (
            self.__dict__[k]
            for k in
            ENTITY_TYPE_MAP.keys()
        )

    def items(self) -> Iterable[tuple[str, dict[str, EntityType]]]:
        return (
            (k, self.__dict__[k])
            for k in
            ENTITY_TYPE_MAP.keys()
        )


class Database:
    def __init__(self, data_location: str):
        self.data_location: str = data_location
        self._dictionary: Optional[DatabaseDictionary] = None

    def load(self) -> None:
        entities: dict[str, type[EntityType]] = ENTITY_TYPE_MAP
        self._dictionary = DatabaseDictionary()
        for folder, entity_type in entities.items():
            root = os.path.join(self.data_location, folder)
            for fn in os.listdir(root):
                word: EntityType = entities[folder].create_from_xml(os.path.join(root, fn))
                self._dictionary[folder][word.getLemma()] = word

    @property
    def dictionary(self) -> DatabaseDictionary:
        if not self._dictionary:
            raise RuntimeError('Load dictionary first')
        return self._dictionary

    def __getitem__(self, pair: tuple[str, str]) -> EntityType:
        return self.dictionary[pair[0]][pair[1]]

    def __len__(self) -> int:
        return sum(map(len, self.dictionary.values()))

if __name__ == "__main__":
    database = Database(sys.argv[1])
    database.load()
    print(len(database), 'entries')
