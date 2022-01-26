#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel wrapper class for NGHXRG - Teledyne HxRG Noise Generator model."""

import logging
import typing as t
from dataclasses import dataclass

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import CMOS, CMOSGeometry
from pyxel.models.charge_measurement.nghxrg.nghxrg_beta import HXRGNoise
from pyxel.util import temporary_random_state


@dataclass
class KTCBiasNoise:
    """KTCBiasNoise parameters."""

    ktc_noise: float
    bias_offset: float
    bias_amp: float


@dataclass
class WhiteReadNoise:
    """WhiteReadNoise parameters."""

    rd_noise: float
    ref_pixel_noise_ratio: float


@dataclass
class CorrPinkNoise:
    """CorrPinkNoise parameters."""

    c_pink: float


@dataclass
class UncorrPinkNoise:
    """UncorrPinkNoise parameters."""

    u_pink: float


@dataclass
class AcnNoise:
    """AcnNoise parameters."""

    acn: float


@dataclass
class PCAZeroNoise:
    """PCAZeroNoise parameters."""

    pca0_amp: float


# Create an alias
NoiseType = t.Union[
    KTCBiasNoise,
    WhiteReadNoise,
    CorrPinkNoise,
    UncorrPinkNoise,
    AcnNoise,
    PCAZeroNoise,
]


# TODO: Use function `simcado.nghxrg.HXRGNoise` instead of
#       `pyxel.models.charge_measurement.nghxrg.nghxrg.HXRGNoise`
def compute_nghxrg(
    pixel_2d: np.ndarray,
    noise: t.Sequence[NoiseType],
    detector_shape: t.Tuple[int, int],
    window_pos: t.Tuple[int, int],
    window_size: t.Tuple[int, int],
    num_outputs: int,
    time_step: int,
    num_rows_overhead: int,
    num_frames_overhead: int,
    reverse_scan_direction: bool,
    reference_pixel_border_width: int,
) -> np.ndarray:
    """Compute NGHXRG.

    Parameters
    ----------
    pixel_2d : ndarray
    noise : sequence of NoiseType
    detector_shape : int, int
    window_pos : int, int
    window_size : int, int
    num_outputs : int
    time_step : int
    num_rows_overhead : int
    num_frames_overhead : int
    reverse_scan_direction : bool
    reference_pixel_border_width : int

    Returns
    -------
    ndarray
    """
    det_size_y, det_size_x = detector_shape
    window_y_start, window_x_start = window_pos
    window_y_size, window_x_size = window_size

    if window_pos == (0, 0) and window_size == detector_shape:
        window_mode = "FULL"  # type: Literal["FULL", "WINDOW"]
    else:
        window_mode = "WINDOW"

    data_hxrg_2d = np.asarray(pixel_2d.copy(), dtype=float)  # type: np.ndarray

    ng = HXRGNoise(
        n_out=num_outputs,
        time_step=time_step,
        nroh=num_rows_overhead,
        nfoh=num_frames_overhead,
        reverse_scan_direction=reverse_scan_direction,
        reference_pixel_border_width=reference_pixel_border_width,
        pca0=data_hxrg_2d,
        det_size_x=det_size_x,
        det_size_y=det_size_y,
        wind_mode=window_mode,
        wind_x_size=window_x_size,
        wind_y_size=window_y_size,
        wind_x0=window_x_start,
        wind_y0=window_y_start,
        verbose=True,
    )  # type: HXRGNoise

    final_data_2d = np.zeros(shape=window_size)

    for item in noise:  # type: NoiseType
        if isinstance(item, KTCBiasNoise):
            data = ng.add_ktc_bias_noise(
                ktc_noise=item.ktc_noise,
                bias_offset=item.bias_offset,
                bias_amp=item.bias_amp,
            )  # type: np.ndarray

        elif isinstance(item, WhiteReadNoise):
            data = ng.add_white_read_noise(
                rd_noise=item.rd_noise,
                reference_pixel_noise_ratio=item.ref_pixel_noise_ratio,
            )

        elif isinstance(item, CorrPinkNoise):
            data = ng.add_corr_pink_noise(c_pink=item.c_pink)

        elif isinstance(item, UncorrPinkNoise):
            data = ng.add_uncorr_pink_noise(u_pink=item.u_pink)

        elif isinstance(item, AcnNoise):
            data = ng.add_acn_noise(acn=item.acn)

        elif isinstance(item, PCAZeroNoise):
            data = ng.add_pca_zero_noise(pca0_amp=item.pca0_amp)

        else:
            raise TypeError(f"Unknown item: {item!r} !")

        data_2d = ng.format_result(data)  # type: np.ndarray
        if data_2d.any():
            if window_mode == "FULL":
                final_data_2d += data_2d
            elif window_mode == "WINDOW":
                window_y_end = window_y_start + window_y_size  # type: int
                window_x_end = window_x_start + window_x_size  # type: int

                final_data_2d[
                    window_y_start:window_y_end, window_x_start:window_x_end
                ] += data_2d

    return final_data_2d


