''' Salesforce API contacts to dataframe '''

import pandas as pd
import requests
import json
import time
import datetime
import os
import sys
import pytz
import numpy as np

from simple_salesforce import Salesforce

# import credentials from config file
import config

# import custom functions
import functions

# set timezone
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

# set pandas display options
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# timestamp
start_time = time.time()

# instantiate Salesforce connection
sf = Salesforce(username=config.username, password=config.password, security_token=config.security_token)

# get all contacts
contacts = sf.query_all("SELECT Id, Name, Salutation, FirstName, LastName, Title, Company, Phone, MobilePhone, Email, MailingStreet, MailingCity, MailingState, MailingPostalCode, MailingCountry, OtherStreet, OtherCity, OtherState, OtherPostalCode, OtherCountry, Birthdate, Description, LeadSource, Status, Lead_Source_Detail__c, ConvertedAccountId, ConvertedAccountName, ConvertedContactId, ConvertedContactName, ConvertedDate, ConvertedOpportunityId, ConvertedOpportunityName, Do_Not_Call, DoNotCallReason, EmailBouncedDate, EmailBouncedReason, Fax, First_Responded__c, HasOptedOutOfEmail, HasOptedOutOfFax, IsEmailBounced, Jigsaw, JigsawContactId, LastCURequestDate, LastCUUpdateDate, LastModifiedById, LastModifiedDate, LastActivityDate, LastViewedDate, Lead_Source_Detail__c, Lead_Source__c, MailingLatitude, MailingLongitude, MasterRecordId, MobilePhone_verified__c, NumberOfEmployees, NumberofLocations__c, OtherLatitude, OtherLongitude, OwnerId, Phone_verified__c, Salutation_c__c, SystemModstamp, Title_c__c, Type, Website, CreatedDate, CreatedById, LastModifiedDate, LastModifiedById, SystemModstamp, IsDeleted FROM Contact")

# convert to dataframe
contacts_df = pd.DataFrame(contacts['records']).drop(columns='attributes')

# add additional columns
contacts_df['CreatedDate'] = pd.to_datetime(contacts_df['CreatedDate'])
contacts_df['CreatedDate'] = contacts_df['CreatedDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['CreatedDate'] = contacts_df['CreatedDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['LastModifiedDate'] = pd.to_datetime(contacts_df['LastModifiedDate'])
contacts_df['LastModifiedDate'] = contacts_df['LastModifiedDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['LastModifiedDate'] = contacts_df['LastModifiedDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['LastActivityDate'] = pd.to_datetime(contacts_df['LastActivityDate'])
contacts_df['LastActivityDate'] = contacts_df['LastActivityDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['LastActivityDate'] = contacts_df['LastActivityDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['LastCURequestDate'] = pd.to_datetime(contacts_df['LastCURequestDate'])
contacts_df['LastCURequestDate'] = contacts_df['LastCURequestDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['LastCURequestDate'] = contacts_df['LastCURequestDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['LastCUUpdateDate'] = pd.to_datetime(contacts_df['LastCUUpdateDate'])
contacts_df['LastCUUpdateDate'] = contacts_df['LastCUUpdateDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['LastCUUpdateDate'] = contacts_df['LastCUUpdateDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['Birthdate'] = pd.to_datetime(contacts_df['Birthdate'])
contacts_df['Birthdate'] = contacts_df['Birthdate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['Birthdate'] = contacts_df['Birthdate'].dt.strftime('%Y-%m-%d')
contacts_df['EmailBouncedDate'] = pd.to_datetime(contacts_df['EmailBouncedDate'])
contacts_df['EmailBouncedDate'] = contacts_df['EmailBouncedDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['EmailBouncedDate'] = contacts_df['EmailBouncedDate'].dt.strftime('%Y-%m-%d')
contacts_df['LastModifiedDate'] = pd.to_datetime(contacts_df['LastModifiedDate'])
contacts_df['LastModifiedDate'] = contacts_df['LastModifiedDate'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
contacts_df['LastModifiedDate'] = contacts_df['LastModifiedDate'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
contacts_df['LastModifiedById'] = contacts_df['LastModifiedById'].str.lstrip('00530000000')
contacts_df['OwnerId'] = contacts_df['OwnerId'].str.lstrip('00530000000')
contacts_df['CreatedById'] = contacts_df['CreatedById'].str.lstrip('00530000000')
contacts_df['MasterRecordId'] = contacts_df['MasterRecordId'].str.lstrip('00Q')
contacts_df['ConvertedAccountId'] = contacts_df['ConvertedAccountId'].str.lstrip('00Q')
contacts_df['ConvertedContactId'] = contacts_df['ConvertedContactId'].str.lstrip('00Q')
contacts_df['ConvertedOpportunityId'] = contacts_df['ConvertedOpportunityId'].str.lstrip('00Q')
contacts_df['LastModifiedById'] = contacts_df['LastModifiedById'].str.lstrip('00Q')