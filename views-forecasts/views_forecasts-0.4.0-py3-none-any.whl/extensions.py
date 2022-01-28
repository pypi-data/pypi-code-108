import re
import pandas as pd
from .file_ops import ForecastsStore
from .db_ops import *
from typing import *
from hashlib import sha256

@pd.api.extensions.register_dataframe_accessor("forecasts")
class ForecastAccessor:
    """
    A Pandas data-frame accessor for the ViEWS predictions.
    Can be explored using df.pred3.* and pd.DataFrame.pred3.*
    Any dataframe having the correct format.
    """
    def __init__(self, pandas_obj:pd.DataFrame,
                 run: Union[int,str,pd.DataFrame,pd.Series,ViewsMetadata().Runs] = 'tests'):
        """
        Initializes the accessor and validates that it really is a Views Prediction
        Extracts some basic metadata.
        :param pandas_obj: A pandas DataFrame containing a ViEWS prediction df
        """

        self.run = ViewsMetadata().run_to_run_id(run)

        self.ACCEPTABLE_SPACE = {'c':['country_id', 'c_id'],
                                 'a':['actor_id','a_id'],
                                 'pg':['priogrid_id','priogrid_gid', 'pg_gid', 'pg_id']}

        self.ACCEPTABLE_TIME = {'m': ['month_id'],
                                'y': ['year_id', 'year']}

        self.ACCEPTABLE_PRED_COLS = {'osa': ['^(.*?)step\w?_pred\w?_\w\w*'],
                                     'ds': ['^(.*?)(ds_)?pred\w?$']}

        self._obj = pandas_obj.reset_index()

        # Validators and object initializers:
        ##
        # Makes sure the object is a ViEWS prediction.
        # Extracts metadata and data about the object.
        # If it cannot be recognized as a prediction, throw AttributeError per pd docs
        # No matter where it comes from, builds an index


        self.spatial_loa = self.__fetch_spatial_loa()
        self.temporal_loa = self.__fetch_temporal_loa()
        self.__make_indexes()

        self.prediction_columns = self.__autodetect_pred_columns()
        self.target = self.__autodetect_target()
        self.steps = self.__autodetect_steps()
        self.ds = True if len(self.__autodetect_pred_columns(osa=False,ds=True)) > 0 else False
        self.osa = True if len(self.__autodetect_pred_columns(osa=True,ds=False)) > 0 else False

        # Fetch the temporal extents
        self.time_min, self.space_min, self.time_max, self.space_max = self.__fetch_extents()

        # Autodetect the target variable.
        self.target = self.__autodetect_target()
        self.steps = self.__autodetect_steps()

        self.description = None

    def __autodetect_steps(self):
        possible_steps = [i.rsplit('_', 1)[-1] for i in self._obj.columns
                          if i in self.__autodetect_pred_columns(osa=True,ds=False)]
        steps = sorted({int(i) for i in possible_steps if i.isnumeric()})
        return steps

    def __autodetect_pred_columns(self, osa=True, ds=True):
        test_reg = []
        columns = []
        if osa:
            test_reg += self.ACCEPTABLE_PRED_COLS['osa']
        if ds:
            test_reg += self.ACCEPTABLE_PRED_COLS['ds']

        for regex in test_reg:
            exp = re.compile(regex)
            for col in self._obj.columns:
                if exp.match(col) is not None:
                    columns += [col]

        return sorted(set(columns))

    def __make_indexes(self, canonical_form = True):
        """
        Reindexes the data frame using the time-month format.
        This is done in order to be able to parse in multiple formats of data frames as input
        (i.e. ingester style, viewser style, R style etc. etc).

        :param canonical_form: Renames the indexes either to the canonical form (e.g. 'country_id','month_id') if true;
        keeps generics (time_id, space_id) if false
        :return: none, alters the original df.
        """

        loa_space = self.ACCEPTABLE_SPACE[self.spatial_loa]
        loa_time = self.ACCEPTABLE_TIME[self.temporal_loa]

        for name in loa_space:
            try:
                self._obj['spatial_id'] = self._obj[name]
                del self._obj[name]
            except KeyError:
                pass

        for name in loa_time:
            try:
                self._obj['temporal_id'] = self._obj[name]
                del self._obj[name]
            except KeyError:
                pass

        self._obj = self._obj.set_index(['temporal_id', 'spatial_id'])

        if canonical_form:
            self._obj.index.names = [loa_time[0], loa_space[0]]

    @staticmethod
    def __set_in_set(set1, set2):
        for i in set1:
            if len(set2.intersection(set(i[1]))) > 0:
                return i[0]
        return None

    def __fetch_spatial_loa(self):
        match = self.__set_in_set(self.ACCEPTABLE_SPACE.items(), set(self._obj.columns))
        if match is None:
            raise AttributeError("No spatial dimension [c,pg,a,...] column/index identified...")
        return match

    def __fetch_temporal_loa(self):
        match = self.__set_in_set(self.ACCEPTABLE_TIME.items(), set(self._obj.columns))
        if match is None:
            raise AttributeError("No temporal dimension [m,y,...] column/index identified...")
        return match

    def __autodetect_target(self):
        """
        The target is defined as the first column of the df that does not contain an _id or a _pred name.
        """
        try:
            return [i for i in self._obj.columns if '_id' not in i and i not in self.__autodetect_pred_columns()][0]
        except IndexError:
            raise AttributeError("""No potential target variable found! This isn't a ViEWS prediction!""")

    def __fetch_extents(self):
        return self._obj.index.min() + self._obj.index.max()

    def set_target(self, target):
        """
        Manually sets the target to another column in the df
        """
        if '_id' in target or target in self.__autodetect_pred_columns():
            raise AttributeError(f"Cannot set {target} variable as it is either a prediction or a target!")
        if target not in self._obj.columns:
            raise AttributeError(f"{target} is not a valid column in the df!")
        self.target = target
        return self

    def set_description(self, description:str):
        self.description = description
        return self

    def set_run(self, run: Union[int,str,pd.DataFrame,ViewsMetadata().Runs]):
        self.run = ViewsMetadata().run_to_run_id(run)
        return self

    def get_run(self):
        return ViewsMetadata().get_runs_by_id(self.run)

    def to_store(self, name: str, overwrite: bool = False, check_transfer:bool = False):
        """
        Store a prediction into our server-side store
        :param name: The name that this prediction will be available as.
        :param run: The name of the run
        :param overwrite: Overwrite if found
        :param check_transfer: Reloads the file from server checking that the hash is correct (i.e. transfer ok)
        :return: void
        """

        already_in_db = ViewsMetadata().with_run(self.run).with_name(name, strict=True).fetch()

        if already_in_db.shape[0] > 0 and overwrite:
            ViewsMetadata().delete(already_in_db.id.max())


        ForecastsStore().write(name=name, run=self.run, overwrite=overwrite, df=self._obj)
        ViewsMetadata().new(
            name=name,
            description=self.description,
            file_name=f'pr_{self.run}_{name}.parquet',
            run=self.run,
            spatial_loa=self.spatial_loa,
            temporal_loa=self.temporal_loa,
            ds=self.ds,
            osa=self.osa,
            time_min=self.time_min,
            time_max=self.time_max,
            space_min=self.space_min,
            space_max=self.space_max,
            steps=self.steps,
            target=self.target,
            prediction_columns=self.prediction_columns
        )

        if check_transfer:
            df = ForecastsStore().read(name=name, run=self.run)
            if self.__get_hash(df) != self.__get_hash(self._obj):
                raise IOError("Transfer did not succeed!")

    @staticmethod
    def __get_hash(df) -> str:
        return sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

    @classmethod
    def read_store(cls, name: str, run: str='tests') -> pd.DataFrame:
        """
        Retrieve a prediction from the server-side store.
        :param name: The name of the prediction and its run. If run not available
        :param run:
        :return: a predictions dataframe and a metadata object.
        """
        run = ViewsMetadata().run_to_run_id(run)
        df = ForecastsStore().read(name=name, run=run)
        return cls(df, run=run).as_df

    @classmethod
    def read_filename(cls, file_name: str) -> pd.DataFrame:
        df = ForecastsStore().read_filename(file_name)
        run = int(file_name.split('_')[1])
        return cls(df, run=run).as_df

    @classmethod
    def read_filtered_df(cls, filtered_df: pd.DataFrame) -> list[pd.DataFrame]:
        """
        Returns a list of prediction dataframes based on a dataframe obtained from the ViewsMetadata()...fetch().
        :param filtered_df: A dataframe obtained from the filter
        :return: A list of prediction dataframes.
        """
        bulk_set = []
        for name in list(filtered_df.file_name):
            bulk_set += [cls.read_filename(name)]
        return bulk_set

    @property
    def as_viewser(self):
        return self._obj

    @property
    def as_df(self):
        return self._obj

    @property
    def as_ingester3(self):
        df = self._obj.copy()
        df = df[self.__autodetect_pred_columns()].reset_index()
        return df

    @property
    def extents(self):
        return self.time_min, self.time_max




# target, description, extra_metadata.

