import os
from typing import Any, Callable, Dict, Optional, Set

import numpy as np
from PIL import Image
from torchvision.datasets import VisionDataset
from torchvision.datasets.utils import download_and_extract_archive

__all__ = ["OxfordCatDog"]


class OxfordCatDog(VisionDataset):
    """
    Oxford IIIT Cat and Dog Dataset.

    Parameters
    ----------
    root : str
        Root directory of the dataset.
    split : str
        Can be `train`, `test`, or `all`.
    mode : Optional[str]
        Can be `label` or `mask` (the default is "label").
    transforms : Optional[Callable]
        Torchvision `StandardTransform`.
    transform : Optional[Callable]
        Image transform.
    target_transform : Optional[Callable]
        Target transform.
    download : bool
        Whether download or not (the default is False).
    """

    _splits: Set[str] = {"train", "test", "all"}
    _modes: Set[str] = {"mask", "label"}
    urls: Dict[str, str] = {
        "images": "https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz",
        "annotations": "https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz",
    }

    def __init__(
        self,
        root: str,
        split: str,
        mode: Optional[str] = "label",
        transforms: Optional[Callable] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        download: bool = False,
    ) -> None:
        super().__init__(root, transforms, transform, target_transform)

        assert split in self._splits

        self.split = split

        self.load_mask = False
        self.load_label = False

        def set_flag(mode):
            assert mode in self._modes
            setattr(self, f"load_{mode}", True)

        if isinstance(mode, str):
            set_flag(mode)
        elif isinstance(mode, (list, tuple, set)):
            for m in mode:
                set_flag(m)
        else:
            raise TypeError(
                f"mode should be str, List[str], Tuple[str], Set[str] but got type {type(mode)}"
            )

        self.mode = mode
        self.image_root = os.path.join(self.root, "images")
        self.annotation_root = os.path.join(self.root, "annotations")

        if download:
            self._download()

        self._load_readme()
        self._load_labels(split)

    def _download(self) -> None:
        for fn, url in self.urls.items():
            download_and_extract_archive(url, download_root=self.root, filename=fn)

    def _load_readme(self) -> None:
        with open(os.path.join(self.annotation_root, "README"), "r") as f:
            self.__doc__ = f.read()

    def _load_labels(self, split: str) -> None:

        filenames = []
        general_labels = []
        coarse_labels = []
        fine_labels = []

        self.name_to_ids = {}
        self.general_id_to_name = {}

        anno_txt = {"all": "list.txt", "train": "trainval.txt", "test": "test.txt"}

        with open(os.path.join(self.annotation_root, anno_txt[split]), "r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith("#"):
                continue
            fn, general, coarse, fine = line.split(" ")

            name = " ".join(fn.lower().split("_")[:-1])
            if name not in self.name_to_ids:
                if int(coarse) - 1 == 0:
                    coarse_name = "cat"
                elif int(coarse) - 1 == 1:
                    coarse_name = "dog"
                else:
                    raise ValueError(
                        f"Coarse label should only be 1 or 2 but got {coarse}"
                    )

                name = f"{name}, {coarse_name}"

                self.name_to_ids[name] = (
                    int(general) - 1,
                    int(coarse) - 1,
                    int(fine) - 1,
                )
                self.general_id_to_name[int(general) - 1] = name

            filenames.append(fn)
            general_labels.append(int(general) - 1)
            coarse_labels.append(int(coarse) - 1)
            fine_labels.append(int(fine) - 1)

        self.filenames = np.array(filenames)
        self.general_labels = np.array(general_labels)
        self.coarse_labels = np.array(coarse_labels)
        self.fine_labels = np.array(fine_labels)

    def __len__(self) -> int:

        return len(self.filenames)

    def __getitem__(self, idx: int) -> Dict[str, Any]:

        fn = self.filenames[idx]
        out = {}

        img = Image.open(os.path.join(self.image_root, fn + ".jpg")).convert("RGB")
        out["image"] = img

        if self.load_mask:
            msk = Image.open(
                os.path.join(self.annotation_root, "trimaps", fn + ".png")
            ).convert("L")
            out["mask"] = msk

        if self.load_label:
            out["general_label"] = self.general_labels[idx]
            out["coarse_label"] = self.coarse_labels[idx]
            out["fine_label"] = self.fine_labels[idx]

        return out if self.transforms is None else self.transforms(out)

    def extra_repr(self) -> str:

        out = []
        INDENT = " " * self.repr_indent
        out.append(INDENT + f"image root: {self.image_root}")
        out.append(INDENT + f"annotation root: {self.annotation_root}")
        out.append(INDENT + f"split: {self.split}")
        out.append(INDENT + f"mode: {self.mode}")

        return "\n".join(out)
