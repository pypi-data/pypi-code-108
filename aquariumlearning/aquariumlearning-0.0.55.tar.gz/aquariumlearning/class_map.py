"""class_map.py
============
The Labeled Class Map and Class Map Entry Modules and corresponding Update Modules.
"""

from math import floor
from .viridis import viridis_rgb
from .turbo import turbo_rgb
from typing import Any, Optional, List, Dict, Tuple, Union, Set


# https://public.tableau.com/profile/chris.gerrard#!/vizhome/TableauColors/ColorPaletteswithRGBValues
tableau_colors = [
    (31, 119, 180),
    (255, 127, 14),
    (44, 160, 44),
    (214, 39, 40),
    (148, 103, 189),
    (140, 86, 75),
    (227, 119, 194),
    (127, 127, 127),
    (188, 189, 34),
    (23, 190, 207),
]

# https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
orig_label_color_list = [
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (67, 99, 216),
    (245, 130, 49),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (188, 246, 12),
    (250, 190, 190),
    (0, 128, 128),
    (230, 190, 255),
    (154, 99, 36),
    (255, 250, 200),
    (128, 0, 0),
    (170, 255, 195),
    (128, 128, 0),
    (255, 216, 177),
    (0, 0, 117),
    (128, 128, 128),
]

# Used as the "step" between consecutive class colors if the number of classes exceeds the number of scheme colors
DEFAULT_COLOR_STEP = 4

UserProvidedColor = Union[Tuple[int, int, int], List[int]]


