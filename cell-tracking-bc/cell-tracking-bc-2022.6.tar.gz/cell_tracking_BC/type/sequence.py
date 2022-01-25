# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from __future__ import annotations

import dataclasses as dcls
import functools as fctl
from itertools import starmap, zip_longest
from multiprocessing import Pool as pool_t
from operator import attrgetter as GetAttribute
from pathlib import Path as path_t
from typing import Any, Callable, Dict, Iterator, Optional, Sequence, Tuple, Union

import numpy as nmpy
import scipy.ndimage as imge

import cell_tracking_BC.in_out.text.progress as prgs
import cell_tracking_BC.standard.issue as isse
from cell_tracking_BC.standard.number import MAX_INT
from cell_tracking_BC.standard.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.cytoplasm import cytoplasm_t
from cell_tracking_BC.type.frame import frame_t, transform_h
from cell_tracking_BC.type.nucleus import nucleus_t
from cell_tracking_BC.type.segmentation import segmentation_t
from cell_tracking_BC.type.segmentations import segmentations_t
from cell_tracking_BC.type.track import (
    forking_track_t,
    single_track_t,
    unstructured_track_t,
)
from cell_tracking_BC.type.tracks import tracks_t


array_t = nmpy.ndarray
channel_computation_h = Callable[[Dict[str, array_t], Dict[str, Any]], array_t]
morphological_feature_computation_h = Callable[
    [cell_t, Dict[str, Any]], Union[Any, Sequence[Any]]
]
radiometric_feature_computation_h = Callable[
    [cell_t, Union[array_t, Sequence[array_t]], Dict[str, Any]],
    Union[Any, Sequence[Any]],
]
feature_filtering_h = Callable[..., Sequence[float]]


_Filtered = None


