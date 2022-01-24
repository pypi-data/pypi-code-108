# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines a TabNet model."""

import copy
import dataclasses as dc
import math
from typing import Any, Mapping, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as f

from azureml.automl.runtime.shared._tabularnetworks.ghost_batchnorm import GhostBatchNorm1d
from azureml.automl.runtime.shared._tabularnetworks.sparsemax import sparsemax
from azureml.automl.runtime.shared._tabularnetworks.tabular_nn_constants import (
    CLASSIFICATION,
    REGRESSION,
    SharedBlockTypes,
)


@dc.dataclass
class TabularNNConfig:
    """A spec which determines the Tabular NN's configuration.

    Attributes
    ----------
    model_type: str
        One of 'classification' or 'regression'
    num_steps: int
        The number of decision steps in the model
    input_features: int
        The number of input features
    hidden_features: int
        The number of features within each decision step
    pred_features: int
        The number of features output by each decision step for the regression/classification head to leverage
    out_features: int
        The number of features the model should output
        (e.g., 1 for regression, N for an N-class classification problem)
    relaxation_factor: float
        Controls how many times a feature can be reused (lower --> less frequently reused)
    batchnorm_momentum: float, optional
        The momentum to use for batchnorm, defaults to None (the PyTorch BN default)
    block_depth: int, optional
        The number of transforms within each decision step, defaults to 4
    categorical_features: list, optional
        List with the length of `num_features` where each entry is equal to the number of unique values if the
        corresponding feature is categorical and 0 otherwise. Can also mark categorical features with a 1
        and preprocessing code will determine the number of unique values.
    embedding_dimension: int, optional
        The dimension of the embedding for categorical features
    dropout: float, optional
        The dropout probability to use for dropout after fully connected layers
    num_virtual_batches: int, optional
        A non-None value indicates Ghost BatchNorm should be applied with `num_virtual_batches` virtual batches
    residual: bool, optional
        Boolean indicating whether or not to include the residual network
    default_shared_block: bool, optional
        Boolean indicating whether to use the default shared block or convolutional shared block
    """

    model_type: str
    num_steps: int
    input_features: int
    hidden_features: int
    pred_features: int
    out_features: int
    relaxation_factor: float
    block_depth: int = 4
    batchnorm_momentum: Optional[float] = None
    categorical_features: Optional[list] = None
    embedding_dimension: Optional[int] = None  # if none, recommended based on number of unique values
    dropout: Optional[float] = None
    num_virtual_batches: Optional[int] = None
    residual: Optional[bool] = True
    shared_block_type: Optional[str] = SharedBlockTypes.FC

    def __post_init__(self):
        """Validates the `TabularNNConfig`."""
        self.model_type = self.model_type.lower()
        if self.model_type not in (CLASSIFICATION, REGRESSION):
            raise ValueError(
                "`model_type` must be one of `regression` or `classification`,"
                ' received: "{0}".'.format(self.model_type)
            )

        if self.num_steps < 0:
            raise ValueError("`num_steps` must be non-negative, received: {0}".format(self.num_steps))

        if self.input_features < 1:
            raise ValueError("`input_features` must be >=1, received: {0}".format(self.input_features))

        if self.pred_features < 1:
            raise ValueError("`pred_features` must be >=1, received: {0}".format(self.pred_features))

        if self.hidden_features <= self.pred_features:
            raise ValueError(
                "`hidden_features` must be > `pred_features`, received:"
                "`hidden_features={0}`, `pred_features={1}`".format(self.hidden_features, self.pred_features)
            )

        if self.out_features < 1:
            raise ValueError("`out_features` must be >=1, received: {0}".format(self.out_features))

        if self.relaxation_factor < 1:
            raise ValueError("`relaxation_factor` must be >=1, received: {0}".format(self.relaxation_factor))

        if self.batchnorm_momentum is not None and (self.batchnorm_momentum <= 0 or self.batchnorm_momentum >= 1):
            raise ValueError(
                "`batchnorm_momentum` must be between 0 and 1, received: {0}".format(self.batchnorm_momentum)
            )

        if self.block_depth % 2 != 0:
            raise ValueError("`block_depth` must be a multiple of 2, received: {0}".format(self.block_depth))

        if self.num_virtual_batches is not None and self.num_virtual_batches < 2:
            raise ValueError(
                "`num_virtual_batches` must either be None or >= 2, received: {0}".format(self.num_virtual_batches)
            )

        if self.dropout is not None:
            if self.dropout == 0:
                self.dropout = None
            elif self.dropout < 0 or self.dropout >= 1:
                raise ValueError("`dropout` must be between 0 and 1, received: {0}".format(self.dropout))

        if self.embedding_dimension is not None and self.embedding_dimension < 1:
            raise ValueError(
                "`embedding_dimension` must be >= 1 or None, received: {0}".format(self.embedding_dimension)
            )

        if self.shared_block_type not in SharedBlockTypes.ALL:
            raise ValueError(
                "`shared block type` must be in {0}, recieved: {1}".format(
                    SharedBlockTypes.ALL, self.shared_block_type
                )
            )

    def build(self):  # -> Tabnet
        """Creates a TabNet model from the configuration."""
        return TabNet(self)

    @staticmethod
    def fromdict(d: Mapping[str, Any]):  # -> TabularNNConfig
        """Creates a TabNet configuration from a `dict`."""
        return TabularNNConfig(**d)


