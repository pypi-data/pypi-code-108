from ingester3.scratch import source_db_path
from ingester3.config import views_user
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import pandas as pd
from numpy import nan
from typing import Union
from datetime import datetime


class ViewsMetadata:
    def __init__(self, show_deleted=False):
        self.engine = sa.create_engine(source_db_path)

        self.show_deleted = show_deleted

        self.metadata = sa.MetaData(schema="forecasts_metadata")
        self.metadata.reflect(self.engine)
        Base = automap_base()
        Base.prepare(self.engine, reflect=True, schema="forecasts_metadata")
        self.Runs = Base.classes.runs
        self.ModelGen = Base.classes.model_generations
        self.Forecasts = Base.classes.forecasts
        self.session = sessionmaker(bind=self.engine)()

        self.__reset_query()

    def __query_runs(self, where_subpart):
        list_runs = []
        for instance in self.session.query(self.Runs).filter(where_subpart).order_by(self.Runs.id):
            list_runs += [(instance.id, instance.name, instance.description, instance.min_month, instance.max_month)]
        return pd.DataFrame(list_runs, columns=['id', 'name', 'description', 'min_month', 'max_month']).set_index('id')

    def get_runs(self) -> pd.DataFrame:
        """
        :return: Returns a dataframe listing all the runs in the latest form.
        """
        return self.__query_runs(True)

    def get_runs_by_id(self, id):
        """
        :param id: The Id of the run
        :return:
        """
        return self.__query_runs(self.Runs.id == id)

    def get_runs_by_name(self, name, strict=False):
        """
        :param name: The name of the run to search for
        :param strict: If strict, exact matching is enforced. Otherwise, partial matching only.
        :return: Returns a dataframe listing all the runs matching a certain name.
        """
        if not strict:
            name = f"%{name}%"
        return self.__query_runs(self.Runs.name.ilike(name))

    def get_run_id_from_name(self, name):
        """
        Returns the id of the run matching. Returns None if no run was found. If you need a more complex system, use
        "get runs by name".
        :param name: The name to search for. Search is strict. If you want a fuzzy search, use the "get_runs_by_name"
        :return: the id of the run
        """
        x = self.get_runs_by_name(name).index.max()
        if x is nan: return None
        return int(x)

    @property
    def test_run(self):
        """
        Returns the id of the test run.
        :return: The id of the test run
        """
        return self.get_runs_by_name('test').index.max()

    @property
    def newest_run(self):
        """
        Return the id of the most recent (highest id) run.
        :return: The id of the te
        """
        return self.get_runs().index.max()

    def new_run(self, name: str, description: str, min_month: int, max_month: int) -> int:
        """
        Add a new run to the database.
        :param name: The name of the run, as a string (e.g. r_2021_01).
        :param description: A longer description of the run, as a string (e.g. March run). Optional.
        :param min_month: The minimum month that should be included in models assigned to the run.
        :param max_month: The maximum month that should be included in models assigned to the run.
        :return: Returns the ID of the currently inserted run.
        """

        if len(name) == 0 or name is None:
            raise KeyError("No empty name allowed!")

        if self.__query_runs(self.Runs.name == name).shape[0] > 0:
            raise KeyError(f"Run {name} exists in the DB as id:"
                             f" {self.__query_runs(self.Runs.name == name).index.max()}")

        try:
            # if user by mistake flips min and max, flip it back
            # adn don't crash if one of them is a None.
            if min_month > max_month:
                min_month, max_month = max_month, min_month
        except TypeError:
            pass

        self.session.add(self.Runs(name=name, description=description, min_month=min_month, max_month=max_month))
        self.session.commit()
        return self.__query_runs(True).index.max()

    def new(self,
            name: str,
            description: str,
            file_name: str,
            run: int,
            spatial_loa: str,
            temporal_loa: str,
            ds: bool,
            osa: bool,
            time_min: int,
            time_max: int,
            space_min: int,
            space_max: int,
            steps: list,
            target: str,
            prediction_columns: list
            ):

        """
        Insert a new metadata row to the DB.
        :param name: name of the dataframe
        :param description: description of the dataframe as text
        :param file_name: file name
        :param run: the run_id (either as a name, an id or as a run_id data frame).
        :param spatial_loa: spatial loa (c,pg,a)
        :param temporal_loa: temporal loa (m,y)
        :param ds: bool - is it dynasim.
        :param osa: bool - is one-step-ahead.
        :param time_min: first month in prediction df
        :param time_max: last month in prediction df
        :param space_min: minimal space id in df
        :param space_max: maximal space id in df
        :param steps: a list of steps
        :param target: the target
        :param prediction_columns: a list of prediction column
        :return: the ID of the inserted data-frame
        """

        run_id = self.run_to_run_id(run)

        if len(name) == 0 or name is None:
            raise KeyError("No empty name allowed!")

        if time_min > time_max:
            time_max, time_min = time_min, time_max

        new_data = self.Forecasts(
                                  name=name,
                                  description=description,
                                  file_name=file_name,
                                  runs_id=int(run_id),
                                  user_name=views_user,
                                  spatial_loa=spatial_loa,
                                  temporal_loa=temporal_loa,
                                  ds=ds,
                                  osa=osa,
                                  time_min=time_min,
                                  time_max=time_max,
                                  space_min=space_min,
                                  space_max=space_max,
                                  steps=steps,
                                  target=target,
                                  prediction_columns=prediction_columns,
                                  model_generations=self.session.query(self.ModelGen).get(1),
                                  deleted=False,
                                  date_written=datetime.now()
                                  )

        self.session.add(new_data)
        self.session.commit()
        return new_data.id

    def with_id(self, id):
        """
        Filter for files that have a certain db_id.
        :param id: db id
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        self.queries += [self.Forecasts.id == id]
        return self

    def with_user(self, user):
        """
        Filters for files that a user sent to the store. It automatically knows who you are.
        :param user: A Views username
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        self.queries += [self.Forecasts.user_name == user]
        return self

    def mine(self):
        """
        Filters for files that you sent to the store. It automatically knows who you are.
        Equivalent to with_user(user=$VIEWS_USER)
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        self.with_user(user=views_user)
        return self

    def with_loa(self, spatial_loa: str = 'c', temporal_loa: str = 'm'):
        """
        Retrieve only prediction files at loa.
        :param spatial_loa: A views LOA, any of {c,pg,a}. None, * or ? serve as wildcards for ALL
        :param temporal_loa: A views LOA, any of {y,m}. None, * or ? serve as wildcards for ALL
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        spatial_query = []

        if spatial_loa not in ('*', '?', None):
            spatial_query += [self.Forecasts.spatial_loa == spatial_loa.lower().strip()]
        if temporal_loa not in ('*', '?', None):
            spatial_query += [self.Forecasts.temporal_loa == temporal_loa.lower().strip()]
        self.queries += [sa.and_(*spatial_query).self_group()]
        return self

    def run_to_run_id(self, run:Union[str,int,pd.DataFrame,pd.Series]) -> int:
        """
        Given a run instance specified either as an int, a pd.DataFrame or an int,
        make it quack like a duck and return the id.

        It's an ugly hack allowing more upstream flexibilty and not fixing the specification for Runs until
        we have a working data model that we've settled on.

        :param run: A run given either as a df, or as a
        :return: an id
        """
        if run is None:
            raise KeyError(f"None is not a valid run")
        if type(run) == int:
            return run
        if type(run) == str:
            try:
                return int(self.get_run_id_from_name(run.lower()))
            except TypeError:
                raise KeyError(f"Run {run} not found!")
        if isinstance(run, self.Runs):
            return run.id
        if isinstance(run, pd.DataFrame):
            try:
                return int(run.index.max())
            except:
                raise KeyError("Not a valid DataFrame shape!")
        if isinstance(run, pd.Series):
            return int(run.name)
        raise TypeError("I'm able to parse a lot, but not this. Give me an int,str,pandas df/S, or Runs object!")

    def with_run(self, run):
        run_id = self.run_to_run_id(run)
        ##print(run_id)
        self.queries += [self.Forecasts.runs_id == run_id]
        return self

    def with_target(self, target: str, strict: bool = False):
        """
        Search for all predictions containing a certain target
        :param target: The target of a prediction dataframe.
        :param strict: Strict will return only exact name matches, otherwise partial matches will work.
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        if not strict:
            target = f"%{target}%"
        self.queries += [self.Forecasts.target.ilike(target)]
        return self


    def with_name(self, name: str, strict: bool = False):
        """
        Search for all predictions containing a certain loa.
        :param name: The name of a prediction dataframe.
        :param strict: Strict will return only exact name matches, otherwise partial matches will work.
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        if not strict:
            name = f"%{name}%"
        self.queries += [self.Forecasts.name.ilike(name)]
        return self

    def with_description(self, description: str, strict: bool = False):
        """
        Search for all predictions containing a certain loa.
        :param spatial_loa: A views LOA, any of {c,pg,a}. None, * or ? serve as wildcards for ALL
        :param temporal_loa: A views LOA, any of {y,m}. None, * or ? serve as wildcards for ALL
        :return: A chain of queries. Retrieve your chain by using `fetch`
        """
        if not strict:
            description = f"%{description}%"
        self.queries += [self.Forecasts.description.ilike(description)]
        return self

    def with_time_range(self, low:int, high:int, exact=False):
        """
        It will retrieve only those predictions containing the time range you specify.
        If exact is specified, the prediction boundaries must be exactly those specified
        (i.e., if low = 100 and high = 200, it will return only those prediction tables that start EXACTLY at 100
        and end exactly at 200
        :param low:
        :param high:
        :param exact:
        :return:
        """
        low, high = int(low), int(high)
        opcode = '=' if exact else "<@"
        self.queries += [sa.text(f"'[{low},{high}]'::int4range {opcode} int4range(time_min,time_max,'[]')")]
        return self


    def with_steps(self, steps: list):
        """
        Search for all predictions containing the set of steps that you are passing
        :param steps: any iterable containing steps
        :return:  A chain of queries. Retrieve your chain by using `fetch`
        """
        steps = ','.join([str(i) for i in steps])
        self.queries += [sa.text(f"'[{steps}]' <@ steps::jsonb")]
        return self

    def with_step(self, step: int):
        """
        Search for all predictions containing one step
        :param step: A step, supplied as an int (e.g. 3)
        :return:  A chain of queries. Retrieve your chain by using `fetch`
        """
        self.with_steps([step])
        return self

    def __reset_query(self):
        """
        Resets the query chain.
        :return: An empty/default query chain.
        """
        if self.show_deleted:
            self.queries = [True]
        else:
            self.queries = [self.Forecasts.deleted == False]
        return self

    def __query_forecasts(self, op_code='and'):
        """
        Queries the metadata tables based on the filtering criteria added in self.filters, and resets the filters
        :return: Returns a dataframe listing all the runs based on the filtring criteria
        """
        op_code = sa.or_ if op_code == 'or' else sa.and_
        if not self.queries:
            self.queries = self.__reset_query()
        sql = sa.select(self.Forecasts).where(op_code(*self.queries)).order_by(self.Forecasts.id)
        #print(">>>",sql)
        with self.engine.connect() as con:
            df = pd.read_sql(sql=sql, con=con)
        return df

    def fetch(self, op_code='and'):
        return self.__query_forecasts(op_code=op_code)

    def delete(self, id):
        self.session.query(self.Forecasts).filter(self.Forecasts.id == int(id)).delete()
        self.session.commit()

    def soft_delete(self, id):
        soft = self.session.query(self.Forecasts).get(id)
        soft.deleted = True
        self.session.commit()





