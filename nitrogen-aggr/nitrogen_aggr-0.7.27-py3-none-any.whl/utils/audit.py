import pyspark.sql.functions as F
from pyspark.sql.utils import AnalysisException
from pyspark.sql.functions import expr

class Audit():

    def __init__(self,
                 spark_session,
                 master_location,
                 project_config,
                 _log):

        self.log = _log
        self.spark = spark_session
        self.master_location = master_location
        self.project_config = project_config

    def unpivot(self, df):

        unpivotExpr = """stack(22,   
            'avg hcc captured', avg_hcc_captured,  
            'avg hcc opportunity', avg_hcc_opp,  
            'avg raf score', avg_raf,  
            'avgdemo', avg_raf_demo,  
            'avg projected raf score', avg_raf_projected,  
            'eligible members', cast(eligible_count as double),  
            'female population ratios', cast(female_percent as double),  
            'members w/ zero hcc score', cast(hcc_zero_count as double),  
            'male population ratios', cast(male_percent as double),  
            'members w/ no provider visits', cast(no_dos_count as double),  
            'no_wellness_visit_count', cast(no_wellness_visit_count as double),  
            'one_dos_and_hcc_sus_count', cast(one_dos_and_hcc_sus_count as double),  
            'gtr_than_three_sus_count', cast(gtr_than_three_sus_count as double),  
            'members w/ no pcp visits', cast(no_pcp_dos_count as double),  
            'members w/ zero demo score', cast(no_demo_count as double),  
            'recapture rates', cast(recapture_rate as double),  
            'RAFx call Errors', cast(rafx_call_errors as double),  
            'total_captured_dxs_sent_to_lambda_rafx', cast(total_captured_dxs_sent_to_lambda_rafx as double),  
            'total_suspect_dxs_sent_to_lambda_rafx', cast(total_suspect_dxs_sent_to_lambda_rafx as double),  
            'total_input_dxs', cast(total_input_dxs as double),  
            'total_hccs', cast(total_hccs as double),  
            'Number of members without first name', cast(first_name_lesseq_than_1_count as double)  
            )  as ( measure, value) 
            """

        df.select(
            "record_timestamp", "job_id", "year",
            "year_name", expr(unpivotExpr)
        ).where("value is not null ").createOrReplaceTempView("unpivot_df")

        return self.spark.sql("""
                select *,
                row_number() over(partition by measure, year     order by  record_timestamp desc) as r ,
                case
                when measure = 'avg hcc captured' then '4kpi'
                when measure = 'avg hcc opportunity' then 'dashboard10'
                when measure = 'avg raf score' then '1kpi'
                when measure = 'avgdemo' then 'dashboard06'
                when measure = 'avg projected raf score' then 'dashboard08'
                when measure = 'eligible members' then '3kpi'
                when measure = 'female population ratios' then 'dashboard12'
                when measure = 'members w/ zero hcc score' then 'dashboard02'
                when measure = 'male population ratios' then 'dashboard11'
                when measure = 'members w/ no provider visits' then 'dashboard04'
                when measure = 'recapture rates' then '2kpi'
                when measure = 'RAFx call Errors' then '5kpi'
                when measure = 'members w/ no pcp visits' then 'dashboard03'
                when measure = 'no_demo_count' then 'dashboard05'
                when measure = 'Number of members without first name' then '6kpi'
                else 'OTHER_GROUP' end as groupy
                from unpivot_df
                where year between 2019 and  year(current_date())
            """)


