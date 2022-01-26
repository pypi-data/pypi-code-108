# Copyright 2019,2020,2021 Sony Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Backward function
from .backward_function.affine import affine_backward
from .backward_function.rnn import rnn_backward
from .backward_function.lstm import lstm_backward
from .backward_function.gru import gru_backward
from .backward_function.convolution import convolution_backward
from .backward_function.fused_convolution import fused_convolution_backward
from .backward_function.depthwise_convolution import depthwise_convolution_backward
from .backward_function.deconvolution import deconvolution_backward
from .backward_function.depthwise_deconvolution import depthwise_deconvolution_backward
from .backward_function.deformable_convolution import deformable_convolution_backward
from .backward_function.adaptive_separable_convolution import adaptive_separable_convolution_backward
from .backward_function.max_pooling import max_pooling_backward
from .backward_function.average_pooling import average_pooling_backward
from .backward_function.global_average_pooling import global_average_pooling_backward
from .backward_function.sum_pooling import sum_pooling_backward
from .backward_function.unpooling import unpooling_backward
from .backward_function.embed import embed_backward
from .backward_function.roi_align import roi_align_backward
from .backward_function.sigmoid import sigmoid_backward
from .backward_function.swish import swish_backward
from .backward_function.tanh import tanh_backward
from .backward_function.relu import relu_backward
from .backward_function.leaky_relu import leaky_relu_backward
from .backward_function.softmax import softmax_backward
from .backward_function.log_softmax import log_softmax_backward
from .backward_function.elu import elu_backward
from .backward_function.selu import selu_backward
from .backward_function.crelu import crelu_backward
from .backward_function.celu import celu_backward
from .backward_function.prelu import prelu_backward
from .backward_function.gelu import gelu_backward
from .backward_function.mish import mish_backward
from .backward_function.relu6 import relu6_backward
from .backward_function.hard_sigmoid import hard_sigmoid_backward
from .backward_function.hard_tanh import hard_tanh_backward
from .backward_function.log_sigmoid import log_sigmoid_backward
from .backward_function.softplus import softplus_backward
from .backward_function.softsign import softsign_backward
from .backward_function.tanh_shrink import tanh_shrink_backward
from .backward_function.sinc import sinc_backward
from .backward_function.fused_batch_normalization import fused_batch_normalization_backward
from .backward_function.batch_normalization import batch_normalization_backward
from .backward_function.group_normalization import group_normalization_backward
from .backward_function.instance_normalization import instance_normalization_backward
from .backward_function.layer_normalization import layer_normalization_backward
from .backward_function.norm_normalization import norm_normalization_backward
from .backward_function.sync_batch_normalization import sync_batch_normalization_backward
from .backward_function.tensor_normalization import tensor_normalization_backward
from .backward_function.weight_normalization import weight_normalization_backward
from .backward_function.weight_standardization import weight_standardization_backward
from .backward_function.spectral_norm import spectral_norm_backward
from .backward_function.mean_subtraction import mean_subtraction_backward
from .backward_function.clip_grad_by_value import clip_grad_by_value_backward
from .backward_function.clip_grad_by_norm import clip_grad_by_norm_backward
from .backward_function.sum import sum_backward
from .backward_function.cumsum import cumsum_backward
from .backward_function.mean import mean_backward
from .backward_function.max import max_backward
from .backward_function.min import min_backward
from .backward_function.norm import norm_backward
from .backward_function.prod import prod_backward
from .backward_function.cumprod import cumprod_backward
from .backward_function.reduce_sum import reduce_sum_backward
from .backward_function.reduce_mean import reduce_mean_backward
from .backward_function.add2 import add2_backward
from .backward_function.add_n import add_n_backward
from .backward_function.bc_add2 import bc_add2_backward
from .backward_function.sub2 import sub2_backward
from .backward_function.mul2 import mul2_backward
from .backward_function.mul_n import mul_n_backward
from .backward_function.div2 import div2_backward
from .backward_function.pow2 import pow2_backward
from .backward_function.add_scalar import add_scalar_backward
from .backward_function.mul_scalar import mul_scalar_backward
from .backward_function.pow_scalar import pow_scalar_backward
from .backward_function.r_sub_scalar import r_sub_scalar_backward
from .backward_function.r_div_scalar import r_div_scalar_backward
from .backward_function.r_pow_scalar import r_pow_scalar_backward
from .backward_function.sign import sign_backward
from .backward_function.minimum2 import minimum2_backward
from .backward_function.maximum2 import maximum2_backward
from .backward_function.minimum_scalar import minimum_scalar_backward
from .backward_function.maximum_scalar import maximum_scalar_backward
from .backward_function.logical_and import logical_and_backward
from .backward_function.logical_or import logical_or_backward
from .backward_function.logical_xor import logical_xor_backward
from .backward_function.equal import equal_backward
from .backward_function.not_equal import not_equal_backward
from .backward_function.greater_equal import greater_equal_backward
from .backward_function.greater import greater_backward
from .backward_function.less_equal import less_equal_backward
from .backward_function.less import less_backward
from .backward_function.searchsorted import searchsorted_backward
from .backward_function.logical_and_scalar import logical_and_scalar_backward
from .backward_function.logical_or_scalar import logical_or_scalar_backward
from .backward_function.logical_xor_scalar import logical_xor_scalar_backward
from .backward_function.equal_scalar import equal_scalar_backward
from .backward_function.not_equal_scalar import not_equal_scalar_backward
from .backward_function.greater_equal_scalar import greater_equal_scalar_backward
from .backward_function.greater_scalar import greater_scalar_backward
from .backward_function.less_equal_scalar import less_equal_scalar_backward
from .backward_function.less_scalar import less_scalar_backward
from .backward_function.logical_not import logical_not_backward
from .backward_function.isnan import isnan_backward
from .backward_function.isinf import isinf_backward
from .backward_function.reset_nan import reset_nan_backward
from .backward_function.reset_inf import reset_inf_backward
from .backward_function.where import where_backward
from .backward_function.constant import constant_backward
from .backward_function.arange import arange_backward
from .backward_function.linspace import linspace_backward
from .backward_function.abs import abs_backward
from .backward_function.exp import exp_backward
from .backward_function.log import log_backward
from .backward_function.identity import identity_backward
from .backward_function.batch_matmul import batch_matmul_backward
from .backward_function.round import round_backward
from .backward_function.ceil import ceil_backward
from .backward_function.floor import floor_backward
from .backward_function.sin import sin_backward
from .backward_function.cos import cos_backward
from .backward_function.tan import tan_backward
from .backward_function.sinh import sinh_backward
from .backward_function.cosh import cosh_backward
from .backward_function.asin import asin_backward
from .backward_function.acos import acos_backward
from .backward_function.atan import atan_backward
from .backward_function.atan2 import atan2_backward
from .backward_function.asinh import asinh_backward
from .backward_function.acosh import acosh_backward
from .backward_function.atanh import atanh_backward
from .backward_function.concatenate import concatenate_backward
from .backward_function.split import split_backward
from .backward_function.stack import stack_backward
from .backward_function.slice import slice_backward
from .backward_function.pad import pad_backward
from .backward_function.transpose import transpose_backward
from .backward_function.broadcast import broadcast_backward
from .backward_function.broadcast_to import broadcast_to_backward
from .backward_function.tile import tile_backward
from .backward_function.one_hot import one_hot_backward
from .backward_function.flip import flip_backward
from .backward_function.shift import shift_backward
from .backward_function.sort import sort_backward
from .backward_function.reshape import reshape_backward
from .backward_function.matrix_diag import matrix_diag_backward
from .backward_function.matrix_diag_part import matrix_diag_part_backward
from .backward_function.meshgrid import meshgrid_backward
from .backward_function.batch_det import batch_det_backward
from .backward_function.batch_inv import batch_inv_backward
from .backward_function.batch_logdet import batch_logdet_backward
from .backward_function.assign import assign_backward
from .backward_function.gather import gather_backward
from .backward_function.gather_nd import gather_nd_backward
from .backward_function.bool_gather import bool_gather_backward
from .backward_function.scatter_nd import scatter_nd_backward
from .backward_function.scatter_add import scatter_add_backward
from .backward_function.bool_scatter import bool_scatter_backward
from .backward_function.bool_fill import bool_fill_backward
from .backward_function.pack_padded_sequence import pack_padded_sequence_backward
from .backward_function.pad_packed_sequence import pad_packed_sequence_backward
from .backward_function.interpolate import interpolate_backward
from .backward_function.fft import fft_backward
from .backward_function.ifft import ifft_backward
from .backward_function.stft import stft_backward
from .backward_function.istft import istft_backward
from .backward_function.dropout import dropout_backward
from .backward_function.top_k_data import top_k_data_backward
from .backward_function.top_k_grad import top_k_grad_backward
from .backward_function.rand import rand_backward
from .backward_function.randint import randint_backward
from .backward_function.randn import randn_backward
from .backward_function.rand_binomial import rand_binomial_backward
from .backward_function.rand_beta import rand_beta_backward
from .backward_function.rand_gamma import rand_gamma_backward
from .backward_function.random_choice import random_choice_backward
from .backward_function.random_crop import random_crop_backward
from .backward_function.random_flip import random_flip_backward
from .backward_function.random_shift import random_shift_backward
from .backward_function.random_erase import random_erase_backward
from .backward_function.image_augmentation import image_augmentation_backward
from .backward_function.sigmoid_cross_entropy import sigmoid_cross_entropy_backward
from .backward_function.binary_cross_entropy import binary_cross_entropy_backward
from .backward_function.softmax_cross_entropy import softmax_cross_entropy_backward
from .backward_function.categorical_cross_entropy import categorical_cross_entropy_backward
from .backward_function.squared_error import squared_error_backward
from .backward_function.absolute_error import absolute_error_backward
from .backward_function.huber_loss import huber_loss_backward
from .backward_function.epsilon_insensitive_loss import epsilon_insensitive_loss_backward
from .backward_function.kl_multinomial import kl_multinomial_backward
from .backward_function.affine_grid import affine_grid_backward
from .backward_function.warp_by_grid import warp_by_grid_backward
from .backward_function.warp_by_flow import warp_by_flow_backward
from .backward_function.binary_sigmoid import binary_sigmoid_backward
from .backward_function.binary_tanh import binary_tanh_backward
from .backward_function.binary_connect_affine import binary_connect_affine_backward
from .backward_function.binary_connect_convolution import binary_connect_convolution_backward
from .backward_function.binary_weight_affine import binary_weight_affine_backward
from .backward_function.binary_weight_convolution import binary_weight_convolution_backward
from .backward_function.inq_affine import inq_affine_backward
from .backward_function.inq_convolution import inq_convolution_backward
from .backward_function.fixed_point_quantize import fixed_point_quantize_backward
from .backward_function.min_max_quantize import min_max_quantize_backward
from .backward_function.pow2_quantize import pow2_quantize_backward
from .backward_function.prune import prune_backward
from .backward_function.quantize_linear import quantize_linear_backward
from .backward_function.dequantize_linear import dequantize_linear_backward
from .backward_function.top_n_error import top_n_error_backward
from .backward_function.binary_error import binary_error_backward
from .backward_function.confusion_matrix import confusion_matrix_backward
from .backward_function.vat_noise import vat_noise_backward
from .backward_function.unlink import unlink_backward
from .backward_function.sink import sink_backward
from .backward_function.nms_detection2d import nms_detection2d_backward
from .backward_function.max_pooling_backward import max_pooling_backward_backward
from .backward_function.patch_correlation import patch_correlation_backward

