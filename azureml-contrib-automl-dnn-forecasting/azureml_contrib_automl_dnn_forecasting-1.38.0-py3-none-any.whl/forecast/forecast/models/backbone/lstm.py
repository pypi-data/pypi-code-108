"""A LSTM-based backbone for forecasting models."""
from __future__ import annotations

import dataclasses as dc
from typing import Optional, Tuple

import torch
import torch.nn as nn

from forecast.models.backbone.base import AbstractBackbone, AbstractBackboneConfig, MultilevelType
from forecast.models.common import StatefulModule


class LSTMBackbone(AbstractBackbone, StatefulModule):
    """A LSTM-based backbone for forecasting models."""

    config: LSTMBackboneConfig

    def __init__(self, config: LSTMBackboneConfig, channels: int, depth: int, dropout_rate: float):
        """Creates an LSTM backbone.

        Parameters
        ----------
        config: LSTMBackboneConfig
            A config specifying the backbone's (scaleless) structure
        channels: int
            The number of channels in the input to the `LSTMBackbone`
        depth: int
            The number of recurrent layers (N > 1 --> a stacked LSTM)
        dropout_rate: float
            The rate at which dropout is applied to all but the final layer of the stacked LSTM

        """
        super().__init__(config)

        self.input_channels = channels
        self.depth = depth
        self.dropout_rate = dropout_rate
        self._receptive_field = self.config.receptive_field
        self._multilevel = MultilevelType[self.config.multilevel]
        self._hidden_channels = round(config.hidden_to_input_channel_ratio * channels)
        self._retained_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None

        self._op = nn.LSTM(input_size=channels,
                           hidden_size=self._hidden_channels,
                           num_layers=depth,
                           batch_first=True,
                           dropout=dropout_rate)

    def forward(self, x: torch.Tensor, future_x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Applies the LSTM backbone to the input tensor.

        Parameters
        ----------
        x: torch.Tensor
            The input to the backbone (output from the premix)
        future_x: None
            Not used

        Returns
        -------
        torch.Tensor

        """
        assert future_x is None, 'LSTMBackbone should not be passed future_x'

        # if we previously retained state, leverage it
        x = x.transpose(1, 2)
        if self.retaining_state and self._retained_state:
            out, state = self._op(x, self._retained_state)
        else:
            out, state = self._op(x)

        # if we should retain state, persist it
        if self.retaining_state:
            self._retained_state = state

        if self._multilevel == MultilevelType.NONE:
            # returned shape will be [batch_size, 1, _hidden_channels]
            return out[:, [-1], :]
        elif self._multilevel == MultilevelType.CELL:
            # returned shape will be [batch_size, 1, _hidden_channels * num_layers]
            return state[0].transpose(0, 1).reshape(x.shape[0], 1, -1).contiguous()
        else:
            raise ValueError(f'`{self._multilevel} not implemented for LSTMBackbone')

    @property
    def receptive_field(self) -> int:
        """The number of time steps prior to the forecasting period which should be passed to the model.

        Returns
        -------
        int

        """
        return self._receptive_field

    @property
    def output_channels(self) -> int:
        """The number of channels in the backbone's output.

        Returns:
        --------
        int

        """
        if self._multilevel == MultilevelType.NONE:
            return self._hidden_channels
        elif self._multilevel == MultilevelType.CELL:
            return self._hidden_channels * self.depth
        else:
            raise ValueError(f'`{self._multilevel} not implemented for LSTMBackbone')

    @property
    def is_future_conditioned(self) -> bool:
        """An LSTM backbone is not future-conditioned.

        Returns:
        --------
        False

        """
        return False

    def reset_state(self) -> None:
        """Resets the retained state of the LSTM.

        Returns:
        --------
        None

        """
        self._retained_state = None

    def export_state(self) -> dict:
        """Exports the LSTM's state.

        Returns
        -------
        dict
            A dict containing hidden and cell states

        """
        if not self._retained_state:
            return {'h': None, 'c': None}
        return {'h': self._retained_state[0],
                'c': self._retained_state[1]}

    def import_state(self, state: dict) -> None:
        """Sets the LSTM's state from the given `dict`.

        Parameters
        ----------
        state: dict
            A mapping containing the cell and hidden state which should be loaded into the LSTM

        Returns
        -------
        None

        """
        h = state.get('h')
        c = state.get('c')
        if h is None or c is None:
            self._retained_state = None
        else:
            self._retained_state = h, c


@dc.dataclass
class LSTMBackboneConfig(AbstractBackboneConfig):
    """A configuration for an LSTM backbone."""

    multilevel: str
    hidden_to_input_channel_ratio: float
    receptive_field: int

    def __post_init__(self) -> None:
        """Validates the inputs to the `LSTMBackboneConfig`."""
        super().__post_init__()

        self.multilevel = self.multilevel.upper()
        if self.multilevel not in MultilevelType.__members__:
            raise ValueError(f'Invalid value "{self.multilevel}" for `multilevel`')
        elif MultilevelType[self.multilevel] not in (MultilevelType.CELL, MultilevelType.NONE):
            raise ValueError(f'`{self.multilevel}` is not implemented for backbone `LSTMBackbone`')

        if self.hidden_to_input_channel_ratio <= 0:
            raise ValueError('`hidden_to_input_channel_ratio` must be positive')

        if self.receptive_field < 2:
            raise ValueError('`receptive_field` must be at least 2')

    def create_backbone(self, input_channels: int, depth: int, dropout_rate: float = 0) -> LSTMBackbone:
        """Creates an `LSTMBackbone` from the config and provided scale parameters.

        Parameters
        ----------
        input_channels: int
            The number of channels in the input to the `LSTMBackbone`
        depth: int
            The number of LSTM cells in the `LSTMBackbone`
        dropout_rate: float
            The rate at which dropout should be applied to the `LSTMBackbone`

        Returns
        -------
        LSTMBackbone

        """
        return LSTMBackbone(self, input_channels, depth, dropout_rate)
