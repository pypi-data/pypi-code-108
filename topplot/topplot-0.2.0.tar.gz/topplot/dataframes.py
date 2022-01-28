from pandas import DataFrame


class Dataframes:
    def __init__(self):
        self.cpus_df: DataFrame = DataFrame()
        self.tasks_df: DataFrame = DataFrame()
        self.poi_df: DataFrame = DataFrame()
        self.mem_df: DataFrame = DataFrame()
        self.core_dfs: DataFrame = DataFrame()
