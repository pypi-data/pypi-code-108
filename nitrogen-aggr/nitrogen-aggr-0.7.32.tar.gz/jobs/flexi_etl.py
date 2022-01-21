import traceback
import pyspark.sql.functions as F
from dependencies.exception import exception_handler
from jobs.etl_job_base import EtlJobBase
from constants.constants_configs import Config as Constant_Config
from dependencies import spark_utils as Su
from dependencies.post_gres import CadmiumPostGres
import re
import psycopg2

class FlexiEtl(EtlJobBase):

    def init_flexi_configurations(self):
        # Note: if no cad job id from aggregation-provider-member.yaml file use this value, which is from run_pipeline.sh.
        cad_job_id = self.config[Constant_Config.JOB_ID]
        # project_root_path = self.config[Constant_Config.PROJECT_ROOT_PATH] # todo

        # Extract variables:
        for var in self.config[Constant_Config.STEP_CONFIG]['variables']:
            key = var.split("=")[0].strip()
            value = var.split("=")[1].strip()
            self.log.info(f"value is {value}")
            if value[0] == "{" and value[-1] == "}":
                value_to_trans = value[1:-1]
                self.log.info(f"value to trans {value_to_trans}")
                value_after_trans = None
                for v in value_to_trans.split("."):
                    if value_after_trans is None:
                        if v == "config":
                            value_after_trans = self.config
                    else:
                        if v in value_after_trans:
                            value_after_trans = value_after_trans[v]
                        else:
                            # Thinking is that this allows up to load arbitrarily many step configs under key name v
                            try:
                                value_after_trans = self.get_config_for_step(v)
                                self.config[v] = value_after_trans
                            except:
                                raise Exception(f"{v} not in {value_after_trans}")
                value_after_trans = f'"{value_after_trans}"'
            else:
                value_after_trans = value
            self.log.info(f"key: {key}, value_after_trans: {value_after_trans}")
            exec("%s=%s" % (key, eval("f'{}'".format(value_after_trans.replace("'", "\\'")))), globals())

        # Note: cad job id from aggregation-provider-member.yaml else use from run_pipeline.sh
        self.log.info(cad_job_id)
        if cad_job_id is not None:
            self.config[Constant_Config.JOB_ID] = cad_job_id
        self.log.info(cad_job_id)
        self.log.info(f"cad_job_id {cad_job_id} and {self.config[Constant_Config.JOB_ID]}")
        # CAST as int
        self.config[Constant_Config.STEP_CONFIG]['fiscal_month_end'] = int(
            self.config['project_config'][Constant_Config.FISCAL_MONTH_END])

        try:
            self.config[Constant_Config.STEP_CONFIG]['parent_demo_client'] = str(
                self.config['project_config'][Constant_Config.PARENT_DEMO_CLIENT])
        except KeyError: pass

        def need_eval(_s):
            pattern = r"[*{}*]"
            found = re.search(pattern, _s)
            if found: return True
            return False

        def add_variable_to_dict(json_input, _max_cnt, _cnt=1):
            """ Recursively goes through the nested json input and
                evaluates the path that has {} and replaces that with
                a corresponding variable input.
            """
            if isinstance(json_input, dict):
                for k, v in json_input.items():
                    if isinstance(v, str) and need_eval(v):
                        json_input[k] = eval('f"""{}"""'.format(v))
                    if _cnt == _max_cnt:
                        return None  # end
                    else:
                        add_variable_to_dict(v, _max_cnt, _cnt=_cnt + 1)
            elif isinstance(json_input, list):
                for item in json_input:
                    add_variable_to_dict(item, _max_cnt, _cnt=_cnt + 1)

        add_variable_to_dict(self.config[Constant_Config.STEP_CONFIG],
                             _max_cnt=len(self.config[Constant_Config.STEP_CONFIG].keys()), _cnt=1)

        if 'database_name' in globals():
            self.config['project_config']['postgres']['database_name'] = database_name
        if 'schema' in globals():
            self.config['project_config']['postgres']['schema'] = schema

        if debug:  self.log.info(self.config[Constant_Config.STEP_CONFIG])
        if debug: self.log.info(f"All configurations: {self.config}")

    @exception_handler
    def extract_data(self):
        """Load test_data from Parquet file format.
       :return: Spark DataFrame.
       """
        step_config = self.config[Constant_Config.STEP_CONFIG]
        env = self.config.get('env',None)
        
        extract = step_config.get('Extract', [])
        if len(extract) > 0:
            self.log.info(f"step_config['Extract'] {step_config['Extract']}")
            for df_name, setting in step_config['Extract'].items():
                self.log.info(f"Key value: {df_name} and {setting}")
                if "type" not in setting:
                    self.log.warn(f"Extract type has not been specified for df_name: {df_name}")
                    raise Exception(f"Extract type has not been specified for table: {df_name}")
                type = setting['type']
                if type == "parquet":
                    self.extract_from_parquet(df_name=df_name, setting=setting)
                elif type == "csv":
                    self.extract_from_csv(df_name=df_name, setting=setting)
                elif type == "postgres":
                    if setting.get('skip_if_local', False) and env == 'local':
                        print(f"Skip if local, postgres {setting}")
                    else:    
                        self.extract_from_postgres(df_name=df_name, setting=setting)
        return

    @exception_handler
    def transform_data(self):
        self.log.info("Transform")
        env = self.config.get('env', None)
        step_config = self.config[Constant_Config.STEP_CONFIG]
        debug = step_config.get('debug', False)
        log_pg = step_config.get('log_pg', False)
        if step_config.get('register_udfs', False):
            Su.register_udfs(_spark=self.spark)
            self.log.info("Udfs registered.")

        transform = step_config.get('Transform', [])
        if len(transform) > 0:
            self.log.info(f"step_config['Transform'] {transform}")

            for k, v in transform.items():
                self.log.info(f"Key value: {k} and {v}")
                if log_pg: self.log.log_into_postgresql_job_log(f"Key value: {k} and {v}")
                if v.get('create_local_job_id', False) and env == 'local':
                    if debug: print(f"SKIP {env}")
                    self.spark.sql("""
                        SELECT '888' AS cad_job_id
                    """).createOrReplaceTempView(k)
                    continue

                type = v.get('type', 'sql')
                if type == 'sql':
                    query = v['sql']
                    if debug: self.log.info(query)
                    df = self.spark.sql(query)
                    if v.get('dropDuplicates', None):
                        self.log.info("Drop duplicates.")
                        df.dropDuplicates()
                    if v.get('cache', None):
                        self.log.info("Cache transform.")
                        df.cache()
                    # Pu.debug_log_with_cnt(msg=f"# {k} df:", _df=df, debug=debug, _log=self.log)
                    if debug: print(f"{k}")
                    if debug: df.printSchema()
                    if debug: print(f"{k}")
                    if debug: df.show(5)
                    df.createOrReplaceTempView(k)
                elif type == 'user_function':
                    function_name = v['function_name']
                    func = getattr(self, function_name, None)
                    if func:
                        df = func()
                        if v.get('dropDuplicates', None):
                            self.log.info("Drop duplicates.")
                            df.dropDuplicates()
                        if v.get('cache', None):
                            self.log.info("Cache transform.")
                            df.cache()
                        if debug and df: df.show()
                        if df: df.createOrReplaceTempView(k)

        return None

    @exception_handler
    def run_etl(self):
        """
        Run etl job
        Overload this function if need be, instead of main
        """
        self.init_flexi_configurations()
        # # SPARK SETTINGS
        if 'repartition' in self.config[Constant_Config.STEP_CONFIG]:
            repartition = self.config[Constant_Config.STEP_CONFIG]['repartition']  # 10
            self.spark.conf.set("spark.sql.shuffle.partitions", repartition)
            # if debug: self.log.info(f"repartition: {repartition}")
            self.log.info(f"repartition: {repartition}")

        self.spark.conf.set("spark.sql.crossJoin.enabled", True)
        _current_job_id = self.config['job_id']
        self.extract_data()
        self.transform_data()
        # if debug: self.log.log_into_postgresql_job_log(f"Starting to load data")
        self.log.log_into_postgresql_job_log(f"Starting to load data")
        self.load_data()
        self.log.info(f"End, loading data, completed.")
        # if debug: self.log.log_into_postgresql_job_log(f"End, loading data, completed.")
        self.log.log_into_postgresql_job_log(f"End, loading data, completed.")
        return

    @exception_handler
    def load_data(self):

        self.log.info("Load...")
        step_config = self.config[Constant_Config.STEP_CONFIG]
        if step_config.get('Load', None) is None:
            return
        for df_name, loads in step_config['Load'].items():
            if df_name == 'close_open_job_id' or df_name == 'close_job_id':
                df = None
            else:
                df = self.spark.table(df_name)
                self.log.info(f"key {df_name}")
                print(loads)

            for load_name, load_settings in loads.items():
                print(load_name)
                if "type" not in load_settings:
                    self.log.warn(f"load type has not been specified for table: {df_name}, load: {load_name}")
                    raise Exception(f"load type has not been specified for table: {df_name}, load: {load_name}")
                type = load_settings["type"]
                if type == "parquet":
                    self.save_to_parquet(df, load_settings, load_name)
                elif type == "postgres":
                    self.save_to_postgres(df, load_settings, load_name)
                elif type == "csv":
                    self.save_to_csv(df, load_settings, load_name)
                elif type == "close_open_job_id":
                    self.close_open_job_id(df, load_settings, load_name)
                elif type == "close_job_id":
                    self.close_job_id(df, load_settings, load_name)
                elif type == "print":
                    print(df_name)
                    print_limit = load_settings.get('limit', 10)
                    print_show_count = load_settings.get('count', False)
                    df.show(print_limit)
                    if print_show_count:
                        print(f"count for {df_name} is {df.count()}")
        return None

    @exception_handler
    def add_custom_config_fields(self, config, args):
        """
        Overloading to add custom config fields
        :params config: config object created in get_base_argparse_configs
        :params args: args given to argparse, used in creating custom config pieces
        :return config: new config object with desired custom fields
        """
        print(args)
        config[Constant_Config.STEP_CONFIG][Constant_Config.PROJECT_ROOT_PATH] = args[Constant_Config.PROJECT_ROOT_PATH]
        config[Constant_Config.STEP_CONFIG]["metadata"] = {}

        return config

    @staticmethod
    def parquet_repartition_cols(partitions):
        """
       :params partitions: array , example [cad_job_id, npi_par]
       :return repartition_cols: array , example [F.col('nipi_par'), F.col('cad_job_id')]
       """
        if partitions is None:
            return None
        if isinstance(partitions, int):
            return partitions

        return list(map(lambda x: F.col(x), partitions))

    @exception_handler
    def extract_from_parquet(self, df_name, setting):
        location = setting['location']
        skip = setting.get('skip', False)
        if skip:
            print(f"Skipping this : {df_name}")
            self.log.info(f"Skipping this : {df_name}")
            return
        self.log.info(f"Extracting from Parquet: location: {location}")
        df = self.spark.read.parquet(location)
        if setting.get('cache', False):
            self.log.info(f"Cache: {df_name}")
            df.cache()
        df.createOrReplaceTempView(df_name)

    def extract_from_csv(self, df_name, setting):
        location = setting['location']

        if "delimiter" in setting:
            delimiter = setting["delimiter"]
        else:
            delimiter = ","

        if "header" in setting:
            header = setting["header"]
        else:
            header = True

        self.log.info(f"Extracting from CSV: location: {location}")
        df = self.spark.read.options(sep=delimiter, header=header, ignoreLeadingWhiteSpace=True,
                                     ignoreTrailingWhiteSpace=True).csv(location)

        if setting.get('cache', False):
            self.log.info(f"Cache: {df_name}")
            df.cache()
        df.createOrReplaceTempView(df_name)

    @exception_handler
    def extract_from_postgres(self, df_name, setting):
        table_name = setting['table_name']

        if "conn_config_name" not in setting:
            self.log.error(f"conn_config_name not set in Postgres load {load_name}")
            raise Exception(f"conn_config_name not set in Postgres load {load_name}")
        # Example: cadmium_postgres_db,
        conn_config_name = setting["conn_config_name"]
        if conn_config_name not in self.config[Constant_Config.PROJECT_CONFIG]:
            self.log.error(f"{conn_config_name} not found in postgres project_config for load {load_name}")
            raise Exception(f"{conn_config_name} not found in postgres project_config for load {load_name}")

        pg_config = self.config[Constant_Config.PROJECT_CONFIG][conn_config_name]
        hostname = pg_config['hostname']
        user = pg_config['user']
        pwd = pg_config['password']
        port = pg_config['port']
        database_name = pg_config['database_name']
        schema = pg_config['schema']

        dbtable_name = f"{schema}.{table_name}"

        df = self.spark.read.format("jdbc") \
            .option("url", f"jdbc:postgresql://{hostname}:{port}/{database_name}") \
            .option("dbtable", dbtable_name) \
            .option("user", user) \
            .option("password", pwd) \
            .option("driver", "org.postgresql.Driver") \
            .load()

        if setting.get('cache', False):
            self.log.info(f"Cache: {df_name}")
            df.cache()
        df.createOrReplaceTempView(df_name)

        return

    @exception_handler
    def save_to_parquet(self, df, setting, load_name):
        location = setting['location']
        partitions = setting.get('partitions', None)
        mode = setting.get('mode', 'append')
        self.log.info(f"Saving to Parquet: location: {location}, partitions: {partitions}, mode: {mode}")

        # with repartition
        Su.save_parquet(repartition=self.parquet_repartition_cols(partitions),
                        partition_by=partitions,
                        path=location, output_data=df, _log=self.log, mode=mode)
        return

    @exception_handler
    def save_to_csv(self, df, setting, load_name):
        location = setting['location']
        partitions = setting.get('partitions', None)
        mode = setting.get('mode', 'append')
        self.log.info(f"Saving to CSV: location: {location}, partitions: {partitions}, mode: {mode}")

        # with repartition
        Su.save_csv(repartition=self.parquet_repartition_cols(partitions),
                    path=location, output_data=df, _log=self.log, mode=mode)
        return

    @exception_handler
    def close_open_job_id(self, df, setting, load_name):
        conn_config_name = setting["conn_config_name"]
        if conn_config_name not in self.config[Constant_Config.PROJECT_CONFIG]:
            self.log.error(f"{conn_config_name} not found in postgres project_config for load {load_name}")
            raise Exception(f"{conn_config_name} not found in postgres project_config for load {load_name}")

        postgres_config = self.config[Constant_Config.PROJECT_CONFIG].get(conn_config_name)
        self.log.info(f"postgres_config {postgres_config}")

        client_name = self.config[Constant_Config.CLIENT]
        workflow_name = self.config.get(Constant_Config.WORKFLOW,"flexisync")
        stage_name = self.config.get(Constant_Config.ENV,"test")
        user_name = self.config.get(Constant_Config.USER,"user")
        table_name = postgres_config["table_name"]
        print(client_name,workflow_name,stage_name,user_name,table_name)
        try:
            postgres = CadmiumPostGres(
                postgres_config["hostname"],
                postgres_config["database_name"],
                postgres_config["user"],
                postgres_config["password"],
                postgres_config["port"],
                True,
            )
            results = postgres.query_table_fetchall(f"SELECT * FROM {table_name} WHERE status = 'OPEN' AND client_name = '{client_name}'")
            self.log.info(f"Results == {results} and {table_name} and {client_name}")
            if results:
                for closed_id in results:
                    self.log.info(f"Close id {closed_id[0]} and {client_name}")
                    postgres.execute_table(f"UPDATE {table_name} SET status = 'CLOSED' WHERE ( id = {closed_id[0]} AND client_name = '{client_name}') ") # CLOSE all OPEN of that client

            max_id_result = postgres.query_table(f"SELECT id FROM {table_name} WHERE client_name = '{client_name}' ORDER BY id DESC LIMIT 1")
            if max_id_result:
                id = max_id_result[0]
            else:
                id = 0 # new table

            postgres.insert_into_table(
                table_name=table_name,
                columns_tuples="(id, client_name, workflow_name, stage_name, user_name, status)",
                placeholders_tuple="(%s, %s, %s, %s, %s, %s)",
                values_tuple=(
                    id + 1,
                    client_name,
                    workflow_name,
                    stage_name,
                    user_name,
                    'OPEN'),
            )

            postgres.close()
            self.log.info(f"Completed close and open job id, new job id: {id+1}")
            print(f"Completed close and open job id, new job id: {id+1}")

        except Exception:
            self.log.error(
                "{} Stack Trace: {}".format(
                    "Logging into Postgres Failed.", traceback.format_exc()
                )
            )
        return

    @exception_handler
    def close_job_id(self, df, setting, load_name):
        conn_config_name = setting["conn_config_name"]
        if conn_config_name not in self.config[Constant_Config.PROJECT_CONFIG]:
            self.log.error(f"{conn_config_name} not found in postgres project_config for load {load_name}")
            raise Exception(f"{conn_config_name} not found in postgres project_config for load {load_name}")

        postgres_config = self.config[Constant_Config.PROJECT_CONFIG].get(conn_config_name)
        self.log.info(f"postgres_config {postgres_config}")

        client_name = self.config[Constant_Config.CLIENT]
        workflow_name = self.config.get(Constant_Config.WORKFLOW,"flexisync")
        stage_name = self.config.get(Constant_Config.ENV,"test")
        user_name = self.config.get(Constant_Config.USER,"user")
        table_name = postgres_config["table_name"]
        print(client_name,workflow_name,stage_name,user_name,table_name)
        try:
            postgres = CadmiumPostGres(
                postgres_config["hostname"],
                postgres_config["database_name"],
                postgres_config["user"],
                postgres_config["password"],
                postgres_config["port"],
                True,
            )
            result = postgres.query_table(f"SELECT * FROM {table_name} WHERE status = 'OPEN' AND client_name = '{client_name}' ORDER BY created_at DESC LIMIT 1")
            if result:
                closed_id = result[0]
                postgres.execute_table(f"UPDATE {table_name} SET status = 'CLOSED' WHERE id = {closed_id} ")
            else:
                self.log.info(f"No OPEN for this client : {client_name}")

            postgres.close()
            self.log.info(f"Completed close for {client_name}")

        except Exception:
            self.log.error(
                "{} Stack Trace: {}".format(
                    "Logging into Postgres Failed.", traceback.format_exc()
                )
            )
        return

    @exception_handler
    def save_to_postgres(self, df, setting, load_name):
        # we only support append and overwrite now (overwrite = truncate + append)
        mode = setting.get('mode', 'append')
        table_name = setting['table_name']

        if "conn_config_name" not in setting:
            self.log.error(f"conn_config_name not set in Postgres load {load_name}")
            raise Exception(f"conn_config_name not set in Postgres load {load_name}")
        conn_config_name = setting["conn_config_name"]
        if conn_config_name not in self.config[Constant_Config.PROJECT_CONFIG]:
            self.log.error(f"{conn_config_name} not found in postgres project_config for load {load_name}")
            raise Exception(f"{conn_config_name} not found in postgres project_config for load {load_name}")

        pg_config = self.config[Constant_Config.PROJECT_CONFIG][conn_config_name]
        hostname = pg_config['hostname']
        user = pg_config['user']
        pwd = pg_config['password']
        port = pg_config['port']
        database_name = pg_config['database_name']
        schema = pg_config['schema']

        dbtable_name = f"{schema}.{table_name}"

        if mode == 'overwrite':
            conn = None
            # try:
            print(dbtable_name)
            conn_string = f"dbname={database_name} user={user} host={hostname} password={pwd}"
            # connect to the PostgreSQL database
            conn = psycopg2.connect(conn_string)
            # create a new cursor
            cur = conn.cursor()
            # execute the sql  statement
            cur.execute(f"TRUNCATE TABLE  {dbtable_name}; ")
            # Commit the changes to the database
            conn.commit()
            # Close communication with the PostgreSQL database
            cur.close()
            if conn is not None:
                conn.close()

        df.write.format("jdbc") \
            .option("url", f"jdbc:postgresql://{hostname}:{port}/{database_name}") \
            .option("dbtable", dbtable_name) \
            .option("user", user) \
            .option("password", pwd) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()

        return


if __name__ == "__main__":
    flexiEtl = FlexiEtl()
    flexiEtl.main()