# Mapping
from collections import OrderedDict
registry = OrderedDict()

registry.update(dict(
    Affine=affine_backward,
    RNN=rnn_backward,
    LSTM=lstm_backward,
    GRU=gru_backward,
    Convolution=convolution_backward,
    FusedConvolution=fused_convolution_backward,
    DepthwiseConvolution=depthwise_convolution_backward,
    Deconvolution=deconvolution_backward,
    DepthwiseDeconvolution=depthwise_deconvolution_backward,
    DeformableConvolution=deformable_convolution_backward,
    AdaptiveSeparableConvolution=adaptive_separable_convolution_backward,
    MaxPooling=max_pooling_backward,
    AveragePooling=average_pooling_backward,
    GlobalAveragePooling=global_average_pooling_backward,
    SumPooling=sum_pooling_backward,
    Unpooling=unpooling_backward,
    Embed=embed_backward,
    RoiAlign=roi_align_backward,
    Sigmoid=sigmoid_backward,
    Swish=swish_backward,
    Tanh=tanh_backward,
    ReLU=relu_backward,
    LeakyReLU=leaky_relu_backward,
    Softmax=softmax_backward,
    LogSoftmax=log_softmax_backward,
    ELU=elu_backward,
    SELU=selu_backward,
    CReLU=crelu_backward,
    CELU=celu_backward,
    PReLU=prelu_backward,
    GELU=gelu_backward,
    Mish=mish_backward,
    ReLU6=relu6_backward,
    HardSigmoid=hard_sigmoid_backward,
    HardTanh=hard_tanh_backward,
    LogSigmoid=log_sigmoid_backward,
    SoftPlus=softplus_backward,
    SoftSign=softsign_backward,
    TanhShrink=tanh_shrink_backward,
    Sinc=sinc_backward,
    FusedBatchNormalization=fused_batch_normalization_backward,
    BatchNormalization=batch_normalization_backward,
    GroupNormalization=group_normalization_backward,
    InstanceNormalization=instance_normalization_backward,
    LayerNormalization=layer_normalization_backward,
    NormNormalization=norm_normalization_backward,
    SyncBatchNormalization=sync_batch_normalization_backward,
    TensorNormalization=tensor_normalization_backward,
    WeightNormalization=weight_normalization_backward,
    WeightStandardization=weight_standardization_backward,
    SpectralNorm=spectral_norm_backward,
    MeanSubtraction=mean_subtraction_backward,
    ClipGradByValue=clip_grad_by_value_backward,
    ClipGradByNorm=clip_grad_by_norm_backward,
    Sum=sum_backward,
    CumSum=cumsum_backward,
    Mean=mean_backward,
    Max=max_backward,
    Min=min_backward,
    Norm=norm_backward,
    Prod=prod_backward,
    CumProd=cumprod_backward,
    ReduceSum=reduce_sum_backward,
    ReduceMean=reduce_mean_backward,
    Add2=add2_backward,
    AddN=add_n_backward,
    BcAdd2=bc_add2_backward,
    Sub2=sub2_backward,
    Mul2=mul2_backward,
    MulN=mul_n_backward,
    Div2=div2_backward,
    Pow2=pow2_backward,
    AddScalar=add_scalar_backward,
    MulScalar=mul_scalar_backward,
    PowScalar=pow_scalar_backward,
    RSubScalar=r_sub_scalar_backward,
    RDivScalar=r_div_scalar_backward,
    RPowScalar=r_pow_scalar_backward,
    Sign=sign_backward,
    Minimum2=minimum2_backward,
    Maximum2=maximum2_backward,
    MinimumScalar=minimum_scalar_backward,
    MaximumScalar=maximum_scalar_backward,
    LogicalAnd=logical_and_backward,
    LogicalOr=logical_or_backward,
    LogicalXor=logical_xor_backward,
    Equal=equal_backward,
    NotEqual=not_equal_backward,
    GreaterEqual=greater_equal_backward,
    Greater=greater_backward,
    LessEqual=less_equal_backward,
    Less=less_backward,
    SearchSorted=searchsorted_backward,
    LogicalAndScalar=logical_and_scalar_backward,
    LogicalOrScalar=logical_or_scalar_backward,
    LogicalXorScalar=logical_xor_scalar_backward,
    EqualScalar=equal_scalar_backward,
    NotEqualScalar=not_equal_scalar_backward,
    GreaterEqualScalar=greater_equal_scalar_backward,
    GreaterScalar=greater_scalar_backward,
    LessEqualScalar=less_equal_scalar_backward,
    LessScalar=less_scalar_backward,
    LogicalNot=logical_not_backward,
    IsNaN=isnan_backward,
    IsInf=isinf_backward,
    ResetNaN=reset_nan_backward,
    ResetInf=reset_inf_backward,
    Where=where_backward,
    Constant=constant_backward,
    Arange=arange_backward,
    Linspace=linspace_backward,
    Abs=abs_backward,
    Exp=exp_backward,
    Log=log_backward,
    Identity=identity_backward,
    BatchMatmul=batch_matmul_backward,
    Round=round_backward,
    Ceil=ceil_backward,
    Floor=floor_backward,
    Sin=sin_backward,
    Cos=cos_backward,
    Tan=tan_backward,
    Sinh=sinh_backward,
    Cosh=cosh_backward,
    ASin=asin_backward,
    ACos=acos_backward,
    ATan=atan_backward,
    ATan2=atan2_backward,
    ASinh=asinh_backward,
    ACosh=acosh_backward,
    ATanh=atanh_backward,
    Concatenate=concatenate_backward,
    Split=split_backward,
    Stack=stack_backward,
    Slice=slice_backward,
    Pad=pad_backward,
    Transpose=transpose_backward,
    Broadcast=broadcast_backward,
    BroadcastTo=broadcast_to_backward,
    Tile=tile_backward,
    OneHot=one_hot_backward,
    Flip=flip_backward,
    Shift=shift_backward,
    Sort=sort_backward,
    Reshape=reshape_backward,
    MatrixDiag=matrix_diag_backward,
    MatrixDiagPart=matrix_diag_part_backward,
    Meshgrid=meshgrid_backward,
    BatchDet=batch_det_backward,
    BatchInv=batch_inv_backward,
    BatchLogdet=batch_logdet_backward,
    Assign=assign_backward,
    Gather=gather_backward,
    GatherNd=gather_nd_backward,
    BoolGather=bool_gather_backward,
    ScatterNd=scatter_nd_backward,
    ScatterAdd=scatter_add_backward,
    BoolScatter=bool_scatter_backward,
    BoolFill=bool_fill_backward,
    PackPaddedSequence=pack_padded_sequence_backward,
    PadPackedSequence=pad_packed_sequence_backward,
    Interpolate=interpolate_backward,
    FFT=fft_backward,
    IFFT=ifft_backward,
    STFT=stft_backward,
    ISTFT=istft_backward,
    Dropout=dropout_backward,
    TopKData=top_k_data_backward,
    TopKGrad=top_k_grad_backward,
    Rand=rand_backward,
    Randint=randint_backward,
    Randn=randn_backward,
    RandBinomial=rand_binomial_backward,
    RandBeta=rand_beta_backward,
    RandGamma=rand_gamma_backward,
    RandomChoice=random_choice_backward,
    RandomCrop=random_crop_backward,
    RandomFlip=random_flip_backward,
    RandomShift=random_shift_backward,
    RandomErase=random_erase_backward,
    ImageAugmentation=image_augmentation_backward,
    SigmoidCrossEntropy=sigmoid_cross_entropy_backward,
    BinaryCrossEntropy=binary_cross_entropy_backward,
    SoftmaxCrossEntropy=softmax_cross_entropy_backward,
    CategoricalCrossEntropy=categorical_cross_entropy_backward,
    SquaredError=squared_error_backward,
    AbsoluteError=absolute_error_backward,
    HuberLoss=huber_loss_backward,
    EpsilonInsensitiveLoss=epsilon_insensitive_loss_backward,
    KLMultinomial=kl_multinomial_backward,
    AffineGrid=affine_grid_backward,
    WarpByGrid=warp_by_grid_backward,
    WarpByFlow=warp_by_flow_backward,
    BinarySigmoid=binary_sigmoid_backward,
    BinaryTanh=binary_tanh_backward,
    BinaryConnectAffine=binary_connect_affine_backward,
    BinaryConnectConvolution=binary_connect_convolution_backward,
    BinaryWeightAffine=binary_weight_affine_backward,
    BinaryWeightConvolution=binary_weight_convolution_backward,
    INQAffine=inq_affine_backward,
    INQConvolution=inq_convolution_backward,
    FixedPointQuantize=fixed_point_quantize_backward,
    MinMaxQuantize=min_max_quantize_backward,
    Pow2Quantize=pow2_quantize_backward,
    Prune=prune_backward,
    QuantizeLinear=quantize_linear_backward,
    DequantizeLinear=dequantize_linear_backward,
    TopNError=top_n_error_backward,
    BinaryError=binary_error_backward,
    ConfusionMatrix=confusion_matrix_backward,
    VATNoise=vat_noise_backward,
    Unlink=unlink_backward,
    Sink=sink_backward,
    NmsDetection2d=nms_detection2d_backward,
    MaxPoolingBackward=max_pooling_backward_backward,
    PatchCorrelation=patch_correlation_backward,
))

