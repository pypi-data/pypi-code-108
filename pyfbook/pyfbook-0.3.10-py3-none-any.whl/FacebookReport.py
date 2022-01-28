import os
from shutil import copyfile

import yaml
from dbstream import DBStream

from pyfbook.SystemUser import SystemUser
from pyfbook.core.ad_accounts.ad_accounts import process_ad_accounts, get_ad_accounts
from pyfbook.core.marketing.extract.reports.launch import launch
from pyfbook.core.marketing.extract.reports.save import save_reports
from pyfbook.core.marketing.transform_and_load.fetch import check_and_fetch_reports, time_increment_mapping


def launch_reports(facebook, start, end):
    for report in facebook.config["reports"]:
        report_name = report['name']
        for time_increment in report["time_increments"]:
            print('Launch report %s %s' % (report_name, time_increment))
            async_reports = launch(
                facebook=facebook,
                report=report,
                time_increment=time_increment_mapping[time_increment],
                start=start,
                end=end
            )
            save_reports(
                data=async_reports,
                facebook=facebook,
                time_increment=time_increment_mapping[time_increment],
                report_name=report_name
            )


class Facebook:
    def __init__(self,
                 config_path=None,
                 dbstream: DBStream = None,
                 transactional_dbstream: DBStream = None,
                 launch_jobs=True,
                 schema_name=None):
        self.config_path = config_path
        if not config_path:
            print('You need a config file')
            create_config_field = input('Do you want to generate a default config field? [Y/n]')
            if create_config_field == 'Y':
                f = open("config.yaml", "w")
                sample_config_path = os.path.dirname(os.path.realpath(__file__)) + '/core/config/sample_config.yaml'
                copyfile(sample_config_path, 'config.yaml')
                f.close()
                print('Config file is created, update it and add its path to this Facebook object')
                exit()
            self.config_path = None
        self.config = yaml.load(open(self.config_path), Loader=yaml.FullLoader)
        self.dbstream = dbstream
        self.transactional_dbstream = transactional_dbstream
        if self.transactional_dbstream is None:
            self.transactional_dbstream = dbstream
        self.launch_jobs = launch_jobs
        self.schema_name = schema_name

    def get(self, report_name=None, time_increment=None, start=None, end=None, list_account_ids=None):
        if report_name:
            report = list(filter(lambda c: c["name"] == report_name, self.config["reports"]))
            if not report:
                print("No report with this name")
                exit()
            self.config["reports"] = report
        if time_increment:
            for i in range(len(self.config["reports"])):
                self.config["reports"][i]["time_increments"] = [time_increment]
        if list_account_ids:
            for i in range(len(self.config["reports"])):
                self.config["reports"][i]["ad_accounts"] = list_account_ids
        if self.launch_jobs:
            launch_reports(self, start, end)
        bool_ = True
        while bool_:
            bool_ = check_and_fetch_reports(self)

    def get_all_ad_accounts(self, list_account_ids=None):
        table_name = "%s.ad_accounts" % (self.schema_name if self.schema_name else self.config.get("schema_name"))
        system_users = SystemUser.all(facebook=self)
        ad_accounts = []
        for system_user in system_users:
            ad_accounts = ad_accounts + get_ad_accounts(system_user)
        process_ad_accounts(ad_accounts, table_name, self, list_account_ids=list_account_ids)

    def create_app_system_user(self, app_id_name, app_secret_name, access_token_name):
        SystemUser.create(self, app_id_name, app_secret_name, access_token_name)
        print("App system user's configuration name created in database")