def _get_bn(feat: int, mom: Optional[float] = None, num_virtual_batches: Optional[int] = None) -> nn.BatchNorm1d:
    """Conditionally returns BatchNorm1d or GhostBatchNorm1d with the specified momentum.

    Parameters
    ----------
    feat: int
        The number of input features
    mom: Optional[float], optional
        Overrides the (Ghost)BatchNorm1d momentum parameter, defaults to None (default PyTorch setting)
    num_virtual_batches: Optional[int], optional
        If non-None, GhostBatchNorm1d is returned. Defaults to None --> BatchNorm1d

    Returns
    -------
    nn.BatchNorm1d

    """
    # TODO: Batchnorm produces weird results and doesn't help performance
    # for now, removing all batchnorm from the model
    return nn.Identity()
    # below this is unused but kept for now
    if mom:
        if num_virtual_batches:
            return GhostBatchNorm1d(feat, num_virtual_batches, momentum=mom)
        else:
            return nn.BatchNorm1d(feat, momentum=mom)
    else:
        if num_virtual_batches:
            return GhostBatchNorm1d(feat, num_virtual_batches)
        else:
            return nn.BatchNorm1d(feat)


def resid_fn(inp, out):
    return math.sqrt(0.5) * (inp + out)


def pass_through(inp, out):
    return out


class FcBnGlu(nn.Module):
    """The building block of `FeatureTransformer`s in the paper (Linear, BatchNorm, GLU)."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        resid: bool,
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
    ):
        """Creates a (Linear, BatchNorm, GLU) block.

        Parameters
        ----------
        in_features: int
            The number of features passed to the block
        out_features: int
            The number of features returned from the block
        resid: bool
            Is the output a sum the input + transformed data (or simply the transformed data)?
        momentum: Optional[float], optional
            The momentum parameter to use for batchnorm (defaults to None, the PyTorch BN default)
        num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], optional
            The dropout probability to use for dropout after fully connected layers. Defaults to None (no dropout)

        """
        super().__init__()

        # the GLU operation will halve the number of features
        hidden_features = out_features * 2
        self._fc = nn.Linear(in_features, hidden_features, bias=False)
        if dropout is not None:
            self._dropout = nn.Dropout(p=dropout)
            self._fc = nn.Sequential(self._fc, self._dropout)
        self._bn = _get_bn(hidden_features, momentum, num_virtual_batches)
        self._op = resid_fn if resid else pass_through

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the series of operations to the given tensor.

        Parameters
        ----------
        x: torch.Tensor
            The set of features to transform

        Returns
        -------
        torch.Tensor

        """
        # input is of shape B x in_features
        out = self._fc(x)
        out = self._bn(out)
        out = f.glu(out)
        return self._op(x, out)


