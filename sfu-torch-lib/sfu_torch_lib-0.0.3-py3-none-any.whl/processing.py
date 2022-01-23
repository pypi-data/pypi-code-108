import functools
from typing import Tuple, Sequence, List, Callable, Union, Optional

import numpy as np
import torch
import torchvision.transforms.functional as functional
from torch import Tensor
from torch.nn import Module
from torchvision.transforms import RandomHorizontalFlip, ColorJitter, RandomResizedCrop, RandomRotation, GaussianBlur
from torchvision.transforms.functional import InterpolationMode

import sfu_torch_lib.tree as tree_lib


class ResizeTree(Module):
    def __init__(self, sizes: Sequence[Tuple[int, int]], interpolations: Sequence[InterpolationMode]) -> None:
        super().__init__()

        self.sizes = sizes
        self.interpolations = interpolations

    def forward(self, tree):
        return tree_lib.map_tree(
            lambda image, size, interpolation: functional.resize(image, size, interpolation),
            tree, self.sizes, self.interpolations,
        )


class RandomResizedCropTree(Module):
    def __init__(
            self,
            sizes: Sequence[Tuple[int, int]],
            interpolations: Sequence[InterpolationMode],
            scale: Tuple[float, float] = (0.08, 1.0),
            ratio: Tuple[float, float] = (3. / 4., 4. / 3.),
    ) -> None:

        super().__init__()

        self.sizes = sizes
        self.interpolations = interpolations
        self.scale = scale
        self.ratio = ratio

    def forward(self, tree):
        i, j, h, w = RandomResizedCrop.get_params(tree[0], self.scale, self.ratio)

        tree = tree_lib.map_tree(
            lambda image, size, interpolation: functional.resized_crop(image, i, j, h, w, size, interpolation),
            tree, self.sizes, self.interpolations,
        )

        return tree


class RandomHorizontalFlipTree(RandomHorizontalFlip):
    def forward(self, tree):
        flip = torch.rand(1) < self.p

        tree = tree_lib.map_tree(lambda image: functional.hflip(image) if flip else image, tree)

        return tree


class ColorJitterTree(ColorJitter):
    @staticmethod
    def transform(function_indices, brightness_factor, contrast_factor, saturation_factor, hue_factor, image):
        for function_index in function_indices:
            if function_index == 0 and brightness_factor is not None:
                image = functional.adjust_brightness(image, brightness_factor)
            elif function_index == 1 and contrast_factor is not None:
                image = functional.adjust_contrast(image, contrast_factor)
            elif function_index == 2 and saturation_factor is not None:
                image = functional.adjust_saturation(image, saturation_factor)
            elif function_index == 3 and hue_factor is not None:
                image = functional.adjust_hue(image, hue_factor)

        return image

    def forward(self, tree):
        transform = functools.partial(
            self.transform,
            *self.get_params(self.brightness, self.contrast, self.saturation, self.hue),
        )

        new_images = tree_lib.map_tree(transform, tree)

        return new_images


class ToTensorTree(Module):
    def __init__(self, *dtypes) -> None:
        super().__init__()

        self.dtypes = dtypes

    def forward(self, tree):
        return tree_lib.map_tree(lambda image, dtype: torch.as_tensor(np.array(image, dtype)), tree, self.dtypes)


class EncodeImageTree(Module):
    def __init__(self, means: Optional[Tensor] = None, variances: Optional[Tensor] = None) -> None:
        super().__init__()

        self.means = means
        self.variances = variances

    def transform(self, tensor: Tensor) -> Tensor:
        tensor /= 255
        tensor = torch.permute(tensor, (2, 0, 1))

        if self.means is not None:
            tensor -= self.means[:, None, None]

        if self.variances is not None:
            tensor /= self.variances[:, None, None]

        return tensor

    def forward(self, tree):
        return tree_lib.map_tree(self.transform, tree)


class RandomRotationTree(Module):
    def __init__(
            self,
            degrees: Union[float, Tuple[float, float]],
            interpolations: Sequence[InterpolationMode] = InterpolationMode.BILINEAR,
            expand: bool = False,
            center: Optional[Tuple[float, float]] = None,
            fill: Union[float, List[float]] = 0,
    ) -> None:

        super().__init__()

        self.degrees = [-degrees, degrees] if isinstance(degrees, float) else degrees
        self.interpolations = interpolations
        self.expand = expand
        self.center = center
        self.fill = fill

    def forward(self, tree):
        angle = RandomRotation.get_params(self.degrees)

        new_tree = tree_lib.map_tree(
            lambda image, interpolation: functional.rotate(
                img=image,
                angle=angle,
                interpolation=interpolation,
                expand=self.expand,
                center=self.center,
                fill=self.fill,
            ),
            tree, self.interpolations
        )

        return new_tree


class GaussianBlurTree(GaussianBlur):
    def forward(self, tree):
        sigma = self.get_params(self.sigma[0], self.sigma[1])

        new_tree = tree_lib.map_tree(
            lambda image, : functional.gaussian_blur(image, self.kernel_size, [sigma, sigma]),
            tree
        )

        return new_tree


class SelectTree(Module):
    def __init__(self, paths) -> None:
        super().__init__()

        self.paths = paths

    def forward(self, tree):
        return tree_lib.select_tree(tree, self.paths)


class ComposeTree(Module):
    def __init__(self, steps: List[Tuple[List[int], Callable]]) -> None:
        super().__init__()

        self.steps = steps

    def forward(self, tree):
        for paths, function in self.steps:
            tree = tree_lib.map_tree_subset(function, tree, paths)

        return tree
