#!/usr/bin/env python3# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

import climetlab as cml
import pandas as pd

# from climetlab.normalize import normalize_args
import xarray as xr
from climetlab import Dataset
from climetlab.decorators import normalize

__version__ = "0.5.4"

URL = "https://storage.ecmwf.europeanweather.cloud"
PATTERN = "{url}/MAELSTROM_AP3/{inout}_{date}00_{timestep}c{patch}.nc"

timestep_subsets = {"tier-1": 0, "2020": list(range(0, 3501, 125))}
date_subsets = {
    "tier-1": "20200101",
    "2020": [
        i.strftime("%Y%m%d")
        for i in pd.date_range(start="20200101", end="20210101", freq="30D")
    ],
}
patch_subsets = {"tier-1": list(range(0, 16, 2)), "2020": list(range(16))}

valid_subset = ["tier-1", "2020"]
valid_timestep = list(range(0, 3501, 125))
valid_patch = list(range(16))
valid_date = [
    i.strftime("%Y%m%d")
    for i in pd.date_range(start="20200101", end="20210101", freq="30D")
] + ["20190131", "20190531", "20190829", "20191028"]


class radiation(Dataset):
    name = "radiation"
    home_page = "https://git.ecmwf.int/projects/MLFET/repos/maelstrom-radiation"
    licence = "CC BY 4.0, see https://apps.ecmwf.int/datasets/licences/general/ "
    documentation = (
        "Minimal call:\n"
        "cml.load_dataset('maelstrom-radiation') \n"
        "Optional arguments:\n"
        "Specify subset, subset = 'tier-1\n"
        "Or specify date/timestep/patch\n"
        "Valid values found in .valid_date etc\n"
        "To add the heating rates use heating_rate = True\n"
        "To gather inputs into blocks of similar shape, raw_inputs = False \n"
        "To reduce to minimal output components, minimal_outputs = True \n"
    )
    citation = "-"
    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/licences/general/ "
        "If you do not agree with such terms, do not download the data. "
    )

    @normalize(
        "dataset",
        ["mcica", "tripleclouds", "3dcorrection", "spartacus"],
        multiple=False,
    )
    @normalize(
        "date",
        valid_date,
        multiple=True,  # type="date-list"
    )  # , aliases={"2020":date_subsets["2020"]})
    @normalize("subset", valid_subset, multiple=False)
    @normalize("patch", valid_patch, multiple=True)
    @normalize("timestep", valid_timestep, multiple=True)
    @normalize("hr_units", ["K s-1", "K d-1"], multiple=False)
    def __init__(
        self,
        dataset="mcica",
        date="20200101",
        timestep=0,
        subset=None,
        raw_inputs=True,
        minimal_outputs=False,
        all_outputs=False,
        patch=list(range(0, 16, 2)),
        heating_rate=True,
        hr_units="K s-1",
        topnetflux=False,
        gather_fluxes=False,
    ):

        self.icol_keys = [
            "q",
            "o3_mmr",
            "co2_vmr",
            "n2o_vmr",
            "ch4_vmr",
            "o2_vmr",
            "cfc11_vmr",
            "cfc12_vmr",
            "hcfc22_vmr",
            "ccl4_vmr",
            "cloud_fraction",
            "aerosol_mmr",
            "q_liquid",
            "q_ice",
            "re_liquid",
            "re_ice",
        ]
        # NB these variables will be needed for SPARTACUS
        # 'fractional_std','inv_cloud_effective_size'
        self.ihl_keys = ["temperature_hl", "pressure_hl"]
        self.iinter_keys = ["overlap_param"]
        self.isca_keys = [
            "skin_temperature",
            "cos_solar_zenith_angle",
            "sw_albedo",
            "sw_albedo_direct",
            "lw_emissivity",
            "solar_irradiance",
        ]
        self.dataset_tags = {
            "mcica": "rad4NN_outputs",
            "3dcorrection": "3dcorrection_outputs",
            "tripleclouds": "triplecloud_outputs",
            "spartacus": "spartacus_outputs",
        }

        self.raw_inputs = raw_inputs
        self.heating_rate = heating_rate
        self.minimal_outputs = minimal_outputs
        self.gather_fluxes = gather_fluxes
        assert not (
            self.minimal_outputs and self.gather_fluxes
        ), "Can't use minimal_outputs and gather_fluxes together"
        self.topnetflux = topnetflux
        self.all_outputs = all_outputs
        self.hr_units = hr_units
        self.hr_scale = {"K s-1": 1, "K d-1": 24 * 3600}[hr_units]
        self.g_cp = 9.80665 / 1004 * self.hr_scale
        if self.minimal_outputs:
            self.all_outputs = False

        self.valid_subset = valid_subset
        self.valid_timestep = valid_timestep
        self.valid_patch = valid_patch
        self.valid_date = valid_date

        if subset is not None:
            print(f"Loading subset: {subset}")
            date = date_subsets[subset]
            timestep = timestep_subsets[subset]
            patch = patch_subsets[subset]
            print(f"Loading date: {date}, timestep: {timestep}, patch: {patch}")
        self.dataset = dataset

        request = dict(
            url=URL, timestep=timestep, patch=patch, inout=["rad4NN_inputs"], date=date
        )
        self.source_inputs = cml.load_source(
            "url-pattern", PATTERN, request, merger=Merger()
        )
        request = dict(
            url=URL,
            timestep=timestep,
            patch=patch,
            inout=[self.dataset_tags[self.dataset]],
            date=date,
        )
        self.source_outputs = cml.load_source(
            "url-pattern", PATTERN, request, merger=Merger()
        )
        return

    def get_heating_rate(self, dataset, wl):
        flux = self.get_fluxes(dataset, wl)
        hl_pressure = dataset["pressure_hl"]
        netflux = flux[..., 0] - flux[..., 1]
        flux_diff = netflux[..., 1:] - netflux[..., :-1]
        net_press = hl_pressure[..., 1:] - hl_pressure[..., :-1]
        result = -self.g_cp * flux_diff / net_press
        result.attrs["long_name"] = f"{wl} heating rate"
        result.attrs["units"] = self.hr_units
        return result.rename({"half_level": "level"})

    def get_fluxes(self, dataset, wl):
        return self.merge_cols(dataset, [f"flux_dn_{wl}", f"flux_up_{wl}"])

    def merge_scalars(self, ds, keys, label=""):
        tmp = []
        for k in keys:
            if len(ds[k].shape) == 1:
                tmp.append(ds[k].expand_dims(label + "variable", axis=-1))
            else:
                rename_dic = {ds[k].dims[-1]: label + "variable"}
                tmp.append(ds[k].rename(rename_dic))
        return xr.concat(tmp, label + "variable", data_vars="all")

    def merge_cols(self, ds, keys, label=""):
        tmp = []
        for k in keys:
            if k == "aerosol_mmr":
                order = ("column", "level", "aerosol_type")
                tmp.append(
                    ds[k].transpose(*order).rename({"aerosol_type": label + "variable"})
                )
            else:
                tmp.append(ds[k].expand_dims(label + "variable", axis=-1))
        return xr.concat(tmp, label + "variable", data_vars="all")

    def get_minimal_outputs(self, ds):
        assert self.heating_rate, "Minimal outputs require heating rate"
        flux = self.get_fluxes(ds, "sw")
        ds["fluxes_sw"] = self._boundary_flux(flux)
        flux = self.get_fluxes(ds, "lw")
        ds["fluxes_lw"] = self._boundary_flux(flux)
        return ds

    def _boundary_flux(self, flux):
        if self.topnetflux:
            flux = xr.concat(
                [
                    flux[..., :1, 0] - flux[..., :1, 1],
                    flux[..., -1:, 0],
                    flux[..., -1:, -1],
                ],
                dim="half_level",
            )
            flux = flux.rename({"half_level": "boundaries"})
        else:
            flux = xr.concat(
                [flux[..., :1, 1], flux[..., -1:, 0], flux[..., -1:, -1]],
                dim="half_level",
            )
            flux = flux.rename({"half_level": "boundaries"})
        return flux

    def to_xarray(self):
        self.source = self.source_inputs
        ds_inputs = super().to_xarray()
        if not self.raw_inputs:
            ds_inputs = self.proc_input_arrays(ds_inputs)
        self.source = self.source_outputs
        ds_outputs = super().to_xarray()
        if self.heating_rate:
            ds_outputs["hr_sw"] = self.get_heating_rate(ds_outputs, "sw")
            ds_outputs["hr_lw"] = self.get_heating_rate(ds_outputs, "lw")
        if not self.all_outputs:
            output_list = ["flux_dn_sw", "flux_up_sw", "flux_dn_lw", "flux_up_lw"]
            if self.minimal_outputs:
                output_list = ["fluxes_sw", "fluxes_lw"]
                ds_outputs = self.get_minimal_outputs(ds_outputs)
            if self.gather_fluxes:
                output_list = ["lw", "sw"]
                ds_outputs["lw"] = self.get_fluxes(ds_outputs, "lw")
                ds_outputs["sw"] = self.get_fluxes(ds_outputs, "sw")
            if self.heating_rate:
                output_list += ["hr_sw", "hr_lw"]
            ds_outputs = ds_outputs[output_list]

        return xr.merge([ds_inputs, ds_outputs])

    def proc_input_arrays(self, inputs_ds):
        sca_inputs = self.merge_scalars(inputs_ds, self.isca_keys, label="sca_")
        col_inputs = self.merge_cols(inputs_ds, self.icol_keys, label="col_")
        hl_inputs = self.merge_cols(inputs_ds, self.ihl_keys, label="hl_")
        inter_inputs = self.merge_cols(inputs_ds, self.iinter_keys, label="inter_")
        hl_pressure = self.merge_cols(inputs_ds, ["pressure_hl"], label="p_")
        return {
            "sca_inputs": sca_inputs,
            "col_inputs": col_inputs,
            "hl_inputs": hl_inputs,
            "pressure_hl": hl_pressure,
            "inter_inputs": inter_inputs,
            "lat": inputs_ds.lat,
            "lon": inputs_ds.lon,
        }

    def to_tfdataset(self, keys=[], example_dim="column"):
        import tensorflow as tf

        dsx = self.to_xarray()
        if len(keys) == 0:
            print("Using all keys")
            keys = dsx.keys()

        # Build generator

        def generate():
            for s in dsx[example_dim]:
                inp = {}
                for key in keys:
                    inp[key] = dsx[key].sel({example_dim: s}).to_numpy()
                yield inp

        # Get key sizes
        output_signature_inp = {}
        for key in keys:
            example_data = dsx[key].isel({example_dim: 0})
            output_signature_inp[key] = tf.TensorSpec(
                example_data.shape, dtype=example_data.dtype, name=key
            )
        return tf.data.Dataset.from_generator(
            generate,
            output_signature=(output_signature_inp),
        )


class Merger:
    def __init__(self, engine="netcdf4", concat_dim="column", options=None):
        self.engine = engine
        self.concat_dim = concat_dim
        self.options = options if options is not None else {}

    def to_xarray(self, paths, **kwargs):
        return xr.open_mfdataset(
            paths,
            engine=self.engine,
            concat_dim=self.concat_dim,
            combine="nested",
            coords="minimal",
            data_vars="minimal",
            preprocess=broadcast_irradiance,
            compat="override",
            parallel=True,
            **self.options,
        )


def broadcast_irradiance(ds):
    if "solar_irradiance" in ds:
        ds["solar_irradiance"] = xr.broadcast(ds["solar_irradiance"], ds["lat"])[0]
    return ds
