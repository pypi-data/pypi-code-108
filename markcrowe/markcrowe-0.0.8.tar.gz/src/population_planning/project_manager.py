# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from data_analytics.github import RepositoryFileManager, RELATIVE_PATH


REPOSITORY_URL = 'https://github.com/markcrowe-com/population-planning-data-analytics/blob/master'


class ProjectArtifactManager(RepositoryFileManager):

    def __init__(self, repository_url: str = REPOSITORY_URL, relative_path: str = RELATIVE_PATH, is_remote: bool = False):
        super().__init__(repository_url, relative_path, is_remote)

        self.COUNTY_BIRTHS_EDA_FILENAME = "artifacts/births-by-county-1985-2020-eda-output.csv"
        self.BIRTHS_DEATHS_MARRIAGES_EDA_FILENAME = "artifacts/births-deaths-marriages-ireland-1960-2021-eda-output.csv"
        self.DIVORCES_ML_FILENAME = "assets/divorces-2011-and-2016-ml-output.csv"
        self.POPULATION_EDA_FILENAME = "artifacts/population-1950-2021-eda-output.csv"
        self.REGION_DEATHS_EDA_FILENAME = "artifacts/deaths-region-2007-2020-eda-output.csv"

    def get_all_eda_filepaths(self, query_string: str = '') -> list:
        query_string_state = self.query_string
        self.query_string = query_string
        filepaths = [self.get_county_births_eda_filepath(),
                     self.get_births_deaths_marriages_eda_filepath(),
                     self.get_population_eda_filepath(),
                     self.get_region_deaths_eda_filepath()]
        self.query_string = query_string_state
        return filepaths

    def get_county_births_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.COUNTY_BIRTHS_EDA_FILENAME)

    def get_births_deaths_marriages_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.BIRTHS_DEATHS_MARRIAGES_EDA_FILENAME)

    def get_divorces_ml_filepath(self) -> str:
        return super().get_repository_filepath(self.DIVORCES_ML_FILENAME)

    def get_population_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.POPULATION_EDA_FILENAME)

    def get_region_deaths_eda_filepath(self) -> str:
        return super().get_repository_filepath(self.REGION_DEATHS_EDA_FILENAME)


class ProjectAssetManager(RepositoryFileManager):

    def __init__(self, repository_url: str = REPOSITORY_URL, relative_path: str = RELATIVE_PATH, is_remote: bool = False):
        super().__init__(repository_url, relative_path, is_remote)

        self.BIRTHS_DEATHS_MARRIAGES_FILENAME = "assets/births-deaths-marriages-ireland-1960-2021.csv"
        self.COUNTY_BIRTHS_FILENAME = "assets/births-by-county-1985-2020.csv"
        self.DIVORCES_FILENAME = "assets/2021-12Dec-11-divorces-2011-and-2016-e4062-filtered.csv"
        self.POPULATION_ESTIMATES_FILENAME = "assets/2021-12Dec-11-population-estimates-1950-2021-pea01.csv"
        self.REGION_DEATHS_FILENAME = "assets/deaths-region-2007-2020.csv"

    def get_all_filepaths(self, query_string: str = '') -> list:
        query_string_state = self.query_string
        self.query_string = query_string
        filepaths = [self.get_county_births_filepath(),
                     self.get_births_deaths_marriages_filepath(),
                     self.get_region_deaths_filepath()]
        self.query_string = query_string_state
        return filepaths

    def get_births_deaths_marriages_filepath(self) -> str:
        return super().get_repository_filepath(self.BIRTHS_DEATHS_MARRIAGES_FILENAME)

    def get_county_births_filepath(self) -> str:
        return super().get_repository_filepath(self.COUNTY_BIRTHS_FILENAME)

    def get_divorces_filepath(self) -> str:
        return super().get_repository_filepath(self.DIVORCES_FILENAME)

    def get_population_estimates_filepath(self) -> str:
        return super().get_repository_filepath(self.POPULATION_ESTIMATES_FILENAME)

    def get_region_deaths_filepath(self) -> str:
        return super().get_repository_filepath(self.REGION_DEATHS_FILENAME)
