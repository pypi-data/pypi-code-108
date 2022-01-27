# This file is part of Sympathy for Data.
# Copyright (c) 2018 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Imports a TDMS file into an ADAF. Each TDMS can contain an unlimited amount of
groups, where each groups holds a set of properties and an unlimited number of
channels (signal data).

The group properties will be stored in the ADAF's Meta section.

The raster is constructed from the fields wf_start_time, wf_increment, and
wf_start_offset, which are guaranteed to exist for each channel. The raster
will be in either datetime or float format, depending on the format of the
mentioned fields. If there isn't enough data to create a raster, an index
vector will be used.  The properties for each channel will be stored as column
attributes for the corresponding signal in the raster.
"""
import nptdms
import os
import numpy as np
import datetime as dt
import itertools
from sympathy.api import importers
from sympathy.api import table
from sympathy.api.exceptions import SyDataError


class DataImporterTDMS(importers.ADAFDataImporterBase):
    IMPORTER_NAME = "TDMS"

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False
        with open(self._fq_infilename, 'rb') as f:
            return f.read(4) == b'TDSm'

    def import_data(self, out_adaf, parameters=None, progress=None):
        try:
            tdms = nptdms.TdmsFile(self._fq_infilename)
        except Exception:
            if not self.valid_for_file():
                raise self.invalid_file(self._fq_infilename)
            raise
        meta_groups = []
        meta_dicts = []

        def channel_info(channel):
            properties = dict(channel.properties)
            start = properties.get('wf_start_time', 0)
            step = properties.get('wf_increment', 0)
            offs = properties.get('wf_start_offset', 0)
            channel_len = len(channel.data)
            return (start, step, offs, channel_len)

        out_sys = out_adaf.sys.create('TDMS')
        basis_properties = set(['wf_start_time', 'wf_increment',
                                'wf_start_offset',
                                'wf_samples'])

        for group in tdms.groups():
            meta_dict = dict(tdms.object(group).properties)
            if meta_dict:
                meta_groups.append(group)
                meta_dicts.append(meta_dict)

            rasters = {}
            n_rasters = len({channel_info(channel) for channel in
                             tdms.group_channels(group)})
            cnt = itertools.count()
            for channel in tdms.group_channels(group):
                # And each channel a raster starting at wf_start_time.
                properties = dict(channel.properties)
                info = channel_info(channel)
                start, step, offs, channel_len = info
                raster = rasters.get(info)

                if raster is None:
                    raster_name = group
                    if n_rasters > 1:
                        raster_name = '{} {}'.format(group, next(cnt))
                    raster = out_sys.create(raster_name)
                    rasters[info] = raster

                    if step == 0:
                        # No time basis can be created, use an index vector
                        tb = np.arange(channel_len)
                    elif isinstance(start, dt.datetime):
                        tb = np.array(
                            [start + dt.timedelta(seconds=offs + i * step)
                             for i in range(channel_len)])
                        properties['wf_start_time'] = start.isoformat()
                    else:
                        tb = np.arange(start + offs, channel_len,
                                       step=step or 1)

                    raster.create_basis(tb, attributes={
                        k: v for k, v in properties.items()
                        if k in basis_properties})

                raster.create_signal(
                    channel.channel, channel.data,
                    {k: v for k, v in properties.items()
                     if k not in basis_properties})
        if len(meta_groups):
            meta_table = table.File()
            for meta_group, meta_dict in zip(meta_groups, meta_dicts):
                for k, v in meta_dict.items():
                    meta_table['TDMS_{}_{}'.format(meta_group, k)] = (
                        np.array([v]))
            out_adaf.meta.from_table(meta_table)