class DenseBlock(nn.Module):
    """The building block of AutoGluon's Tabular DNN"""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
    ):
        """Creates a (Linear, BatchNorm, GLU) block.

        Parameters
        ----------
        in_features: int
            The number of features passed to the block
        out_features: int
            The number of features returned from the block
        momentum: Optional[float], optional
            The momentum parameter to use for batchnorm (defaults to None, the PyTorch BN default)
        num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], optional
            The dropout probability to use for dropout after fully connected layers. Defaults to None (no dropout)

        """
        super().__init__()

        self._bn = _get_bn(in_features, momentum, num_virtual_batches)
        self._fc = nn.Linear(in_features, out_features, bias=False)
        if dropout is not None:
            self._dropout = nn.Dropout(p=dropout)
            self._fc = nn.Sequential(
                self._dropout,
                self._fc,
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the series of operations to the given tensor.

        Parameters
        ----------
        x: torch.Tensor
            The set of features to transform

        Returns
        -------
        torch.Tensor

        """
        # input is of shape B x in_features
        out = self._bn(x)
        out = self._fc(out)
        out = f.relu(out)
        return out


class ConvBnRelu(nn.Module):
    """
    Alternative to `FeatureTransformer`s in the paper (Conv, BatchNorm, Relu, Conv, BatchNorm, Relu).
    This is helpful for searching through different architectures but not used in the default.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        resid: bool,
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
        kernel: int = 3,
    ):
        """Creates a (Conv, Conv, BatchNorm) block.

        Parameters
        ----------
        in_features: int
            The number of features passed to the block
        out_features: int
            The number of features returned from the block
        resid: bool
            Is the output a sum the input + transformed data (or simply the transformed data)?
        momentum: Optional[float], optional
            The momentum parameter to use for batchnorm (defaults to None, the PyTorch BN default)
        num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], not used but here for consistency
            The dropout probability to use for dropout after fully connected layers. Defaults to None (no dropout)
            not used currently but maintains a consistent api for all of the block components
        kernel: int, optional
            The size of kernels for convolutional layers
        """
        super().__init__()

        # the GLU operation will halve the number of features, mimic behavior here
        hidden_features = out_features * 2
        self._conv = nn.Conv1d(1, hidden_features, kernel, padding=int((kernel - 1) / 2), bias=False)
        self._conv2 = nn.Conv1d(hidden_features, 1, 1, bias=False)

        self._bn = _get_bn(hidden_features, momentum, num_virtual_batches)
        self._bn_2 = _get_bn(out_features, momentum, num_virtual_batches)

        self._op = resid_fn if resid else pass_through

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the series of operations to the given tensor.

        Parameters
        ----------
        x: torch.Tensor
            The set of features to transform

        Returns
        -------
        torch.Tensor
        """
        # input is of shape B x in_features
        out = self._conv(x.unsqueeze(1))
        out = self._bn(out)
        out = f.relu(out)
        out = self._conv2(out)
        out = self._bn_2(out.squeeze(1))
        out = f.relu(out)
        return self._op(x, out)


class DistinctBlock(nn.Module):
    """The half of a `FeatureTransformer` that is unique to each decision step."""

    def __init__(
        self,
        features: int,
        depth: int = 2,
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
    ):
        """Creates the set of operations that is unique to each decision step.

        Parameters
        ----------
        features: int
            The number of features in the block
        depth: int, optional
            The number of (Linear, BN, GLU) units in the block, defaults to 2
        momentum: Optional[float], optional
            The momentum parameter for BatchNorm, defaults to None (the PyTorch BN default)
        num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], optional
            The dropout probability to use for dropout after fully connected layers. Defaults to None (no dropout)
        """
        super().__init__()
        self._units = nn.Sequential(
            *[FcBnGlu(features, features, resid=True, momentum=momentum, dropout=dropout) for _ in range(depth)]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the series of operations to the given tensor.

        Parameters
        ----------
        x: torch.Tensor
            The set of features to transform

        Returns
        -------
        torch.Tensor

        """
        return self._units(x)


