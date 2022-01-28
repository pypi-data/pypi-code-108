import pandas as pd
import numpy as np
import datetime
import io
import os
import glob
import sys
from googleads import adwords
from datetime import datetime, timedelta

# Auth and dictionary of account names
def google_ads_campaign_report(file_yaml_url, account_dictionary):

  # Define the report date range: last 28 days including today
  start=datetime.today().date().isoformat().replace("-", "")
  end=datetime.now() + timedelta(days= - 40)
  end= end.date().isoformat().replace("-","")

  def run_Hour0fDay_kip_report(account_name, acc_id, start_date, end_date):
  
    # Define output as a string
    output= io.StringIO()
    
    adwords_client = adwords.AdWordsClient.LoadFromStorage('googleads.yaml')
    adwords_client.SetClientCustomerId(acc_id)    

    report_downloader = adwords_client.GetReportDownloader(version='v201809')
    report_query = (adwords.ReportQueryBuilder()
                      .Select(
                          'Month'
                          ,'Date'
                        #   ,'AccountId'
                          ,'CampaignId'
                          ,'ExternalCustomerId'
                          ,'CampaignName'
                          ,'CampaignStatus'
                        #   ,'CampaignType'
                          ,'Amount'
                          ,'AccountCurrencyCode'
                          ,'Clicks'
                          ,'Impressions'
                          ,'Ctr'
                          ,'AverageCpc'
                          ,'Cost'
                          ,'Conversions'
                          ,'ViewThroughConversions'
                          ,'CostPerConversion'
                          ,'ConversionRate'
                          ,'AverageCpm'
                          )
                      .From('CAMPAIGN_PERFORMANCE_REPORT')
                    #   .Where('CampaignStatus').In('ENABLED')
                      .During(end_date+ ','+start_date) 
                      .Build())

    report_downloader.DownloadReportWithAwql(report_query, 'CSV', output, skip_report_header=True,
              skip_column_header=False, skip_report_summary=True,
              include_zero_impressions=False)

    output.seek(0)
    
    types= { 'CampaignId':pd.np.int64, 'Clicks': pd.np.float64, 'Impressions': pd.np.float64,
            'Cost': pd.np.float64,'Conversions': pd.np.float64,'ConversionValue': pd.np.float64  }

    df = pd.read_csv(output,low_memory=False, dtype= types, na_values=[' --'])
    # delete the first and last column
    df['Brand']=account_name
    # micro amount 1000000
    df['Cost']=df.Cost/1000000
    
    print(df.head())
    return df

  list_df = []

  for account_name, account_id in account_dictionary.items():
      # df=run_campaign_performance_report(k, v,start, end)
      df=run_Hour0fDay_kip_report(account_name, account_id,start, end)
      list_df.append(df)
  
  final_df = pd.concat(list_df)
  
  return final_df

# Auth and dictionary of account names
def google_ads_keyword_performance(file_yaml_url, account_dictionary):

  edate=datetime.today().date().isoformat().replace("-", "")
  sdate=datetime.now() + timedelta(days= - 3)
  sdate= sdate.date().isoformat().replace("-", "")

  # def dates_bwn_twodates(start_date, end_date):
  #     for n in range(int ((end_date - start_date).days)):
  #         dd = start_date + timedelta(n)
  #         str = dd.isoformat().replace("-", "")
  #         yield str
  # rd = list(dates_bwn_twodates(sdate, edate))

  def run_keyword_performance(account_name, acc_id, start_date, end_date):

    output= io.StringIO()

    adwords_client = adwords.AdWordsClient.LoadFromStorage('googleads.yaml')
    adwords_client.SetClientCustomerId(acc_id)    

    report_downloader = adwords_client.GetReportDownloader(version='v201809')

    # Create report query.
    report_query = (adwords.ReportQueryBuilder()
                    .Select( 'AccountCurrencyCode'
                            ,'AccountDescriptiveName'
                            ,'AccountTimeZone'
                            ,'AdGroupId'
                            ,'AdGroupName'
                            ,'AdGroupStatus'
                            ,'ApprovalStatus'
                            ,'BaseAdGroupId'
                            ,'BaseCampaignId'
                            ,'BiddingStrategyId'
                            ,'BiddingStrategyName'
                            ,'BiddingStrategySource'
                            ,'BiddingStrategyType'
                            ,'CampaignId'
                            ,'CampaignName'
                            ,'CampaignStatus'
                            ,'Clicks'
                            ,'ConversionRate'
                            ,'Conversions'
                            ,'Cost'
                            ,'CpcBid'
                            ,'CpcBidSource'
                            ,'CpmBid'
                            ,'CreativeQualityScore'
                            ,'Criteria'
                            ,'Ctr'
                            ,'CustomerDescriptiveName'
                            ,'Date'
                            ,'DayOfWeek'
                            ,'Device'
                            ,'EngagementRate'
                            ,'Engagements'
                            ,'ExternalCustomerId'
                            ,'FinalAppUrls'
                            ,'FinalMobileUrls'
                            ,'FinalUrls'
                            ,'FinalUrlSuffix'
                            ,'FirstPageCpc'
                            ,'FirstPositionCpc'
                            ,'GmailForwards'
                            ,'GmailSaves'
                            ,'GmailSecondaryClicks'
                            ,'Id'
                            ,'Impressions'
                            ,'InteractionRate'
                            ,'Interactions'
                            ,'IsNegative'
                            ,'KeywordMatchType'
                            ,'LabelIds'
                            ,'Labels'
                            ,'Month'
                            ,'MonthOfYear'
                            ,'Quarter'
                            ,'Slot'
                            ,'Status'
                            ,'SystemServingStatus'
                            ,'ViewThroughConversions'
                            ,'Week'
                            ,'Year'
                            )
                    .From('KEYWORDS_PERFORMANCE_REPORT')
                  #   .Where('Status').In('ENABLED', 'PAUSED')
                    .During(f'{sdate},{edate}')
                    .Build())

    # You can provide a file object to write the output to. For this
    report_downloader.DownloadReportWithAwql(
        report_query, 'CSV', ouput, skip_report_header=True,
        skip_column_header=False, skip_report_summary=True,
        include_zero_impressions=False)
      
    output.seek(0)

    ##      types= { 'CampaignId':pd.np.int64, 'Clicks': pd.np.float64, 'Impressions': pd.np.float64,
    ##        'Cost': pd.np.float64,'Conversions': pd.np.float64,'ConversionValue': pd.np.float64  }

    df = pd.read_csv(output,low_memory=False, na_values=[' --'])
    # delete the first and last column
    df['Brand']=account_name
    # micro amount 1000000
    df['Cost']=df.Cost/1000000
    
    print(df.head())
    return df

  # Prepare response
  list_df = []

  for account_name, account_id in account_dictionary.items():
      # df=run_campaign_performance_report(k, v,start, end)
      df=run_keyword_performance(account_name, account_id,start, end)
      list_df.append(df)
  
  final_df = pd.concat(list_df)

  return final_df


