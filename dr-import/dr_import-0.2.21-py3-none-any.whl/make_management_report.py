""" Script that creates the NEMM management report using a directory of Tator reports per trip
"""

import argparse
import glob
import os
import yaml

import pandas as pd
import progressbar

def main(directory: str) -> None:
    """ Creates the management report csv file using the provided directory of Tator spreadsheets

    :param directory: Directory containing the Tator trip spreadsheets. Will also contain the
                      final management report csv file.
    """

    print("\n")
    print("-------------------------------------------------------")
    print("Make Management Report: STARTED")
    print("-------------------------------------------------------")
    print("\n")

    # Loop over the spreadsheets in the directory and create a list of dataframes from them
    raw_report_files = glob.glob(os.path.join(directory,"*.xlsx"))
    report_spreadsheet_dfs = []

    print(f"Reading {len(raw_report_files)} reports in {directory}")
    bar = progressbar.ProgressBar()
    for file in bar(raw_report_files):
        report_spreadsheet_dfs.append(pd.read_excel(file, sheet_name=None, engine='openpyxl'))

    # Now, loop over each of the report dataframes and combine them into the management report
    report=pd.DataFrame()
    df_list=[]
    management_report=pd.DataFrame()

    print(f"Processing data from reports")
    bar = progressbar.ProgressBar()
    for report_info in bar(report_spreadsheet_dfs):

        summary_fsb = report_info['summary_fsb']
        summary_tator = report_info['summary_tator']
        reviewer_tator = report_info['reviewer_tator']
        haul_fsb = report_info['haul_fsb']
        haul_tator = report_info['haul_tator']
        other_events_fsb = report_info['other_events_fsb']
        other_events_tator = report_info['other_events_tator']
        discards_fsb = report_info['discards_fsb']
        discards_tator = report_info['discards_tator']
        fsb_response = report_info['fsb_response']

        report=discards_fsb[['species_common_itis','count','discard_datetime','disposition','reviewer_id','haul_id','comments']]
        report=pd.merge(report,discards_tator['haul_offset'],left_index=True, right_index=True)
        cols=['set_start_datetime','set_end_datetime','haulback_start_datetime','haulback_end_datetime', 'amount_reviewed','observed','gear_category','catch_sorting_end_datetime','haul_id']
        report=pd.merge(report,haul_fsb[cols],on='haul_id')

        other_events_fsb.rename(columns={'comments':'notes'},inplace=True)
        cols=['event_category', 'event_code', 'event_duration', 'haul_id','event_datetime', 'notes','reviewer_id']
        report=report.append(other_events_fsb[cols])

        report['vessel_name']=summary_fsb.iloc[0]['vessel_name']
        report['evtr_num']=summary_fsb.iloc[0]['evtr_num']
        report['date_sail']=summary_fsb.iloc[0]['date_sail']
        report['date_land']=summary_fsb.iloc[0]['date_land']

        try:
            report['nemm_sail_time']=summary_tator.iloc[0]['nemm_sail_time']
            report['nemm_land_time']=summary_tator.iloc[0]['nemm_land_time']
            report['full_review_time']=reviewer_tator.full_review_time.sum()

            report.nemm_land_time=pd.to_datetime(report.nemm_land_time)
            report.nemm_sail_time=pd.to_datetime(report.nemm_sail_time)

            trip_duration=report.iloc[0].nemm_land_time - report.iloc[0].nemm_sail_time
            report['ratio']=str(round(report.iloc[0].full_review_time/(trip_duration.components.days*24*60+trip_duration.components.hours*60+trip_duration.components.minutes)*100,2))+' %'

        except:
            report['nemm_sail_time'] = "N/A"
            report['nemm_land_time'] = "N/A"
            report['full_review_time'] = "N/A"
            report['ratio'] = "N/A"


        report=report[['vessel_name', 'evtr_num', 'date_sail', 'date_land','nemm_sail_time','nemm_land_time','full_review_time','ratio','haul_id','set_start_datetime', 'set_end_datetime', 'haulback_start_datetime',
          'haulback_end_datetime','event_category', 'event_code','event_duration', 'event_datetime',
        'notes','amount_reviewed', 'observed', 'gear_category',
          'catch_sorting_end_datetime','species_common_itis', 'count', 'discard_datetime', 'disposition',
          'reviewer_id','haul_offset','comments']]
        df_list.append(report)

    for i in range(len(df_list)):
        management_report=management_report.append(df_list[i])

    filename = os.path.join(directory, 'Management_Report.csv')
    print(f"Creating management report: {filename}")
    management_report.to_csv(filename, index=False)

    print("\n")
    print("-------------------------------------------------------")
    print("Make Management Report: FINISHED")
    print("-------------------------------------------------------")
    print("\n")


def parse_args() -> argparse.Namespace:
    """ Script argument parser

    :returns: Processed script arguments

    """

    parser=argparse.ArgumentParser(description='Create the NEMM Management Report using MREM Tator trip reports')
    parser.add_argument("directory", help="Location of reports to process")
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's entry point
    """
    args = parse_args()
    main(directory=args.directory)

if __name__ == "__main__":
    script_main()