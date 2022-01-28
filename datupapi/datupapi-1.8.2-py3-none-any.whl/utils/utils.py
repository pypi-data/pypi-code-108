import boto3
import datetime
import os
import pytz
import time

from datupapi.configure.config import Config

class Utils(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def set_timestamp(self, timezone='America/Chicago'):
        """
        Return a timestamp with the specified timezone and format YYYYmmDDTHMS

        :param timezone: Timezone in string format. Default America/Lima
        :return timestamp: Current timestamp with format YYYYmmDDTHMS

        >>> timestamp = set_timestamp(timezone='America/Chicago')
        >>> timestamp = '20210407T081538'
        """

        timestamp_utc = pytz.utc.localize(datetime.datetime.now())
        timestamp = timestamp_utc.astimezone(pytz.timezone(timezone)).strftime("%Y%m%dT%H%M%S")
        return timestamp


    def delete_datalake_objects(self, datalake=None, datalake_path=None):
        """
        Return the list of deleted objects in the specified datalake and path

        :param datalake: Datalake's name to delete the stored objects.
        :param datalake_path: Datalake path to delete the stored objects
        :return response: Objetcs list deleted in specified datalake and path

        >>> response = delete_datalake_objects(datalake='mydatalake', datalake_path='path/to/objects')
        >>> response = {}
        """

        client = boto3.client('s3',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            objects = client.list_objects_v2(Bucket=datalake, Prefix=datalake_path)
            if objects['KeyCount'] is not 0:
                for object in objects['Contents']:
                    response = client.delete_objects(Bucket=datalake,
                                                     Delete={'Objects': [{'Key': object['Key']}]})
            else:
                self.logger.debug(f'Empty datalake location. Please check the inserted path.')
                return None
        except client.exceptions.NoSuchBucket as err:
            self.logger.exception(f'The datalake does not exist. Please check its name: {err}')
        return response


    def send_email_notification(self, to_emails, cc_emails, bcc_emails, html_message=None):
        """
        Send and email from a verified account to the specified recipients including html content

        :param to_emails: List of destination email addresses
        :param cc_emails: List of cc email addresses
        :param bcc_emails: List of bcc email addresses
        :param html_message: Email content in HTML format
        :return response: Response from AWS SES API

        >>> response = send_email_notification(to_emails=['abc@datup.ai'], cc_emails=['def@datup.ai'], html_message='<p>Hello</p>')
        >>> response
        """

        client = boto3.client('ses',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.send_email(Source = 'no-reply@datup.ai',
                                          Destination = {
                                              'ToAddresses': to_emails,
                                              'CcAddresses': cc_emails,
                                              'BccAddresses': bcc_emails
                                          },
                                          Message = {
                                              'Subject':{
                                                  'Data': 'Datup - Pronosticos ya estan disponibles',
                                                  'Charset': 'UTF-8'
                                              },
                                              'Body': {
                                                  'Html': {
                                                      'Data': html_message,
                                                      'Charset': 'UTF-8'
                                                  }
                                              }
                                          })
        except client.exceptions.MessageRejected as err:
            self.logger.exception(f'The datalake does not exist. Please check its name: {err}')
            raise
        return response








