

import json
import requests
import time
import psutil
import traceback

url = "https://hooks.slack.com/services/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"    # Testing channel webhook url

class Alerter:
    """Class for sending alerts and monitoring stats to a slack channel"""

    def send_alert(message:str, url=url, userId:str=None, send_error:bool=False):
        """
        This function send alert to a target channel tagging a user with a alert message and traceback error.

        args:
                message : Pass the message to be displayed in the channel
                url : Pass webhook of target channel (if nothing is passed then #tesing channel will be alerted)
                userId : Slack userId of user who needs to be tagged (format of userid = 'Z0172K2PD5K')
                send_error : This should be set True, if slack_alert is called while catching exception
        returns: Nothing
        """
        if send_error==True:
            message = f"{message}\n{traceback.format_exc()}"
        if userId is not None:
            payload = {"text": f'<@{userId}> : {message}'}
        else:
            payload = {"text": f'{message}'}
        requests.post(url=url, data=json.dumps(payload))

    def start_monitoring():
        tic = time.time()
        initial_ram = psutil.virtual_memory().used/(1024*1000000)
        return (tic, initial_ram)

    def stop_monitoring():
        toc = time.time()
        final_ram = psutil.virtual_memory().used/(1024*1000000)
        return (toc, final_ram)

    def send_monitoring_stats(start:tuple, stop:tuple,message:str, url=url, userId:str=None):

        """
        This function send run time and RAM usage for a cronjob to a target channel tagging a user with a  message

        Args:
                message : Pass the message to be displayed in the channel
                url : Pass webhook of target channel (if nothing is passed then #tesing channel will be alerted)
                userId : Slack userId of user who needs to be tagged (format of userid = 'Z0172K2PD5K')
                start : this should be set to output of start_monitoring function
                stop : this should be set to output of start_monitoring function
        """

        tic, initial_ram = start
        toc, final_ram = stop
        run_time = round(toc-tic)
        memory_usage = round(final_ram-initial_ram, 2)

        message = f"{message}\nTotal time taken : {run_time} sec\nTotal RAM usage : {memory_usage} gb"
        if userId is not None:
            payload = {"text": f'<@{userId}> : {message}'}
        else:
            payload = {"text": f'{message}'}
        requests.post(url=url, data=json.dumps(payload))