# TODO: copyright
@temporary_random_state
def nghxrg(
    detector: CMOS,
    noise: t.Sequence[
        t.Mapping[
            Literal[
                "ktc_bias_noise",
                "white_read_noise",
                "corr_pink_noise",
                "uncorr_pink_noise",
                "acn_noise",
                "pca_zero_noise",
            ],
            t.Mapping[str, float],
        ]
    ],
    window_position: t.Optional[t.Tuple[int, int]] = None,
    window_size: t.Optional[t.Tuple[int, int]] = None,
    n_output: int = 1,
    n_row_overhead: int = 0,
    n_frame_overhead: int = 0,
    reverse_scan_direction: bool = False,
    reference_pixel_border_width: int = 4,
    seed: t.Optional[int] = None,  # This parameter is used by '@temporary_random_state'
) -> None:
    """Generate fourier noise power spectrum on HXRG detector.

    For more information see :cite:p:`2015:rauscher`.

    Parameters
    ----------
    detector: Detector
    noise: list
    window_position: t.Sequence, optional
        [x0 (columns), y0 (rows)].
    window_size: t.Sequence, optional
        [x (columns), y (rows)].
    seed: int, optional
    n_output: int
        Number of detector outputs.
    n_row_overhead: int
        New row overhead in pixel.
        This allows for a short wait at the end of a row before starting the next row.
    n_frame_overhead: int
        New frame overhead in rows.
        This allows for a short wait at the end of a frame before starting the next frame.
    reverse_scan_direction: bool
        Set this True to reverse the fast scanner readout directions.
        This capability was added to support Teledyne’s programmable fast scan readout directions.
        The default setting (False) corresponds to what HxRG detectors default to upon power up.
    reference_pixel_border_width: int
        Width of reference pixel border around image area.
    """
    if n_output not in range(33):
        raise ValueError("'n_output' must be between 0 and 32.")

    if n_row_overhead not in range(101):
        raise ValueError("'n_row_overhead' must be between 0 and 100.")

    if n_frame_overhead not in range(101):
        raise ValueError("'n_frame_overhead' must be between 0 and 100.")

    if reference_pixel_border_width not in range(33):
        raise ValueError("'reference_pixel_border_width' must be between 0 and 32.")

    # Converter
    params = []  # type: t.List[NoiseType]
    for item in noise:
        if "ktc_bias_noise" in item:
            sub_item = item["ktc_bias_noise"]  # type: t.Mapping[str, float]
            param = KTCBiasNoise(
                ktc_noise=sub_item["ktc_noise"],
                bias_offset=sub_item["bias_offset"],
                bias_amp=sub_item["bias_amp"],
            )  # type: NoiseType

        elif "white_read_noise" in item:
            sub_item = item["white_read_noise"]
            param = WhiteReadNoise(
                rd_noise=sub_item["rd_noise"],
                ref_pixel_noise_ratio=sub_item["ref_pixel_noise_ratio"],
            )

        elif "corr_pink_noise" in item:
            sub_item = item["corr_pink_noise"]
            param = CorrPinkNoise(c_pink=sub_item["c_pink"])

        elif "uncorr_pink_noise" in item:
            sub_item = item["uncorr_pink_noise"]
            param = UncorrPinkNoise(u_pink=sub_item["u_pink"])

        elif "acn_noise" in item:
            sub_item = item["acn_noise"]
            param = AcnNoise(acn=sub_item["acn"])

        elif "pca_zero_noise" in item:
            sub_item = item["pca_zero_noise"]
            param = PCAZeroNoise(pca0_amp=sub_item["pca0_amp"])

        else:
            raise KeyError(f"Unknown key: item = {item!r}")

        params.append(param)

    logging.getLogger("nghxrg").setLevel(logging.WARNING)

    # Prepare the parameters
    geo = detector.geometry  # type: CMOSGeometry

    if window_position is None:
        window_position = (0, 0)
    if window_size is None:
        window_size = (geo.row, geo.col)

    if detector.is_dynamic:
        time_step = int(detector.time / detector.time_step)  # type: int
    else:
        time_step = 1

    # Compute new pixels
    result_2d = compute_nghxrg(
        pixel_2d=detector.pixel.array,
        noise=params,
        detector_shape=(geo.row, geo.col),
        window_pos=window_position,
        window_size=window_size,
        num_outputs=n_output,
        time_step=time_step,
        num_rows_overhead=n_row_overhead,
        num_frames_overhead=n_frame_overhead,
        reverse_scan_direction=reverse_scan_direction,
        reference_pixel_border_width=reference_pixel_border_width,
    )  # type: np.ndarray

    # Add the pixels
    detector.pixel.array += result_2d