# Update the mapping for the function of the periodic property in backwards
from .backward_function.affine import affine_data_grad_backward, affine_filter_grad_backward
from .backward_function.convolution import convolution_data_grad_backward, convolution_filter_grad_backward
from .backward_function.deconvolution import deconvolution_data_grad_backward, deconvolution_filter_grad_backward
from .backward_function.embed import embed_filter_grad_backward
from .backward_function.batch_normalization import batch_normalization_backward_backward
from .backward_function.fused_batch_normalization import fused_batch_normalization_backward_backward
from .backward_function.average_pooling import average_pooling_data_grad_backward
from .backward_function.global_average_pooling import global_average_pooling_data_grad_backward
from .backward_function.sum_pooling import sum_pooling_data_grad_backward
from .backward_function.unpooling import unpooling_data_grad_backward
from .backward_function.concatenate import concatenate_data_grad_backward
from .backward_function.slice import slice_data_grad_backward
from .backward_function.pad import pad_data_grad_backward
from .backward_function.transpose import transpose_data_grad_backward
from .backward_function.interpolate import interpolate_data_grad_backward

def register(func_name, func):
    """Register the backward function to a function.

    Args:
      func_name (str): The function class name, for example, Affine.
      func (function): The function to be called as the backward function to the function `func_name`..
                       Arguments of the func must be (ctx: nn.Context, inputs: list of nn.Variable, **kwargs)..
                       The inputs are the ones to the function of the `func_name`. The kwargs are
                       the arguments of the function. For example, if the `func_name` is Affine,
                       func is `affine_backward`, the inputs are data, weights, and bias if necessary, and
                       kwargs = dict(base_axis=base_axis).
    """
    registry[func_name] = func