class ClassMapEntry:
    """A description of how to interpret a classification.

    In the common case, only three values are needed:
    - The string representation of the class
    - The int [0,255] representation of the class
    - What color to render it as.

    In more complex cases, some classes may be ignored in evaluation,
    or collapsed together into a different class at inference time,
    or tracked as part of a larger category.

    Args:
        name (str): The string representation of the class
        class_id (int): The int representation of the class
        color (Union[Tuple[int, int, int], List[int]]): A length 3 list/tuple of RGB int values
        train_name (Optional[int], optional): The string representation of the class that this label will be inferred as. Defaults to None.
        train_id (Optional[str], optional): The int representation of the class that this label will be infererred as. Defaults to None.
        category (Optional[str], optional): The string representation of the parent category. Defaults to None.
        category_id (Optional[int], optional): The int representation of the parent category. Defaults to None.
        has_instances (bool, optional): Whether each label of this class is a separate instance. Defaults to True.
        ignore_in_eval (bool, optional): Whether to ignore this class while evaluating metrics. Defaults to False.
        train_color (Optional[Union[Tuple[int, int, int], List[int]]], optional): A length 3 list/tuple of RGB int values for showing inferences of this class. Defaults to None.
        keypoint_names (Optional[List[str]], optional): List of keypoint names that exist for this class. Indicies of keypoints in this list are used for the skeletons.
        skeleton (Optional[List[Union[Tuple[int, int], List[int]]]], optional): List of integer pairs that reference indicies in keypoint_names that represent the skeleton for this class.
    """

    def __init__(
        self,
        *,
        name: str,
        class_id: int,
        color: UserProvidedColor,
        train_name: Optional[str] = None,
        train_id: Optional[int] = None,
        category: Optional[str] = None,
        category_id: Optional[int] = None,
        has_instances: bool = True,
        ignore_in_eval: bool = False,
        train_color: Optional[UserProvidedColor] = None,
        keypoint_names: Optional[List[str]] = None,
        skeleton: Optional[List[Union[Tuple[int, int], List[int]]]] = None,
    ) -> None:

        # Set defaults for more complex class mapping fields if not set
        if train_name is None:
            train_name = name
        if train_id is None:
            train_id = class_id
        if category is None:
            category = name
        if category_id is None:
            category_id = class_id
        if train_color is None:
            train_color = color

        # Assert on types
        # Names
        if type(name) is not str:
            raise Exception("Argument 'name' must be a string.")
        if type(train_name) is not str:
            raise Exception("Argument 'train_name' must be a string.")
        if type(category) is not str:
            raise Exception("Argument 'category' must be a string.")

        # Class IDs
        if type(class_id) is not int:
            raise Exception("Argument 'class_id' must be an int.")
        if type(train_id) is not int:
            raise Exception("Argument 'train_id' must be an int.")
        if type(category_id) is not int:
            raise Exception("Argument 'category_id' must be an int.")
        if class_id < 0:
            raise Exception("Argument 'class_id' cannot have negative values.")
        if train_id < 0:
            raise Exception("Argument 'train_id' cannot have negative values.")
        if category_id < 0:
            raise Exception("Argument 'category_id' cannot have negative values.")

        # Colors
        if type(color) not in [list, tuple]:
            raise Exception(
                "Argument 'color' must be a list or tuple of ints, in the range [0,255]."
            )
        if type(train_color) not in [list, tuple]:
            raise Exception(
                "Argument 'train_color' must be a list or tuple of ints, in the range [0,255]."
            )
        if len(color) != 3:
            raise Exception("Argument 'color' must have a length of 3.")
        if len(train_color) != 3:
            raise Exception("Argument 'train_color' must have a length of 3.")
        for val in color:
            if (type(val) is not int) or val < 0 or val > 255:
                raise Exception(
                    "Argument 'color' must have integer entries in the range [0,255]."
                )
        for val in train_color:
            if (type(val) is not int) or val < 0 or val > 255:
                raise Exception(
                    "Argument 'train_color' must have integer entries in the range [0,255]."
                )

        # Keypoints skeleton
        if keypoint_names is not None:
            if not isinstance(keypoint_names, list):
                raise Exception("Argument 'keypoint_names' must be a list of strings.")
            for keypoint_name in keypoint_names:
                if not isinstance(keypoint_name, str):
                    raise Exception(
                        "Argument 'keypoint_names' must be a list of strings."
                    )
        if skeleton is not None:
            if keypoint_names is None:
                raise Exception(
                    "Argument 'keypoint_names' cannot be None when using Argument 'skeleton'."
                )
            if not isinstance(skeleton, list):
                raise Exception("Argument 'skeleton' must be a list of integer pairs.")
            for bone in skeleton:
                if type(bone) not in [list, tuple] or len(bone) != 2:
                    raise Exception(
                        "Argument 'skeleton' must be a list of integer pairs."
                    )
                for i in bone:
                    if i >= len(keypoint_names):
                        raise Exception("Index out of range in argument 'skeleton'.")

        self.name = name
        self.class_id = class_id
        self.train_name = train_name
        self.train_id = train_id
        self.category = category
        self.category_id = category_id
        self.has_instances = has_instances
        self.ignore_in_eval = ignore_in_eval
        self.color = list(color)
        self.train_color = list(train_color)
        self.keypoint_names = keypoint_names
        self.skeleton = skeleton

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictified form of this data structure.

        Returns:
            Dict[str, Any]: dict represenation of Class Map Entry
        """
        return {
            "name": self.name,
            "id": self.class_id,
            "train_name": self.train_name,
            "train_id": self.train_id,
            "category": self.category,
            "category_id": self.category_id,
            "has_instances": self.has_instances,
            "ignore_in_eval": self.ignore_in_eval,
            "color": self.color,
            "train_color": self.train_color,
            "keypoint_names": self.keypoint_names,
            "skeleton": self.skeleton,
        }


class LabelClassMap:
    """A collection of ClassMapEntries that defines how to interpret classifications.

    Args:
        entries (list of ClassMapEntry, optional): List of classification entries. Defaults to None.

    """

    @staticmethod
    def from_classnames(classnames: List[str]) -> "LabelClassMap":
        """A helper utility to generate a set of distinct colors given a list of classnames based on
        the number of classes

        Args:
            classnames (List[str]): List of classifications as strings

        Returns:
            LabelClassMap: A LabelClassMap containing categorical colors for the provided classnames.
        """
        if len(classnames) <= 10:
            return LabelClassMap.from_classnames_max10(classnames)
        elif len(classnames) <= 20:
            return LabelClassMap.from_classnames_max20(classnames)
        else:
            return LabelClassMap.from_classnames_turbo(classnames)

    @staticmethod
    def from_classnames_max20(classnames: List[str]) -> "LabelClassMap":
        """A helper utility to generate a set of distinct colors given a list of classnames

        Args:
            classnames (List[str]): List of up to twenty classifications as strings

        Returns:
            LabelClassMap: A LabelClassMap containing categorical colors for the provided classnames.
        """
        if len(classnames) > 20:
            raise Exception("More than 20 classnames were provided.")

        classmap = LabelClassMap()
        for idx, classname in enumerate(classnames):
            entry = ClassMapEntry(
                class_id=idx,
                name=classname,
                color=orig_label_color_list[idx % len(orig_label_color_list)],
            )
            classmap.add_entry(entry)

        return classmap

    @staticmethod
    def from_classnames_max10(classnames: List[str]) -> "LabelClassMap":
        """A helper utility to generate a set of distinct colors given a list of classnames

        Args:
            classnames (list of str): List of up to ten classifications as strings

        Returns:
            LabelClassMap: A LabelClassMap containing categorical colors for the provided classnames.
        """
        if len(classnames) > 10:
            raise Exception("More than 10 classnames were provided.")

        classmap = LabelClassMap()
        for idx, classname in enumerate(classnames):
            entry = ClassMapEntry(
                class_id=idx,
                name=classname,
                color=tableau_colors[idx % len(tableau_colors)],
            )
            classmap.add_entry(entry)

        return classmap

    @staticmethod
    def from_classnames_turbo(classnames: List[str]) -> "LabelClassMap":
        """A helper utility to generate a set of distinct colors given a list of classnames.

        These colors are pulled from the turbo color scheme, and will be assigned
        in order from dark to light.

        Args:
            classnames (list of str): List of classifications as strings.

        Returns:
            LabelClassMap: A LabelClassMap containing colors for the provided classnames.
        """
        classmap = LabelClassMap()
        col_step = max(DEFAULT_COLOR_STEP, floor(len(turbo_rgb) / len(classnames)))

        for idx, classname in enumerate(classnames):
            col_idx = (col_step * idx) % len(turbo_rgb)
            color = turbo_rgb[col_idx]

            entry = ClassMapEntry(class_id=idx, name=classname, color=color)
            classmap.add_entry(entry)

        return classmap

    @staticmethod
    def from_classnames_viridis(classnames: List[str]) -> "LabelClassMap":
        """A helper utility to generate a set of distinct colors given a list of classnames.

        These colors are pulled from the viridis color scheme, and will be assigned
        in order from dark to light.

        Args:
            classnames (list of str): List of classifications as strings.

        Returns:
            LabelClassMap: A LabelClassMap containing colors for the provided classnames.
        """
        classmap = LabelClassMap()
        col_step = max(DEFAULT_COLOR_STEP, floor(len(viridis_rgb) / len(classnames)))

        for idx, classname in enumerate(classnames):
            col_idx = (col_step * idx) % len(viridis_rgb)
            color = viridis_rgb[col_idx]

            entry = ClassMapEntry(class_id=idx, name=classname, color=color)
            classmap.add_entry(entry)

        return classmap

    def __init__(self, *, entries: Optional[List[ClassMapEntry]] = None) -> None:
        self.entries: List[ClassMapEntry] = []
        self._name_set: Set[str] = set()
        self._class_id_set: Set[int] = set()

        if entries is not None:
            for entry in entries:
                self.add_entry(entry)

    def add_entry(self, entry: ClassMapEntry) -> None:
        """Add a ClassMapEntry.

        Args:
            entry (ClassMapEntry): entry
        """
        if not isinstance(entry, ClassMapEntry):
            raise Exception("entry must be a ClassMapEntry")

        if entry.class_id in self._class_id_set:
            raise Exception(f"An entry with class id {entry.class_id} already exists.")
        if entry.name in self._name_set:
            raise Exception(f"An entry with name {entry.name} already exists.")

        self._class_id_set.add(entry.class_id)
        self._name_set.add(entry.name)

        self.entries.append(entry)


class ClassMapUpdateEntry:
    """A description of a change to be made to a classification. Classification can be referred to by name or id

    Args:
        name (Optional[str], optional): The string representation of the class
        class_id (Optional[int], optional): The int representation of the class
        color (Optional[Union[Tuple[int, int, int], List[int]]], optional): A length 3 list/tuple of RGB int values
        train_color (Optional[Union[Tuple[int, int, int], List[int]]], optional): A length 3 list/tuple of RGB int values for showing inferences of this class. Defaults to None.
        keypoint_names (Optional[List[str]], optional): List of keypoint names that exist for this class. Indicies of keypoints in this list are used for the skeletons.
        skeleton (Optional[List[Union[Tuple[int, int], List[int]]]], optional): List of integer pairs that reference indicies in keypoint_names that represent the skeleton for this class.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        class_id: Optional[int] = None,
        color: Optional[UserProvidedColor] = None,
        train_color: Optional[UserProvidedColor] = None,
        keypoint_names: Optional[List[str]] = None,
        skeleton: Optional[List[Union[Tuple[int, int], List[int]]]] = None,
    ) -> None:
        # Assert on types
        # Name
        if name:
            if type(name) is not str:
                raise Exception("Argument 'name' must be a string.")

        # Class ID
        if class_id:
            if type(class_id) is not int:
                raise Exception("Argument 'class_id' must be an int.")
            if class_id < 0:
                raise Exception("Argument 'class_id' cannot have negative values.")

        # Colors
        if color:
            if type(color) not in [list, tuple]:
                raise Exception(
                    "Argument 'color' must be a list or tuple of ints, in the range [0,255]."
                )
            if len(color) != 3:
                raise Exception("Argument 'color' must have a length of 3.")
            for val in color:
                if (type(val) is not int) or val < 0 or val > 255:
                    raise Exception(
                        "Argument 'color' must have integer entries in the range [0,255]."
                    )

        if train_color:
            if type(train_color) not in [list, tuple]:
                raise Exception(
                    "Argument 'train_color' must be a list or tuple of ints, in the range [0,255]."
                )

            if len(train_color) != 3:
                raise Exception("Argument 'train_color' must have a length of 3.")

            for val in train_color:
                if (type(val) is not int) or val < 0 or val > 255:
                    raise Exception(
                        "Argument 'train_color' must have integer entries in the range [0,255]."
                    )

        # Some kind of IDness
        if not name and not class_id:
            raise Exception(
                "ClassMapUpdateEntry must have either a 'name' or 'class_id' argument"
            )

        # Some kind of actual change
        if not color and not train_color:
            raise Exception(
                "ClassMapUpdateEntry must include an update of either 'color' or 'train_color'"
            )

        # Keypoints skeleton
        if keypoint_names is not None:
            if not isinstance(keypoint_names, list):
                raise Exception("Argument 'keypoint_names' must be a list of strings.")
            for keypoint_name in keypoint_names:
                if not isinstance(keypoint_name, str):
                    raise Exception(
                        "Argument 'keypoint_names' must be a list of strings."
                    )
        if skeleton is not None:
            if keypoint_names is None:
                raise Exception(
                    "Argument 'keypoint_names' cannot be None when using Argument 'skeleton'."
                )
            if not isinstance(skeleton, list):
                raise Exception("Argument 'skeleton' must be a list of integer pairs.")
            for bone in skeleton:
                if type(bone) not in [list, tuple] or len(bone) != 2:
                    raise Exception(
                        "Argument 'skeleton' must be a list of integer pairs."
                    )
                for i in bone:
                    if i >= len(keypoint_names):
                        raise Exception("Index out of range in argument 'skeleton'.")

        self.name = name
        self.class_id = class_id
        self.color = color
        self.train_color = train_color
        self.keypoint_names = keypoint_names
        self.skeleton = skeleton

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictified form of this data structure.

        Returns:
            Dict[str, Any]: dict represenation of Class Map Update Entry
        """

        return {
            "name": self.name,
            "id": self.class_id,
            "color": self.color,
            "train_color": self.train_color,
            "keypoint_names": self.keypoint_names,
            "skeleton": self.skeleton,
        }
