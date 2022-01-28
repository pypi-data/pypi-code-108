from typing import Callable, Optional, Sequence, Union

from .oxford_iiit_pet import OxfordIIITPet

__all__ = ["OxfordCatDog"]


class OxfordCatDog(OxfordIIITPet):
    """Oxford IIIT Cat and Dog Dataset."""

    def __init__(
        self,
        root: str,
        split: str = "trainval",
        target_types: Union[Sequence[str], str] = "category",
        return_bbox: bool = False,
        transforms: Optional[Callable] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        download: bool = False,
    ) -> None:

        if return_bbox and "segmentation" not in target_types:
            if isinstance(target_types, str):
                target_types = (
                    target_types,
                    "segmentation",
                )
            else:  # is a sequence e.g. ('category',)
                target_types = list(target_types)
                target_types.append("segmentation")

        super().__init__(
            root,
            split,
            target_types,
            transforms,
            transform,
            target_transform,
            download,
        )

        self.return_bbox = return_bbox
        self.read_me = self._load_readme()
        # load species and breed labels
        self._load_labels()

    def _load_readme(self) -> str:
        with open(self._anns_folder / "README", "r") as f:
            return f.read()

    def _load_labels(self) -> None:

        filenames = []
        general_labels = []
        coarse_labels = []
        fine_labels = []

        self.class_to_idx_tuple = {}
        self.idx_to_name = {}
        self.idx_to_species_breed_idx = {}

        with open(self._anns_folder / "list.txt", "r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith("#"):
                continue
            fn, general, coarse, fine = line.split(" ")

            name = " ".join((w.capitalize() for w in fn.lower().split("_")[:-1]))
            if name not in self.class_to_idx_tuple:
                if int(coarse) - 1 == 0:
                    coarse_name = "Cat"
                elif int(coarse) - 1 == 1:
                    coarse_name = "Dog"
                else:
                    raise ValueError(
                        f"Coarse label should only be 1 or 2 but got {coarse}"
                    )

                name = f"{name}, {coarse_name}"

                self.class_to_idx_tuple[name] = (
                    int(general) - 1,
                    int(coarse) - 1,
                    int(fine) - 1,
                )
                self.idx_to_name[int(general) - 1] = name
                self.idx_to_species_breed_idx[int(general) - 1] = (
                    int(coarse) - 1,
                    int(fine) - 1,
                )

            filenames.append(fn)
            general_labels.append(int(general) - 1)
            coarse_labels.append(int(coarse) - 1)
            fine_labels.append(int(fine) - 1)

        self._filenames = filenames
        self._species_labels = general_labels
        self._breed_labels = fine_labels
        self.species_to_species_idx = {"Cat": 0, "Dog": 1}

        for name, idx_tuple in self.class_to_idx_tuple.items():
            breed, species = name.split(", ")
            if species == "Cat":
                self.cat_breed_to_breed_idx[breed] = idx_tuple[-1]
            else:  # species == 'Dog'
                self.dog_breed_to_breed_idx[breed] = idx_tuple[-1]