@dcls.dataclass(repr=False, eq=False)
class sequence_t:

    path: Optional[path_t] = None
    shape: Tuple[int, int] = None
    original_length: int = None
    length: int = None
    base_channels: Sequence[str] = None
    frames_of_channel: Dict[str, Sequence[Union[array_t, frame_t]]] = None
    cell_channel: str = None  # Name of channel whose frames store the segmented cells
    segmentations: segmentations_t = dcls.field(init=False, default=None)
    tracks: tracks_t = dcls.field(init=False, default=None)

    @classmethod
    def NewFromFrames(
        cls,
        frames: array_t,
        in_channel_names: Sequence[Optional[str]],
        path: path_t,
        /,
        *,
        first_frame: int = 0,
        last_frame: int = MAX_INT,
    ) -> sequence_t:
        """
        in_channel_names: names equal to None or "___" or "---" indicate channels that should be discarded
        """
        # TODO: make this function accept various input shapes thanks to an additional arrangement parameter of the
        #     form THRC, T=time, H=channel, RC= row column. This requires that SequenceFromPath deals with TH combined
        #     dimension.
        if (n_dims := frames.ndim) not in (3, 4):
            raise ValueError(
                f"{n_dims}: Invalid number of dimensions of sequence with shape {frames.shape}; "
                f"Expected=3 or 4=(TIME POINTS*CHANNELS)xROWSxCOLUMNS or "
                f"TIME POINTSxCHANNELSxROWSxCOLUMNS"
            )

        n_in_channels = in_channel_names.__len__()

        frames_of_channel = {}
        for name in in_channel_names:
            if (name is not None) and (name != "___") and (name != "---"):
                frames_of_channel[name] = []
        base_channel_names = tuple(frames_of_channel.keys())

        if n_dims == 3:
            c_idx = n_in_channels - 1
            time_point = -1
            for raw_frame in frames:
                c_idx += 1
                if c_idx == n_in_channels:
                    c_idx = 0
                    time_point += 1

                if time_point < first_frame:
                    continue
                elif time_point > last_frame:
                    break

                name = in_channel_names[c_idx]
                if name in base_channel_names:
                    frame = frame_t(raw_frame)
                    frames_of_channel[name].append(frame)
        else:
            for time_point, raw_frame in enumerate(frames):
                if time_point < first_frame:
                    continue
                elif time_point > last_frame:
                    break

                for c_idx, channel in enumerate(raw_frame):
                    name = in_channel_names[c_idx]
                    if name in base_channel_names:
                        frame = frame_t(channel)
                        frames_of_channel[name].append(frame)

        frames_of_base_channel = frames_of_channel[base_channel_names[0]]
        shape = frames_of_base_channel[0].shape
        length = frames_of_base_channel.__len__()
        instance = cls(
            path=path,
            shape=shape,
            original_length=frames.__len__(),
            length=length,
            base_channels=base_channel_names,
            frames_of_channel=frames_of_channel,
        )

        return instance

    @property
    def channels(self) -> Sequence[str]:
        """
        Names of channels read from file (base channels) and computed channels
        """
        return tuple(self.frames_of_channel.keys())

    @property
    def has_cells(self) -> bool:
        """"""
        return self.cell_channel is not None

    @property
    def cell_frames(self) -> Sequence[frame_t]:
        """"""
        return self.frames_of_channel[self.cell_channel]

    def Frames(
        self,
        /,
        *,
        channel: Union[str, Sequence[str]] = None,
    ) -> Union[
        Sequence[Union[array_t, frame_t]],
        Iterator[Sequence[Union[array_t, frame_t]]],
    ]:
        """
        channel: None=all (!) base channels; Otherwise, only (a) base channel name(s) can be passed
        as_iterator: Always considered True if channel is None or a sequence of channel names
        """
        if isinstance(channel, str):
            return self.frames_of_channel[channel]
        else:
            return self._FramesForMultipleChannels(channel)

    def _FramesForMultipleChannels(
        self, channels: Optional[Sequence[str]], /
    ) -> Iterator[Sequence[Union[array_t, frame_t]]]:
        """
        /!\ If "channels" contains both base and non-base channels, then the returned tuples will contain both array_t
        and frame_t elements (but frame_t is a subclass of array_t, so...).
        """
        if channels is None:
            channels = self.base_channels

        for f_idx in range(self.length):
            frames = (self.frames_of_channel[_chl][f_idx] for _chl in channels)

            yield tuple(frames)

    def ChannelExtrema(self, channel: str, /) -> Tuple[float, float]:
        """"""
        min_intensity = nmpy.Inf
        max_intensity = -nmpy.Inf

        for frame in self.frames_of_channel[channel]:
            min_intensity = min(min_intensity, nmpy.amin(frame))
            max_intensity = max(max_intensity, nmpy.amax(frame))

        return min_intensity.item(), max_intensity.item()

    def NCells(
        self, /, *, in_frame: Union[int, Sequence[int]] = None
    ) -> Union[int, Sequence[int]]:
        """
        in_frame: None=>total over the sequence
        """
        if in_frame is None:
            return sum(_cll.__len__() for _cll in self.cells_iterator)

        just_one = isinstance(in_frame, int)
        if self.has_cells:
            if just_one:
                in_frame = (in_frame,)

            output = in_frame.__len__() * [0]

            for f_idx, cells in enumerate(self.cells_iterator):
                if f_idx in in_frame:
                    output[in_frame.index(f_idx)] = cells.__len__()

            if just_one:
                output = output[0]
        elif just_one:
            output = 0
        else:
            output = in_frame.__len__() * (0,)

        return output

    @property
    def cells_iterator(self) -> Iterator[Sequence[cell_t]]:
        """"""
        for frame in self.cell_frames:
            yield frame.cells

    @property
    def cytoplasms_iterator(self) -> Iterator[Sequence[Optional[cytoplasm_t]]]:
        """"""
        for frame in self.cell_frames:
            yield tuple(map(GetAttribute("cytoplasm"), frame.cells))
            # output = []
            # for cell in frame.cells:
            #     output.append(cell.cytoplasm)
            # yield output

    @property
    def nuclei_iterator(self) -> Iterator[Sequence[Sequence[nucleus_t]]]:
        """"""
        for frame in self.cell_frames:
            yield tuple(map(GetAttribute("nuclei"), frame.cells))
            # output = []
            # for cell in frame.cells:
            #     output.append(cell.nuclei)
            # yield output

    def ApplyTransform(
        self,
        Transform: transform_h,
        /,
        *,
        channel: Union[str, Sequence[str]] = None,
        **kwargs,
    ) -> None:
        """
        channel: None=all (!)
        """
        if channel is None:
            channels = self.base_channels
        elif isinstance(channel, str):
            channels = (channel,)
        else:
            channels = channel

        for channel in channels:
            targets = self.frames_of_channel[channel]
            references_sets = self.Frames(channel=self.channels)
            for target, references in zip(targets, references_sets):
                refs_as_dict = dict(zip(self.channels, references))
                # refs_as_dict = {
                #     _nme: _frm for _nme, _frm in zip(self.channels, references)
                # }
                target.ApplyTransform(Transform, channels=refs_as_dict, **kwargs)

    def AddComputedChannel(
        self, name: str, ChannelComputation: channel_computation_h, /, **kwargs
    ) -> None:
        """"""
        computed = []
        for frames in self.Frames(channel=self.channels):
            frames_as_dict = dict(zip(self.channels, frames))
            # frames_as_dict = {_nme: _frm for _nme, _frm in zip(self.channels, frames)}
            computed.append(ChannelComputation(frames_as_dict, **kwargs))

        self.frames_of_channel[name] = computed

    def AddCellsFromSegmentations(
        self,
        channel: str,
        segmentations: segmentations_t,
    ) -> None:
        """
        Segmentation are supposed to be binary (as opposed to already labeled)
        """
        self.cell_channel = channel
        self.segmentations = segmentations

        for frame, segmentation in zip(self.cell_frames, segmentations):
            frame.AddCellsFromSegmentation(segmentation)

    def AddCellFeature(
        self,
        name: Union[str, Sequence[str]],
        Feature: Union[
            morphological_feature_computation_h, radiometric_feature_computation_h
        ],
        /,
        channel: Union[str, Sequence[str]] = None,
        should_run_in_parallel: bool = True,
        should_run_silently: bool = False,
        **kwargs,
    ) -> None:
        """
        name: If an str, then the value returned by Feature will be considered as a whole, whether it is actually a
        single value or a value container. If a sequence of str's, then the object returned by Feature will be iterated
        over, each element being matched with the corresponding name in "name".
        channel: if None, then morphological feature, else radiometric feature.
        """
        if isinstance(name, str):
            description = f'Feature "{name}"'
        else:
            description = f'Feature "{name[0]}, ..., {name[-1]}"'
        ParallelFeature = fctl.partial(Feature, **kwargs)

        with prgs.ProgressDesign(should_be_silent=should_run_silently) as progress:
            if channel is None:
                iterator = self.cells_iterator
            else:
                iterator = zip(self.cells_iterator, self.frames_of_channel[channel])
            progress_context = prgs.progress_context_t(
                progress,
                iterator,
                total=self.length,
                description=description,
            )

            if should_run_in_parallel:
                pool = pool_t()
                MapFunctionOnList = pool.map
                StarMapFunctionOnList = pool.starmap
            else:
                pool = None
                MapFunctionOnList = map
                StarMapFunctionOnList = starmap

            if channel is None:
                if isinstance(name, str):
                    for cells in progress_context.elements:
                        features = MapFunctionOnList(ParallelFeature, cells)
                        for cell, feature in zip(cells, features):
                            cell.AddFeature(name, feature)
                else:
                    names = name
                    for cells in progress_context.elements:
                        multi_features = MapFunctionOnList(ParallelFeature, cells)
                        for cell, features in zip(cells, multi_features):
                            for name, feature in zip(names, features):
                                cell.AddFeature(name, feature)
            else:
                if isinstance(name, str):
                    for cells, frame in progress_context.elements:
                        features = StarMapFunctionOnList(
                            ParallelFeature,
                            zip_longest(cells, (frame,), fillvalue=frame),
                        )
                        for cell, feature in zip(cells, features):
                            cell.AddFeature(name, feature)
                else:
                    names = name
                    for cells, frame in progress_context.elements:
                        multi_features = StarMapFunctionOnList(
                            ParallelFeature,
                            zip_longest(cells, (frame,), fillvalue=frame),
                        )
                        for cell, features in zip(cells, multi_features):
                            for name, feature in zip(names, features):
                                cell.AddFeature(name, feature)

            if should_run_in_parallel:
                pool.close()
                pool.terminate()

    def AddTracks(
        self,
        tracks: tracks_t,
        /,
    ) -> None:
        """"""
        self.tracks = tracks

    def FilteredCellFeature(
        self,
        feature: Union[str, Sequence[str]],
        Filter: feature_filtering_h,
        /,
        *args,
        **kwargs,
    ) -> Dict[int, Sequence[Any]]:
        """"""
        output = {}

        if isinstance(feature, str):
            features = (feature,)
        else:
            features = feature
        if any(_ftr not in self.available_cell_features for _ftr in features):
            raise ValueError(f"{feature}: Invalid feature(s)")

        for track in self.tracks.single_tracks_iterator:
            all_series = [
                self.FeatureEvolutionAlongTrack(track, _ftr) for _ftr in features
            ]
            filtered = Filter(*all_series, *args, **kwargs)
            if filtered is None:
                output[track.label] = None
            else:
                pre_padding = track.root_time_point * (None,)
                filtered = pre_padding + tuple(filtered)
                output[track.label] = filtered

        return output

    @property
    def available_cell_features(self) -> Sequence[str]:
        """"""
        one_cell = self.cell_frames[0].cells[0]

        return one_cell.available_features

    @staticmethod
    def FeatureEvolutionAlongTrack(
        track: single_track_t, feature: str, /
    ) -> Sequence[Any]:
        """"""
        if feature in track[0].features:
            return tuple(_cll.features[feature] for _cll in track)

        raise ValueError(f"{feature}: Invalid feature(s)")

    def FeatureEvolutionsAlongAllTracks(
        self, feature: str, /
    ) -> Dict[int, Tuple[single_track_t, Sequence[Any]]]:
        """"""
        output = {}

        for track in self.tracks.single_tracks_iterator:
            output[track.label] = (
                track,
                sequence_t.FeatureEvolutionAlongTrack(track, feature),
            )

        return output

    def ClearContents(self):
        """
        To free up some memory when all processing has been done
        """
        for frames in self.Frames():
            for frame in frames:
                frame.ClearContents()

    def PrintValidInvalidTrackSummary(self) -> None:
        """"""
        n_invalids = []
        issues_per_type = {}
        for track_type, invalids in self.tracks.invalids.items():
            track_type = track_type.__name__[:-2].replace("_", " ").capitalize()
            if (invalids is None) or (invalids.__len__() == 0):
                number = f"{track_type}: None"
            else:
                number = f"{track_type}: {invalids.__len__()}"

                issues = (
                    f"    Track {_tck.labels_as_str}{isse.ISSUE_SEPARATOR}"
                    f"{isse.FactorizedIssuesAsStr(_iss, max_n_contexts=5)}"
                    for _tck, _iss in invalids
                )
                issues_per_type[track_type] = "\n".join(issues)

            n_invalids.append(number)

        n_invalids = ", ".join(n_invalids)
        issues_per_type = "\n".join(
            f"{_typ}:\n{_iss}" for _typ, _iss in issues_per_type.items()
        )

        print(
            f"Tracks: valid={self.tracks.__len__()}; invalid={n_invalids}\n{issues_per_type}"
        )

    def __str__(self) -> str:
        """"""
        if self.tracks is None:
            invalid_tracks = None
        else:
            invalid_tracks = (
                f"{self.tracks.invalids[unstructured_track_t]=}\n"
                f"    {self.tracks.invalids[single_track_t]=}\n"
                f"    {self.tracks.invalids[forking_track_t]=}"
            )

        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.path=}\n"
            f"    {self.base_channels=}\n"
            f"    {self.channels=}\n"
            f"    {self.shape=}\n"
            f"    {self.original_length=}\n"
            f"    {self.length=}\n"
            f"    {self.tracks=}\n"
            f"    {invalid_tracks=}\n"
        )


sequence_h = Union[
    Sequence[array_t], Sequence[segmentation_t], segmentations_t, sequence_t
]


def BoundingBoxSlices(sequence: array_t, /) -> Sequence[slice]:
    """
    sequence: as an XYT-volume
    """
    min_reduction = nmpy.amin(sequence, axis=-1)
    max_reduction = nmpy.amax(sequence, axis=-1)
    constant = nmpy.any(min_reduction != max_reduction, axis=-1)
    output = imge.find_objects(constant)[0]

    return output
