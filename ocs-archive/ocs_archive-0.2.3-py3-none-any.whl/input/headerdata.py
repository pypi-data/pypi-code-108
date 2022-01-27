from ocs_archive.settings import settings


class HeaderData:
    def __init__(self, header_data: dict = None):
        """Creates HeaderData with input dictionary of headers."""
        if header_data is None:
            header_data = {}
        self.header_data = header_data

    def get_headers(self):
        return self.header_data

    def update_headers(self, new_headers: dict):
        self.header_data.update(new_headers)

    def remove_header(self, key: str):
        try:
            del self.header_data[key]
        except KeyError:
            pass

    def get_archive_frame_data(self):
        return {
            'reduction_level': self.get_reduction_level(),
            'observation_day': self.get_observation_day(),
            'observation_date': self.get_observation_date(),
            'proposal_id': self.get_proposal_id(),
            'instrument_id': self.get_instrument_id(),
            'target_name': self.get_target_name(),
            'site_id': self.get_site_id(),
            'telescope_id': self.get_telescope_id(),
            'exposure_time': self.get_exposure_time(),
            'primary_optical_element': self.get_primary_optical_element(),
            'public_date': self.get_public_date(),
            'configuration_type': self.get_configuration_type(),
            'observation_id': self.get_observation_id(),
            'request_id': self.get_request_id(),
            'related_frame_filenames': list(self.get_related_frames().values())
        }

    def headers_are_set(self, keys: list):
        """Check that the values for the provided headers are set."""
        headers = self.get_headers()
        empty_values = [None, '']
        values = [headers.get(key) for key in keys]
        return all([value not in empty_values for value in values])

    def get_related_frame_keys(self):
        return settings.RELATED_FRAME_KEYS

    def get_related_frames(self):
        headers = self.get_headers()
        keys = self.get_related_frame_keys()
        related_frames = {}
        for key in keys:
            if key in headers and headers[key]:
                related_frames[key] = headers[key]
        return related_frames

    def get_observation_day(self):
        return self.get_headers().get(settings.OBSERVATION_DAY_KEY)

    def get_observation_date(self):
        return self.get_headers().get(settings.OBSERVATION_DATE_KEY)

    def get_proposal_id(self):
        return self.get_headers().get(settings.PROPOSAL_ID_KEY)

    def get_configuration_type(self):
        return self.get_headers().get(settings.CONFIGURATION_TYPE_KEY)

    def get_exposure_time(self):
        return self.get_headers().get(settings.EXPOSURE_TIME_KEY)
    
    def get_public_date(self):
        return self.get_headers().get(settings.PUBLIC_DATE_KEY)

    def get_reduction_level(self):
        return self.get_headers().get(settings.REDUCTION_LEVEL_KEY, 0)

    def get_instrument_id(self):
        return self.get_headers().get(settings.INSTRUMENT_ID_KEY)

    def get_site_id(self):
        return self.get_headers().get(settings.SITE_ID_KEY)

    def get_primary_optical_element(self):
        return self.get_headers().get(settings.PRIMARY_OPTICAL_ELEMENT_KEY)

    def get_target_name(self):
        return self.get_headers().get(settings.TARGET_NAME_KEY)

    def get_telescope_id(self):
        return self.get_headers().get(settings.TELESCOPE_ID_KEY)

    def get_observation_id(self):
        return self.get_headers().get(settings.OBSERVATION_ID_KEY)

    def get_configuration_id(self):
        return self.get_headers().get(settings.CONFIGURATION_ID_KEY)

    def get_request_id(self):
        return self.get_headers().get(settings.REQUEST_ID_KEY)

    def get_requestgroup_id(self):
        return self.get_headers().get(settings.REQUESTGROUP_ID_KEY)
