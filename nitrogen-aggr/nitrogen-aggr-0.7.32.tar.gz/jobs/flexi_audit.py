from constants.constants_configs import Config as Constant_Config
from dependencies.exception import exception_handler
from jobs.flexi_etl import FlexiEtl
from utils.audit import Audit


class FlexiAudit(FlexiEtl):
    @exception_handler
    def unpivot_audit(self):
        # find  epi_member_id for claims
        audit = Audit(
            self.spark,
            self.config[Constant_Config.LOCATION_MASTER],
            self.get_config_for_step('audit_threshold'),
            self.log
        )

        df_unpivot_audit = audit.unpivot(self.spark.table("aggr_nitrogen_yearly_dashboard"))

        return df_unpivot_audit

    @staticmethod
    def print_df(df, load_settings, load_name):
        print_limit = load_settings.get('limit', 10)
        df.show(print_limit)
        if load_settings.get('count', False):
            print(f"count is {df.count()}")

    def load_data(self):
        self.log.info("Load...")
        step_config = self.config[Constant_Config.STEP_CONFIG]
        if step_config.get('Load', None) is None:
            return

        loads_containing_bad_measurements = []
        for df_name, df_settings in step_config['Load'].items():
            df: DataFrame = self.spark.table(df_name)
            self.log.info(f"key {df_name}")
            print(df_settings)

            if 'verify' in df_settings and df_settings['verify']:
                # Cache results as we may be accessing them multiple times to check whether or not the results are good
                df.cache()
                if df.count() > 0:
                    loads_containing_bad_measurements.append(df_name)

            for load_name, load_settings in df_settings['loads'].items():
                print(load_name)
                if "type" not in load_settings:
                    self.log.warn(f"load type has not been specified for table: {df_name}, load: {load_name}")
                    raise Exception(f"load type has not been specified for table: {df_name}, load: {load_name}")

                load_type = load_settings["type"]
                if load_type == "parquet":
                    self.save_to_parquet(df, load_settings, load_name)
                elif load_type == "postgres":
                    self.save_to_postgres(df, load_settings, load_name)
                elif load_type == "csv":
                    self.save_to_csv(df, load_settings, load_name)
                elif load_type == "print":
                    self.print_df(df, load_settings, load_name)

            df.unpersist()

        if len(loads_containing_bad_measurements) > 0:
            raise Exception(
                f"Found measurements outside expected thresholds. See the following loads: {loads_containing_bad_measurements}.")

        return None


if __name__ == "__main__":
    run_flexi_audit = FlexiAudit()
    run_flexi_audit.main()
