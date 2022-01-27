from abc import ABC, abstractmethod
from simses.commons.utils.utilities import format_float


class State(ABC):

    """
    Basic abstract class for all states in SimSES. States in SimSES are date objects 1) transfering data from one
    object to another and 2) documenting results of simulation. Those written state files are used for the analysis
    of the simulation. There are no cached results in SimSES, all states are written immediately after each simulation
    timestep. The underlying state object in this class is a plain dictonary.
    """

    TIME = 'Time in s'

    def __init__(self):
        self.__state = dict()

    def _initialize(self) -> None:
        """
        Initializes all keys of state class with 0.

        Requirement: Keys have to be written in CAPITAL_LETTERS.

        Returns
        -------
        None:
            None
        """
        for attr in self.__class_attributes():
            self.init_variable(getattr(self, attr))

    @classmethod
    def __class_attributes(cls) -> [str]:
        return [attr for attr in dir(cls) if attr.isupper() and not attr.startswith("_")
                and not callable(getattr(cls, attr))]

    @classmethod
    def header(cls) -> [str]:
        """
        Returns a list of all state keys

        Returns
        -------

        """
        keys: [str] = list()
        for attr in cls.__class_attributes():
            keys.append(getattr(cls, attr))
        return keys
        # return list(self.__state.keys())

    def to_export(self) -> dict:
        """
        Returns a dictionary with a list of all values

        Returns
        -------
        dict:
            values combined with state.
        """
        export_dict: dict = dict()
        key: str = type(self).__name__
        export_dict[key] = {}
        export_dict[key]['DATA'] = self.to_list
        export_dict[key]['TIME'] = self.time
        export_dict[key]['ID'] = self.id
        return export_dict

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    def __str__(self) -> str:
        res = ''
        for val in list(self.__state.values()):
            res += format_float(val) + ','
        return res

    def __repr__(self):
        return self.__str__()

    @property
    def to_list(self) -> list:
        """
        Returns a list of all values of self.state

        Returns
        -------
        list
        """
        return list(self.__state.values())

    @property
    def time(self) -> float:
        """
        Time in s

        Returns
        -------

        """
        return self.get(self.TIME)

    @time.setter
    def time(self, value: float) -> None:
        self.set(self.TIME, value)

    def get(self, key: str) -> float:
        """
        Returns value for key

        Parameters
        ----------
        key : str

        Returns
        -------
        value as float
        """
        return self.__state[key]

    def set(self, key: str, value: float) -> None:
        """
        Sets value to variable of key

        Parameters
        ----------
        key : str
        value : float

        Returns
        -------
        None
        """
        self.__state[key] = value

    def init_variable(self, key: str) -> None:
        """
        Intitalize variable of key with 0.

        Parameters
        ----------
        key : str

        Returns
        -------
        None
        """
        self.set(key, 0)

    def __check_instance_of(self, state) -> None:
        if not isinstance(state, self.__class__):
            raise Exception('State ' + state.__class__.__name__ + ' is not an instance of ' + self.__class__.__name__ +
                            '. Please check state transfer.')

    def add(self, state) -> None:
        """
        Adding all items of state to self.state

        Parameters
        ----------
        state : State

        Returns
        -------
            None
        """
        self.__check_instance_of(state)
        for key in self.__state.keys():
            try:
               self.__state[key] += state.get(key)
            except TypeError as err:
                raise TypeError('Key: ' + key, err)

    def set_all(self, state) -> None:
        """
        Setting all items of state to self.state

        Parameters
        ----------
        state : State

        Returns
        -------
            None
        """
        self.__check_instance_of(state)
        for key in self.__state.keys():
            self.__state[key] = state.get(key)

    def divide_by(self, divisor: float, key=None) -> None:
        """
        Divide all values of self.state by divisor. If a key is provided, only the value for the key is divided.

        Parameters
        ----------
        divisor : float
        key : str

        Returns
        -------
            None
        """
        if divisor == 0:
            raise Exception('Divison by zero')
        if key is None:
            for key in self.__state.keys():
                self.__state[key] /= divisor
        else:
            self.__state[key] /= divisor

    @classmethod
    def sum_reverse(cls, key: str, states: []) -> float:
        """
        Calculation the inverted sum of inverse values (like parallel resistances).

        Parameters
        ----------
        key : str
            Key of the state.
        states : list
            List of states.

        Returns
        -------
        float:
            Summed up value.

        """
        value = 0
        for state in states:
            value += 1 / state.get(key)
        return 1 / value

    @classmethod
    @abstractmethod
    def sum_parallel(cls, states: []):
        """
        Classmethod to calculate the combined state over several states connected in parallel.

        Parameters
        ----------
        states: List
            List of State which are connected in parallel.

        Returns
        -------
        state:
            Combined State over the parallel States.
        """
        pass

    @classmethod
    @abstractmethod
    def sum_serial(cls, states: []):
        """
        Classmethod to calculate the combined state over several states connected in serial.

        Parameters
        ----------
        states: List
            List of State which are connected in serial.

        Returns
        -------
        state:
            Combined State over the serial States.
        """
        pass
