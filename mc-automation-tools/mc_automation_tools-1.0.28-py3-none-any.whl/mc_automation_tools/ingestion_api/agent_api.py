"""This module will wrap raster agent service"""
"""
This module wrapping agent api's restful functionality
"""

from mc_automation_tools import common, base_requests


class DiscreteAgentApi:
    __trigger = 'trigger'
    __status = 'status'
    __start = 'start'
    __stop = 'stop'

    def __init__(self, end_point_url):
        self.__end_point_url = end_point_url

    @property
    def get_class_params(self):
        params = {
            'trigger': self.__trigger,
            'status': self.__status,
            'start': self.__start,
            'stop': self.__stop,
            "API url's": {'manual_trigger': common.combine_url(self.__end_point_url, self.__trigger),
                          'watch_status': common.combine_url(self.__end_point_url, self.__status),
                          'start_watch': common.combine_url(self.__end_point_url, self.__status, self.__start),
                          'stop_watch': common.combine_url(self.__end_point_url, self.__status, self.__stop)

                          }
        }
        return params

    # ===============================================Agent api's========================================================
    def post_manual_trigger(self, source_directory):
        """
        This method triggering ingestion process by manual method (from given valid directory
        """
        body = {'sourceDirectory': source_directory}
        url = common.combine_url(self.__end_point_url, self.__trigger)
        resp = base_requests.send_post_request(url, body)
        return resp

    def get_watching_statuses(self):
        """
        This method return bool -> true if watcher is on, false if watcher
        """
        url = common.combine_url(self.__end_point_url, self.__status)
        resp = base_requests.send_get_request(url)
        return resp

    def post_start_watch(self):
        """
        This method change watcher status to true and return -> "watching": true
        """
        url = common.combine_url(self.__end_point_url, self.__status, self.__start)
        resp = base_requests.send_post_request(url)
        return resp

    def post_stop_watch(self):
        """
        This method change watcher status to true and return -> "watching": false
        """
        url = common.combine_url(self.__end_point_url, self.__status, self.__stop)
        resp = base_requests.send_post_request(url)
        return resp
