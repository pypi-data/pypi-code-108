from typing import Tuple, Union


class Note:
    """
    0: C
    1: C# = Db
    2: D
    3: D# = Eb
    4: E
    5: F
    6: F# = Gb
    7: G
    8: G# = Ab
    9: A
    10: A# = Bb
    11: B
    """

    def __init__(self, name: str, group: int = 4, move_half: int = 0, beats: Union[int, float] = 1):
        """
        C = C4
        D 5 1 = D5# = E5b
        B 4 -1 = B4b = A4#
        """
        self.group = group
        self.name = name
        self.flat = move_half < 0
        self.sharp = move_half > 0
        self.__beats = beats

    def __as_indexed(self):
        a = self.group
        if self.name == 'C':
            b = 0
        elif self.name == 'D':
            b = 2
        elif self.name == 'E':
            b = 4
        elif self.name == 'F':
            b = 5
        elif self.name == 'G':
            b = 7
        elif self.name == 'A':
            b = 9
        elif self.name == 'B':
            b = 11
        else:
            raise RuntimeError("unknown name")

        if self.flat:
            if b == 0:
                b = 11
                a = a - 1
            else:
                b = b - 1
        elif self.sharp:
            if b == 11:
                b = 0
                a = a + 1
            else:
                b = b + 1
        return a, b,

    @staticmethod
    def __make_note_from_indexed(indexed: Tuple[int, int]):
        group = indexed[0]
        b = indexed[1]
        move_half = 0

        if b == 0:
            name = 'C'
        elif b == 1:
            name = 'D'
            move_half = -1
        elif b == 2:
            name = 'D'
        elif b == 3:
            name = 'E'
            move_half = -1
        elif b == 4:
            name = 'E'
        elif b == 5:
            name = 'F'
        elif b == 6:
            name = 'G'
            move_half = -1
        elif b == 7:
            name = 'G'
        elif b == 8:
            name = 'A'
            move_half = -1
        elif b == 9:
            name = 'A'
        elif b == 10:
            name = 'B'
            move_half = -1
        elif b == 11:
            name = 'B'
        else:
            raise RuntimeError

        return Note(name, group, move_half)

    def get_beats(self):
        return self.__beats

    def get_note_higher(self, distance: int):
        if distance < 0:
            return self.get_note_lower(abs(distance))
        t = self.__as_indexed()
        a = t[0]
        b = t[1]
        for i in range(distance):
            b = b + 1
            if b == 12:
                b = 0
                a = a + 1
        return Note.__make_note_from_indexed((a, b))

    def get_note_lower(self, distance: int):
        if distance < 0:
            return self.get_note_higher(abs(distance))
        t = self.__as_indexed()
        a = t[0]
        b = t[1]
        for i in range(distance):
            if b == 0:
                b = 11
                a = a - 1
            else:
                b = b - 1
        return Note.__make_note_from_indexed((a, b))

    def get_distance_to_another_note(self, another_note):
        """
        X = self - another
        """
        a = self.__as_indexed()
        b = another_note.__as_indexed()

        return (a[0] - b[0]) * 12 + (a[1] - b[1])

    def __get_distance_to_a4(self):
        a = self.__as_indexed()
        return (a[0] - 4) * 12 + (a[1] - 9)

    def get_sound_in_hz(self) -> float:
        """
        f(A4) = 440 Hz
        For any other note X, n=X-A4 (1 for half), f(X)=2^(n/12)*440 Hz
        For Example, if X is C5, n=3 (A4-#-B4-C5), f(C5)=2^(3/12)*440=523.2511306011972 Hz
        """
        distance_to_a4 = self.__get_distance_to_a4()
        return pow(2, distance_to_a4 / 12.0) * 440.0
