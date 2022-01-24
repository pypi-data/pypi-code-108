"""A premix which creates embeddings followed by a convolution to map the channel count to the desired dimension."""

from __future__ import annotations

import dataclasses as dc
from typing import Optional, Sequence

import torch
import torch.nn as nn

from forecast.models.premix import AbstractPremix, AbstractPremixConfig


class EmbeddingPremix(AbstractPremix):
    """A series of parallel feature embeddings followed by a Conv1D to map the channel count to the desired dimension.

    Note: The output tensor will be transformed such that unmodified features will become the leading features (order
    preserved) with the embeddings concat'd at the end (in the feature dimension).
    """

    config: EmbeddingPremixConfig

    def __init__(self, config: EmbeddingPremixConfig, output_channels: int):
        """Creates an EmbeddingPremix.

        Parameters
        ----------
        config: EmbeddingPremixConfig
            Specifies the feature indices and the corresponding embedding dimensions.
        output_channels: int
            The number of channels in the `torch.Tensor` output from the premix.

        """
        super().__init__(config)
        self._embeddings = nn.ModuleList([nn.Embedding(e.input_dim, e.output_dim) for e in config.embeddings])

        conv_in_ch = config.input_channels - len(config.embeddings) + sum(e.output_dim for e in config.embeddings)
        self._conv = nn.Conv1d(in_channels=conv_in_ch, out_channels=output_channels, kernel_size=1)
        self._output_channels = output_channels

        embed_inds = set(e.feature_index for e in config.embeddings)
        non_embeds = torch.tensor([i for i in range(config.input_channels) if i not in embed_inds])

        # creates the attribute self._non_embed_ind
        # we use a buffer so that it is moved to the same device as the the data
        # this is needed as index_select requires both to be on the same device
        self.register_buffer('_non_embed_ind', non_embeds)

    def forward(self, state: torch.Tensor, future_state: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Applies the embedding + conv layer.

        Parameters
        ----------
        state: torch.Tensor
            The input features to the premix
        future_state: torch.Tensor, optional
            Unused

        Returns
        -------
        torch.Tensor (shape: [BATCH_SIZE, CH_OUT, TS_LENGTH])

        """
        embeds = [e(state[:, c.feature_index, :].long()).transpose(1, 2)
                  for e, c in zip(self._embeddings, self.config.embeddings)]
        out = torch.cat([state.index_select(1, self._non_embed_ind), *embeds], dim=1)
        return self._conv(out)

    @property
    def is_future_conditioned(self) -> bool:
        """An `EmbeddingPremix` layer is not future conditioned."""
        return False

    @property
    def receptive_field(self) -> int:
        """An `EmbeddingPremix` layers has a receptive field of 1."""
        return 1

    @property
    def output_channels(self) -> int:
        """The number of channels in the tensor output from the premix.

        Returns
        -------
        int

        """
        return self._output_channels


@dc.dataclass
class EmbeddingConfig:
    """A configuration for a single embedding.

    Attributes:
    -----------
    feature_index: int
        The feature_index of the feature to be embedded
    input_dim: int
        The number of elements in the input space, represented by an `int` of range [0, input_dim-1]
    output_dim: int
        The dimensionality of the embedding

    """

    feature_index: int
    input_dim: int
    output_dim: int

    def __post_init__(self) -> None:
        """Validates `EmbeddingConfig`."""
        if self.feature_index < 0:
            raise ValueError(f'Feature index must be >= 0, received value of {self.feature_index}')
        if self.input_dim < 2:
            raise ValueError(f'Input dimension for feature f{self.feature_index} < 2 ({self.input_dim})')
        if self.output_dim < 1:
            raise ValueError(f'Output dimension for feature f{self.feature_index} < 1 ({self.output_dim})')


@dc.dataclass
class EmbeddingPremixConfig(AbstractPremixConfig):
    """Config for an `EmbeddingPremix`.

    Attributes:
    -----------
    embeddings: Sequence[EmbeddingConfig]
        A sequence of configs describing the embeddings to be included in the premix

    """

    embeddings: Sequence[EmbeddingConfig]

    def __post_init__(self) -> None:
        """Validates indices and embed_dims."""
        super().__post_init__()

        # ensure all channel indices are valid
        for i, embed in enumerate(self.embeddings):
            ind = embed.feature_index
            if ind >= self.input_channels:
                raise ValueError(f'Requested embedding for input feature {ind} which is >= # of model input channels '
                                 f'({self.input_channels})')

        # ensure no indices are repeated
        inds = [e.feature_index for e in self.embeddings]
        if len(inds) != len(set(inds)):
            from collections import Counter
            repeats = [elem for elem, cnt in Counter(inds).items() if cnt > 1]
            raise ValueError('Multiple embeddings for a single feature is not permitted; '
                             f'requested multiple embeddings for features {repeats}.')

    def create_premix(self, output_channels: int) -> EmbeddingPremix:
        """Creates a `EmbeddingPremix` based on the specified config.

        Parameters:
        -----------
        output_channels: int
            The desired number of output channels of the output conv.

        """
        return EmbeddingPremix(self, output_channels)
