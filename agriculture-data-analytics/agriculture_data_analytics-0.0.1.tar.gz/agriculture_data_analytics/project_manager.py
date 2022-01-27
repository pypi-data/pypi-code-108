# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from data_analytics.github import RepositoryFileManager, RELATIVE_PATH


REPOSITORY_URL = 'https://github.com/markcrowe-com/agriculture-data-analytics'


class ProjectArtifactManager(RepositoryFileManager):

    def __init__(self, relative_path: str = RELATIVE_PATH, repository_url: str = REPOSITORY_URL, is_remote: bool = False):
        super().__init__(repository_url, relative_path, is_remote)
        self.BOVINE_TUBERCULOSIS_EDA_FILENAME: str = "artifacts/bovine-tuberculosis-eda-output.csv"
        self.CATTLE_BEEF_EXPORTS_EDA_FILENAME: str = "artifacts/cattle-beef-exports-eda-output.csv"
        self.COUNTY_BOVINE_TUBERCULOSIS_EDA_FILENAME: str = "artifacts/county-bovine-tuberculosis-eda-output.csv"

    def get_bovine_tuberculosis_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.BOVINE_TUBERCULOSIS_EDA_FILENAME)

    def get_cattle_beef_exports_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.CATTLE_BEEF_EXPORTS_EDA_FILENAME)

    def get_county_bovine_tuberculosis_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.COUNTY_BOVINE_TUBERCULOSIS_EDA_FILENAME)


class ProjectAssetManager(RepositoryFileManager):

    def __init__(self, relative_path: str = RELATIVE_PATH, repository_url: str = REPOSITORY_URL, is_remote: bool = False):
        super().__init__(repository_url, relative_path, is_remote)
        self.CATTLE_BEEF_EXPORTS_FILENAME: str = "assets/cso-tsa04-exports-of-cattle-and-beef-1930-2020-2022-01Jan-13.csv"
        self.CATTLE_BEEF_MONTHLY_EXPORTS_FILENAME: str = "assets/cso-tsm04-exports-of-cattle-and-beef-1970-2021-2022-01Jan-13.csv"
        self.BOVINE_TUBERCULOSIS_FILENAME: str = "assets/cso-daa01-bovine-tuberculosis-2022-01-Jan-15.csv"
        self.BOVINE_TUBERCULOSIS_QUARTERLY_FILENAME: str = "assets/cso-daq01-bovine-tuberculosis-quarterly-2022-01-Jan-15.csv"

    def get_bovine_tuberculosis_filepath(self) -> str:
        return super().get_repository_filepath(self.BOVINE_TUBERCULOSIS_FILENAME)

    def get_bovine_tuberculosis_quarterly_filepath(self) -> str:
        return super().get_repository_filepath(self.BOVINE_TUBERCULOSIS_QUARTERLY_FILENAME)

    def get_cattle_beef_exports_filepath(self) -> str:
        return super().get_repository_filepath(self.CATTLE_BEEF_EXPORTS_FILENAME)

    def get_cattle_beef_monthly_exports_filepath(self) -> str:
        return super().get_repository_filepath(self.CATTLE_BEEF_MONTHLY_EXPORTS_FILENAME)