# TODO: This generates plot. It should be in class `Output`
# def display_noisepsd(
#     array: np.ndarray,
#     nb_output: int,
#     dimensions: t.Tuple[int, int],
#     noise_name: str,
#     path: Path,
#     step: int,
#     # mode: Literal["plot"] = "plot",
# ) -> t.Tuple[t.Any, np.ndarray]:
#     """Display noise PSD from the generated FITS file.
#
#     For power spectra, need to be careful of readout directions.
#
#     For the periodogram, using Welch's method to smooth the PSD
#     > Divide data in N segment of length nperseg which overlaps at nperseg/2
#     (noverlap argument)
#     nperseg high means less averaging for the PSD but more points.
#     """
#     # Conversion gain
#     conversion_gain = 1
#     data_corr = array * conversion_gain
#
#     if nb_output <= 1:
#         raise ValueError("Parameter 'nb_output' must be >= 1.")
#
#     # Should be in the simulated data header
#     dimension = dimensions[0]  # type: int
#     pix_p_output = dimension ** 2 / nb_output  # Number of pixels per output
#     nbcols_p_channel = dimension / nb_output  # Number of columns per channel
#     nperseg = int(pix_p_output / 10.0)  # Length of segments for Welch's method
#     read_freq = 100000  # Frame rate [Hz]
#
#     # Initializing table of nb_outputs periodogram +1 for dimensions
#     pxx_outputs = np.zeros((nb_output, int(nperseg / 2) + 1))
#
#     # For each output
#     for i in np.arange(nb_output):
#         # If i odd, flatten data since its the good reading direction
#         if i % 2 == 0:
#             start_x_idx = int(i * nbcols_p_channel)
#             end_x_idx = int((i + 1) * nbcols_p_channel)
#
#             output_data = data_corr[:, start_x_idx:end_x_idx].flatten()
#         # Else, flip it left/right and then flatten it
#         else:
#             start_x_idx = int(i * nbcols_p_channel)
#             end_x_idx = int((i + 1) * nbcols_p_channel)
#
#             output_data = np.fliplr(data_corr[:, start_x_idx:end_x_idx])
#             output_data.flatten()
#         # output data without flipping
#         # output_data = data_corr[:,int(i*(nbcols_p_channel)):
#         #                         int((i+1)*(nbcols_p_channel))].flatten()
#
#         # print(output_data, read_freq, nperseg)
#         # Add periodogram to the previously initialized array
#         f_vect, pxx_outputs[i] = signal.welch(output_data, read_freq, nperseg=nperseg)
#
#     # For the detector
#     # detector_data = data_corr.flatten()
#     # Add periodogram to the previously initialized array
#     # test, Pxx_detector = signal.welch(detector_data,
#     #                                   read_freq,
#     #                                   nperseg=nperseg)
#
#     # if mode == "plot":
#     #     fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
#     #     fig.canvas.set_window_title("Power Spectral Density")
#     #     fig.suptitle(
#     #         noise_name
#     #         + " Power Spectral Density\n"
#     #         + "Welch seg. length / Nb pixel output: "
#     #         + str("{:1.2f}".format(nperseg / pix_p_output))
#     #     )
#     #     ax1.plot(f_vect, np.mean(pxx_outputs, axis=0), ".-", ms=3, alpha=0.5, zorder=32)
#     #     for _, ax in enumerate([ax1]):
#     #         ax.set_xlim([1, 1e5])
#     #         ax.set_xscale("log")
#     #         ax.set_yscale("log")
#     #         ax.set_xlabel("Frequency [Hz]")
#     #         ax.set_ylabel("PSD [e-${}^2$/Hz]")
#     #         ax.grid(True, alpha=0.4)
#     #
#     #     filename = path.joinpath(
#     #         "nghxrg_" + noise_name + "_" + str(step) + ".png"
#     #     )  # type: Path
#     #     plt.savefig(filename, dpi=300)
#     #     plt.close()
#
#     result = np.asarray(np.mean(pxx_outputs, axis=0))  # type: np.ndarray
#     return f_vect, result