class AttentiveTransformer(nn.Module):
    """The component which computes an attention mask based on the previous step's transformed features."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
    ):
        """Creates a TabNet attention block.

        Parameters
        ----------
        in_features: int
            The number of features used to compute the attention
        out_features: int
            The number of features to attend to
        momentum: Optional[float], optional
            The momentum parameter for BatchNorm, defaults to None (the PyTorch BN default)
        num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], optional
            The dropout probability to use for dropout after fully connected layers. Defaults to None (no dropout)
        """
        super().__init__()
        self._fc = nn.Linear(in_features, out_features, bias=False)
        if dropout is not None:
            self._dropout = nn.Dropout(p=dropout)
            self._fc = nn.Sequential(self._fc, self._dropout)
        self._bn = _get_bn(out_features, momentum, num_virtual_batches)

    def forward(self, x: torch.Tensor, prev_mask: torch.Tensor) -> torch.Tensor:
        """Determines the feature attention based on the prior step's features and the previously applied mask.

        Parameters
        ----------
        x: torch.Tensor
            The latter fraction of features from the previous decision step
        prev_mask: torch.Tensor
            The previously applied attention mask

        Returns
        -------
        torch.Tensor
            The attention mask for the input features

        """
        # see section 3.3 of the paper
        out = self._fc(x)
        out = self._bn(out)
        return sparsemax(out * prev_mask)


class EmbeddingBNLayer(nn.Module):
    """Creates an embedding layer followed by a batch norm to handle categorical inputs."""

    def __init__(
        self,
        num_unique: int,
        embedding_dimension: Optional[int],
        momentum: Optional[float] = None,
        num_virtual_batches: Optional[int] = None,
        dropout: Optional[float] = None,
    ):
        """
        Parameters
        ----------
        num_unique: int
            The number of unique categoricals in the feature
        embedding_dimension: int
            The size of the dimension to embed the categorical feature in
        momentum: Optional[float], optional
            The momentum parameter for BatchNorm, defaults to None (the PyTorch BN default)
         num_virtual_batches: Optional[int], optional
            If non-None, use Ghost BatchNorm instead. Defaults to None (BatchNorm)
        dropout: Optional[float], optional
            The dropout probability to use for dropout after embedding layers. Defaults to None (no dropout)
        """
        super().__init__()
        # adding the use of padding_idx can be used to not cause errors when encountering unseen classses
        self._embedding = nn.Embedding(
            num_unique,
            self._suggest_embedding_dimension(num_unique) if embedding_dimension is None else embedding_dimension,
            padding_idx=None,
        )
        self.embedding_dim = self._embedding.embedding_dim
        if dropout is not None:
            self._dropout = nn.Dropout(p=dropout)
            self._embedding = nn.Sequential(self._embedding, self._dropout)
        self._bn = _get_bn(embedding_dimension, momentum, num_virtual_batches)

    def _suggest_embedding_dimension(self, num_unique: int) -> int:
        # based off autogluon's approach
        if num_unique <= 3:
            return 1
        else:
            num_rec = int(min(max(1, 1.6 * num_unique ** 0.56), 100))
            # avoid making huge embedding tables
            if num_rec * num_unique > 1e6:
                num_rec = int(max(1, 1e6 // num_unique))
            return num_rec

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Transform the categorical feature

        Parameters
        ----------
        x: torch.Tensor
            The categorical feature to transform. The features must be 0 indexed with no gaps.
        Returns
        -------
        torch.Tensor
            The categorical feature after embedding
        """
        out = self._embedding(x)
        out = self._bn(out)
        return out


class SqueezeOutput(nn.Module):
    """Used to remove a dimension from a tensor, needed in the output of regression models."""

    def __init__(self):
        super().__init__()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Premove a dimension from a tensor.
        Parameters
        ----------
        x: torch.Tensor
            The tensor to be squeezed
        Returns
        -------
        torch.Tensor
            The tensor in fewer dimensions
        """
        return x.squeeze()


class TabularOutputLayer(nn.Module):
    """Create the predictor and outputs the correct shape."""

    def __init__(
        self, pred_features: int, out_features: int, model_type: str = CLASSIFICATION, dropout: Optional[float] = None
    ):
        """
        Transform the categorical feature

        Parameters
        ----------
        pred_features: int
            Number of features to use in prediction
        out_features: int
            Number of classes to predict, 1 for regression
        model_type: str, optional
            Type of model, one of {"classification", "regression"}
        dropout: float, optional
            dropout to be applied before the linear layer
        """
        super().__init__()
        self._model_type = model_type
        self._is_regression = model_type == REGRESSION
        self.head = nn.Linear(pred_features, out_features, bias=self._is_regression)
        if dropout:
            self.head = nn.Sequential(*[nn.Dropout(dropout), self.head])

        self.out_features = out_features
        self.pred_features = pred_features
        if self._is_regression:
            # dimensions need to match the dimensions of the targets which are one dimensional
            self.head = nn.Sequential(*[self.head, SqueezeOutput()])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict from the last layer

        Parameters
        ----------
        x: torch.Tensor
            The feature to use for prediction.
        Returns
        -------
        torch.Tensor
            The prediction
        """
        return self.head(x)