def show_registry():
    """Show all backward fuctions registry
    """
    for k, v in registry.items():
        print(k, v)
    print("Functions registered are ones which originally support the backward method.\n"
          "Functions e.g., F.constant which do not support the backward can be parts of "
          "the computation graph targeted by nn.grad.")

register("AffineDataGrad", affine_data_grad_backward)
register("AffineFilterGrad", affine_filter_grad_backward)
register("ConvolutionDataGrad", convolution_data_grad_backward)
register("ConvolutionFilterGrad", convolution_filter_grad_backward)
register("DeconvolutionDataGrad", deconvolution_data_grad_backward)
register("DeconvolutionFilterGrad", deconvolution_filter_grad_backward)
register("EmbedFilterGrad", embed_filter_grad_backward)
register("BatchNormalizationBackward", batch_normalization_backward_backward)
register("FusedBatchNormalizationBackward", fused_batch_normalization_backward_backward)
register("UnpoolingDataGrad", unpooling_data_grad_backward)
register("AveragePoolingDataGrad", average_pooling_data_grad_backward)
register("GlobalAveragePoolingDataGrad", global_average_pooling_data_grad_backward)
register("MaxPoolingBackwardDataGrad", max_pooling_backward)
register("SumPoolingDataGrad", sum_pooling_data_grad_backward)
register("ConcatenateDataGrad", concatenate_data_grad_backward)
register("SliceDataGrad", slice_data_grad_backward)
register("PadDataGrad", pad_data_grad_backward)
register("TransposeDataGrad", transpose_data_grad_backward)
register("InterpolateDataGrad", interpolate_data_grad_backward)
