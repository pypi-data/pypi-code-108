import re
import typing


__all__ = ["Properties"]


class Properties:
    """
    Parse properties file.
    """
    def __init__(self):
        self.__loaded: bool = False
        self.__load_arg: str = ""
        self.__data: dict = {}

    def __setitem__(self, name, value) -> None:
        """
        Setting the value of a property.

        :param name: Property name.
        :param value: Value to set for the property.
        """
        self.set_property(name, value)

    def __getitem__(self, name) -> str:
        """
        Getting the value of a property.

        :param name: Property name.
        :exception KeyError: When property does not exist.
        :return: Property Value.
        """
        return self.get_property(name)

    def __delitem__(self, name) -> None:
        """
        Deleting the value of a property.

        :param name: Property name.
        :exception KeyError: When property does not exist.
        """
        self.delete_property(name)

    def __len__(self) -> int:
        """
        Get the number of properties.

        :return: The number of properties.
        """
        return len(self.__data)

    def __iter__(self) -> typing.Iterator:
        """
        Get an iterator object.

        :return: Iterator object.
        """
        return iter(self.__data.keys())

    def load(self, file_name: str) -> None:
        """
        Load data from .properties file.

        :param file_name: .properties file name.
        :exception TypeError: When an error occurs while parsing data.
        :exception IOError: When an error occurs while reading the file.
        """
        if self.__loaded:
            self.save(self.__load_arg)
        self.__data.clear()
        try:
            with open(file=file_name, mode="r", encoding="utf-8") as f:
                raw = re.split("(?<!\\\\)=", re.sub("#.+\n", "", f.read()))
                self.__data = dict(zip(raw[::2], raw[1::2]))
        except TypeError:
            raise TypeError("An error occurred while parsing data.")
        except IOError:
            raise IOError("An error occurred while reading the file.")
        self.__loaded = True
        self.__load_arg = file_name

    def save(self, file_name: str = None) -> None:
        """
        Save data in .properties file.

        :param file_name: .properties file name.
        :exception IOError: When an error occurs while writing data.
        """
        if file_name is None and not self.__loaded:
            raise IOError("Cannot create a file without a file name.")
        try:
            with open(file=self.__load_arg if file_name is None else file_name,
                      mode="w", encoding="utf-8") as f:
                raw = "\n".join([f"{i[0]}={i[1]}" for i in self.__data.items()])
                f.write(raw)
        except IOError:
            raise IOError("An error occurred while writing data.")

    def set_property(self, name: str, value: str) -> None:
        """
        Setting the value of a property.

        :param name: Property name.
        :param value: Value to set for the property.
        """
        self.__data[name] = value.replace("=", "\\=")

    def get_property(self, name: str) -> str:
        """
        Getting the value of a property.

        :param name: Property name.
        :exception KeyError: When property does not exist.
        :return: Property Value.
        """
        try:
            return self.__data[name].replace("\\=", "=")
        except KeyError:
            raise KeyError("Property does not exist.")

    def delete_property(self, name: str) -> None:
        """
        Deleting the value of a property.

        :param name: Property name.
        :exception KeyError: When property does not exist.
        """
        try:
            del self.__data[name]
        except KeyError:
            raise KeyError("Property does not exist.")

    def list(self) -> typing.List[str]:
        """
        Getting the list of properties name.

        :return: List of properties name.
        """
        return list(self.__data)