class TabularInputFeaturizer(nn.Module):
    """
    Creates a module to handle embedding and normalizing tabular input
    """

    def __init__(self, config: TabularNNConfig, return_embedding: bool = False):
        """
        Creates the TabularInputFeaturizer from the configuration.

        Parameters
        ----------
        config: TabularNNConfig
            The configuration spec for the model
        return_embedding:
            Whether the forward should return the orginal numeric columns or columns after featurization
        """
        super().__init__()
        self.categorical_features = config.categorical_features
        if config.categorical_features is not None:
            self.categorical_features = torch.tensor(config.categorical_features)

        # allow categorical columns to be featurized via embedding dimensions
        # do this first because it impacts the in_feature size
        if self.categorical_features is not None:
            self._embedding_indices = torch.where(self.categorical_features > 0)[0]
            self._continuous_features = self.categorical_features.clone().detach()
            self._continuous_features = self._continuous_features == 0
            self.num_cat = self._embedding_indices.shape[0]
        else:
            self.num_cat = 0
            self._continuous_features = torch.ones((config.input_features,), dtype=torch.bool)
        if self.num_cat > 0:
            embedding_dimension = config.embedding_dimension
            self._embedding = nn.ModuleList(
                [
                    EmbeddingBNLayer(
                        num_unique,
                        embedding_dimension,
                        dropout=config.dropout,
                        num_virtual_batches=config.num_virtual_batches,
                    )
                    for num_unique in self.categorical_features
                    if num_unique != 0
                ]
            )
            self._total_embedding_size = sum([embed.embedding_dim for embed in self._embedding])
        else:
            self._total_embedding_size = 0
            self._embedding = None

        self.num_con = config.input_features - self.num_cat
        self._in_features = self.num_con + self._total_embedding_size

        if self.num_con > 0:
            # apply batchnorm to continuous features
            # paper references not using virtual batches for the input featurizer
            # input features for non streaming datasets can also be normalized easily
            self._bn = _get_bn(self.num_con, config.batchnorm_momentum)
        else:
            self._bn = None

        # prepare for connection to output, directly makes a prediction
        self._residual = config.residual
        self._return_embedding = return_embedding
        self._out_features = config.out_features
        if self.num_con > 0 and (self._residual or self._return_embedding):
            # this breaks the interpretability
            # consider using a different embedding dimension instead of into num_con
            self._dense = nn.Sequential(*[nn.Linear(self.num_con, self.num_con), nn.ReLU()])
        else:
            self._dense = None
        if self._residual:
            self._dense_to_output = nn.Linear(
                self._in_features, self._out_features, bias=config.model_type == REGRESSION
            )
            if config.model_type == REGRESSION:
                # dimensions need to match the dimensions of the targets which are one dimensional
                self._dense_to_output = nn.Sequential(*[self._dense_to_output, SqueezeOutput()])
        else:
            self._dense_to_output = None

    def get_input_size(self) -> int:
        """
        Returns the size of the input after embedding

        Returns
        -------
        torch.Tensor
            the transformed input features

        """
        return self._in_features

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Applies the featurizer to the input data.

        Parameters
        ----------
        x: torch.Tensor
            The features to transform

        Returns
        -------
        torch.Tensor
            the transformed input features

        """
        if self.num_cat > 0:
            x_cat = [
                self._embedding[i](x[:, emb_index].to(torch.long))
                for i, emb_index in enumerate(self._embedding_indices)
            ]
            x_cat_total = torch.cat(x_cat, 1)
            if self.num_con > 0:
                x_con = self._bn(x[:, self._continuous_features])
                x = torch.cat([x_con, x_cat_total], 1)
                if self._dense is not None:
                    out = self._dense(x_con)
                    embedding = torch.cat([out, x_cat_total], 1)
            else:
                x = x_cat_total
                embedding = x  # otherwise embedding ends up as None
        else:
            x = self._bn(x)
            if self._dense is not None:
                embedding = self._dense(x)
            else:
                embedding = None
        # AutoGluon recommends a direction connection of input to output
        if self._residual:
            if embedding is not None:
                out = self._dense_to_output(embedding)
            else:
                out = self._dense_to_output(x)
        else:
            out = None
        if self._return_embedding:
            return embedding, out
        return x, out


class AutoGluonTabularNN(nn.Module):
    """
    The AutoGluon model
    https://github.com/awslabs/autogluon/tree/master/autogluon/utils/tabular/ml/models/tabular_nn
    """

    def __init__(self, config: TabularNNConfig):
        """Creates the AutoGluonTabularNN model from the configuration.

        Parameters
        ----------
        config: TabularNNConfig
            The configuration spec for the model

        """
        super().__init__()
        self.config = copy.deepcopy(config)

        # in_features = config.input_features not needed because the input featurizer gets it from the config
        h_features = config.hidden_features
        pred_features = config.pred_features
        out_features = config.out_features
        # batchnorm not currently used by keep these for now
        mom = config.batchnorm_momentum
        num_vb = config.num_virtual_batches

        dropout = config.dropout

        self.model_type = config.model_type

        # return embedding here
        self._input_featurizer = TabularInputFeaturizer(config, return_embedding=True)
        # account for categorical embeddings
        self._in_features = self._input_featurizer.get_input_size()

        # create the dense blocks
        self._dense_0 = DenseBlock(
            self._in_features, h_features, momentum=mom, num_virtual_batches=num_vb, dropout=dropout
        )
        self._dense_1 = DenseBlock(
            h_features, pred_features, momentum=mom, num_virtual_batches=num_vb, dropout=dropout
        )

        self._head = TabularOutputLayer(pred_features, out_features, model_type=config.model_type, dropout=dropout)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies the model to the feature data.

        Parameters
        ----------
        x: torch.Tensor
            The features for prediction

        Returns
        -------
        torch.Tensor
            A tuple containing the unnormalized logits

        """
        x, pred = self._input_featurizer(x)
        x = self._dense_0(x)
        x = self._dense_1(x)
        out = self._head(x)
        if pred is None:
            return out
        else:
            return pred + out

    def is_classification(self) -> bool:
        """
        Determines if the model is a classification model.

        Returns
        -------
        bool
            boolean indicating if the model is a classification model

        """
        return self.model_type == CLASSIFICATION


