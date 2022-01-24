import os
from ..dataset_validator import DatasetValidatorBase

class FullFieldDatasetValidator(DatasetValidatorBase):

    def _validate(self):
        self._check_not_empty()
        self._convert_negative_indices()
        self._get_resources()
        self._get_output_filename()
        self._check_can_do_flatfield()
        self._check_slice_indices()
        self._handle_processing_mode()
        self._handle_binning()
        self._check_output_file()


    def _check_can_do_flatfield(self):
        if self.nabu_config["preproc"]["flatfield"]:
            darks = self.dataset_info.darks
            assert len(darks) > 0, "Need at least one dark to perform flat-field correction"
            for dark_id, dark_url in darks.items():
                assert os.path.isfile(dark_url.file_path()), "Dark file %s not found" % dark_url.file_path()
            flats = self.dataset_info.flats
            assert len(flats) > 0, "Need at least one flat to perform flat-field correction"
            for flat_id, flat_url in flats.items():
                assert os.path.isfile(flat_url.file_path()), "Flat file %s not found" % flat_url.file_path()


    def _check_slice_indices(self):
        nx, nz = self.dataset_info.radio_dims
        rec_params = self.nabu_config["reconstruction"]
        if rec_params["enable_halftomo"]:
            ny, nx = self._get_nx_ny()
        what = (
            ("start_x", "end_x", nx),
            ("start_y", "end_y", nx),
            ("start_z", "end_z", nz)
        )
        for (start_name, end_name, numels) in what:
            self._check_start_end_idx(
                rec_params[start_name],
                rec_params[end_name],
                numels,
                start_name=start_name,
                end_name=end_name
            )
