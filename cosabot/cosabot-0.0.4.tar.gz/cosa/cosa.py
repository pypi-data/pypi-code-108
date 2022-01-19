from pathlib import Path
from random import choice
from typing import Optional
from cosa.transform import k_representative_pallette, elastic_transform
from PIL import Image
import numpy as np

FUNCTIONS = {
    "k_rep": k_representative_pallette,
    "elastic": elastic_transform,
}


class Cosa:
    """Main `cosa` class that has the functionality to
    read, transform and save images.
    """

    def __init__(self):
        self.image = None
        self.transformed = None

    def read(self, input_path: str) -> None:
        """Load an image, given a path.
        Args:
            input_path (str): The path to the image that
                will be transformed.

        Returns:
            None
        """
        input_path = Path(input_path)
        if input_path.is_file():
            self.image = np.asarray(Image.open(input_path))
        else:
            raise ValueError(f"File {input_path} does not exist!")

    def transform(self, func: Optional[str] = None, **args) -> None:
        """Transform a loaded image with a given
        functions. If the function is not specified
        one will be chosen randomly.

        Args:
            func (Optional[str]): The name of the function
                that will be applied as a transformation to the
                image.
            **args

        Returns:
            None
        """
        funcs_list = list(FUNCTIONS.keys())
        if func not in funcs_list and func is not None:
            raise ValueError(f"{func} function not supported.")
        if not func:
            func = choice(funcs_list)
        self.transformed = FUNCTIONS[func](image=self.image, **args)

    def write(self, output_path: str) -> None:
        """Write an image in a given path.

        Args:
            output_path (str): The path to the image that
                will be saved after the transformation.

        Returns:
            None
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.transformed is None:
            raise ValueError(
                "There is no image to write! Make sure to load & transform one first."
            )
        self.transformed.save(output_path)