class TabNet(nn.Module):
    """The TabNet model (see https://arxiv.org/pdf/1908.07442.pdf for more details)."""

    def __init__(self, config: TabularNNConfig):
        """Creates the TabNet model from the configuration.

        Parameters
        ----------
        config: TabularNNConfig
            The configuration spec for the model

        """
        super().__init__()
        self.config = copy.deepcopy(config)

        self.num_steps = config.num_steps
        # in_features = config.input_features not needed because the input featurizer gets it from the config
        h_features = config.hidden_features
        pred_features = config.pred_features
        out_features = config.out_features
        # batchnorm not currently used by keep these for now
        mom = config.batchnorm_momentum
        num_vb = config.num_virtual_batches

        dropout = config.dropout

        self.model_type = config.model_type

        self._input_featurizer = TabularInputFeaturizer(config)
        # account for categorical embeddings
        self._in_features = self._input_featurizer.get_input_size()

        # construct our N feature transformers
        # the first half of the units in a given feature transformer are shared across all feature transformers
        # the second half of the units are unique to that feature transformer
        # allow for just the shortcut network
        if self.num_steps > 0:
            self._shared = self._create_shared_block(config)
            self._distinct = self._create_distinct_block(config)

            # we leverage the remaining hidden_features - pred_features to learn where to attend
            # we pad with an identity, which is unused, to ensure len(_attention) == len(_distinct)
            self._attention = nn.ModuleList(
                [
                    AttentiveTransformer(h_features - pred_features, self._in_features, mom, num_vb, dropout=dropout)
                    for _ in range(self.num_steps - 1)
                ]
            )
            self._attention.append(nn.Identity())
            # no dropout here
            self._head = TabularOutputLayer(pred_features, out_features, model_type=config.model_type)
        else:
            self._shared = None
            self._distinct = None
            self._attention = None
            self._head = None

    def _create_shared_block(self, config) -> nn.Module:
        """Creates the TabNet shared_block from the configuration.

        Parameters
        ----------
        config: TabularNNConfig
            The configuration spec for the model

        Returns
        -------
        nn.module
            The shared components across tabnet steps
        """
        if config.shared_block_type == SharedBlockTypes.FC:
            shared_block = nn.Sequential(
                *[
                    FcBnGlu(
                        self._in_features if i == 0 else config.hidden_features,
                        config.hidden_features,
                        i != 0,
                        momentum=config.batchnorm_momentum,
                        dropout=config.dropout,
                        num_virtual_batches=config.num_virtual_batches,
                    )
                    for i in range(config.block_depth // 2)
                ]
            )
        elif config.shared_block_type == SharedBlockTypes.CONV:
            shared_block = nn.Sequential(
                *(
                    [
                        FcBnGlu(
                            self._in_features,
                            config.hidden_features,
                            False,
                            momentum=config.batchnorm_momentum,
                            dropout=config.dropout,
                            num_virtual_batches=config.num_virtual_batches,
                        )
                    ]
                    + [
                        ConvBnRelu(
                            config.hidden_features,
                            config.hidden_features,
                            True,
                            momentum=config.batchnorm_momentum,
                            dropout=config.dropout,
                            num_virtual_batches=config.num_virtual_batches,
                            kernel=5,
                        )
                        for i in range((config.block_depth // 2) - 1)
                    ]
                )
            )
        return shared_block

    def _create_distinct_block(self, config) -> nn.Module:
        """Creates the TabNet distinct_block from the configuration.

        Parameters
        ----------
        config: TabularNNConfig
            The configuration spec for the model

        Returns
        -------
        nn.module
            The distinct components across tabnet steps
        """
        return nn.ModuleList(
            [
                DistinctBlock(
                    config.hidden_features,
                    config.block_depth // 2,
                    momentum=config.batchnorm_momentum,
                    dropout=config.dropout,
                    num_virtual_batches=config.num_virtual_batches,
                )
                for _ in range(config.num_steps)
            ]
        )

    def is_classification(self) -> bool:
        """
        Determines if the model is a classification model.

        Returns
        -------
        bool
            boolean indicating if the model is a classification model

        """
        return self.model_type == CLASSIFICATION

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies the model to the feature data.

        Parameters
        ----------
        x: torch.Tensor
            The features for prediction

        Returns
        -------
        (torch.Tensor, torch.tensor)
            A tuple containing the unnormalized logits and the sparsity regularizer

        """
        batch_size = x.shape[0]
        pred_feat = self.config.pred_features

        # connection straight from input to output helps performance but is not in original implementation
        x, pred = self._input_featurizer(x)
        # just the shortcut network
        if self.num_steps == 0:
            if self.training:
                return pred, torch.tensor(0.0, device=x.device, dtype=x.dtype)
            else:
                return pred
        masked_feats = feats = x

        out = torch.zeros(batch_size, pred_feat, device=x.device, dtype=x.dtype)
        agg_mask = torch.ones_like(x, device=x.device, dtype=x.dtype)
        reg = torch.tensor(0.0, device=x.device, dtype=x.dtype)
        for i, (distinct, attention) in enumerate(zip(self._distinct, self._attention)):
            # feature transformer
            masked_feats = self._shared(masked_feats)
            masked_feats = distinct(masked_feats)

            # split transformed features/add to output
            if i > 0:
                # split the first N features for prediction
                # the remaining features will be used to compute the next mask
                for_pred = f.relu(masked_feats[:, :pred_feat])
                out += for_pred

            # compute the feature attention for the next step
            # no need to compute the mask for the last step as there will be no remaining steps
            if i < len(self._distinct) - 1:
                mask = attention(masked_feats[:, pred_feat:], agg_mask)
                agg_mask = agg_mask * (self.config.relaxation_factor - mask)

                # per the paper, we regularize by averaging over the batch and summing over the features
                reg = reg + torch.mean(torch.sum(-mask * torch.log(mask + 0.00001), dim=1)) / (
                    self.config.num_steps - 1
                )

                # mask the features for the next step
                masked_feats = mask * feats

        out = self._head(out)
        if pred is not None:
            out = out + pred
        if self.training:
            return out, reg
        else:
            # no need for reg during eval
            return out
