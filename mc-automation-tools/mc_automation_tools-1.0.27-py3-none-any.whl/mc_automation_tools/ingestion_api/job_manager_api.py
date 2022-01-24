"""
This module is the wrapper for job manager api according provided swagger
"""
import json
import time
import logging
from mc_automation_tools.configuration import config
from mc_automation_tools import base_requests, common

_log = logging.getLogger('mc_automation_tools.ingestion_api.job_manager_api')


class JobsTasksManager:
    __jobs_api = 'jobs'
    __resettable = 'resettable'
    __reset = 'reset'
    __tasks = 'tasks'
    __tasks_status = 'tasksStatus'
    __find = 'find'
    __start_pending = 'startPending'
    __find_inactive = 'findInactive'
    __release_inactive = 'releaseInactive'
    __update_expired_status = 'updateExpiredStatus'

    def __init__(self, end_point_url):
        self.__end_point_url = end_point_url

    @property
    def get_class_params(self):
        params = {
            'jobs_api': self.__jobs_api,
            'resettable': self.__resettable,
            'reset': self.__reset,
            'tasks': self.__tasks,
            'tasks_status': self.__tasks_status,
            'find': self.__find,
            'start_pending': self.__start_pending,
            'find_inactive': self.__find_inactive,
            'release_inactive': self.__release_inactive,
            'update_expired_status': self.__update_expired_status
        }
        return params

    # ===============================================jobs api's=========================================================
    def find_jobs_by_criteria(self, params):
        """
        This method will query and return information about jobs and tasks on job manager db by providing query params
        * user should provide dict to parameters according the api:
            {
                'resourceId': string,
                'version': string,
                'isCleaned': bool,
                'status': string -> [Pending, In-Progress, Completed, Failed],
                'type': string -> [The type of the job],
                'shouldReturnTasks': bool -> default is True

            }
        :param params: query params -> resourceId, version, isCleaned, status, type, shouldReturnTasks
        :return: full jobs status + tasks by params
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api)
        resp = base_requests.send_get_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[find_jobs_by_criteria]:failed retrieve jobs, return with error:[{resp.status_code}],error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def create_new_job(self, body):
        """
        This method will write new job into DB of job manager -> jobs table, example:
        {
          "resourceId": "string",
          "version": "string",
          "description": "string",
          "parameters": {},
          "status": "Pending",
          "reason": "string",
          "type": "string",
          "percentage": 100,
          "priority": 0,
          "expirationDate": "2021-11-30T11:59:56.954Z",
          "tasks": [
            {
              "description": "string",
              "parameters": {},
              "reason": "string",
              "percentage": 100,
              "type": "string",
              "status": "Pending",
              "attempts": 0
            }
          ]
        }
        :param body: json body of requested params
        :return: json of job id and related task ids
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api)
        if isinstance(body, dict):
            body = json.dumps(body)
        elif not isinstance(body, str):
            raise ValueError(f'params is not on valid params -> json or dict')

        resp = base_requests.send_post_request(url, body)
        if resp.status_code != config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'[create_new_job]:failed on creation new job, return with error:[{resp.status_code}],error msg:[{str(resp.content)}]')
        return json.loads(resp.content)

    def get_job_by_id(self, uuid, return_tasks=True):
        """
        This method will query specific job according its uuid
        :param uuid: str -> unique id of job provided on creation
        :param return_tasks: bool -> Flag if provide with response also the tasks related
        :return: json\ dict of the job
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid)
        params = {'shouldReturnTasks': str(return_tasks).lower()}
        resp = base_requests.send_get_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[get_job_by_id]:failed retrieve job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def updates_job(self, uuid, body):
        """
        This method based on PUT rest request to update exists job
        example of body:
            {
              "parameters": {},
              "status": "Pending",
              "percentage": 100,
              "reason": "string",
              "isCleaned": true,
              "priority": 0,
              "expirationDate": "2021-11-30T12:27:46.951Z"
            }
        :param uuid: str -> unique id of job provided on creation
        :param body: dict -> entire parameters to change
        :return: success message
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid)
        if isinstance(body, dict):
            body = json.dumps(body)
        elif not isinstance(body, str):
            raise ValueError(f'params is not on valid params -> json or dict')
        resp = base_requests.send_put_request(url, body)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[get_job_by_id]:failed update job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')
        return resp.text

    def delete_job(self, uuid, return_tasks=True):
        """
        This method will delete job from job manager db based on provided uuid
        :param uuid: str -> unique id of job provided on creation
        :param return_tasks: bool -> Flag if provide with response also the tasks related
        :return: response state
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid)
        params = json.dumps({'shouldReturnTasks': return_tasks})
        resp = base_requests.send_delete_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[delete_job]:failed delete job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def resettable(self, uuid):
        """
        This method check if job is resettable
        :param uuid: str -> unique id of job provided on creation
        :return: dict -> {jobId:str, isResettable:bool} on success
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid, self.__resettable)
        resp = base_requests.send_post_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[resettable]:failed get resettable state for job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def reset(self, uuid):
        """
        This method reset a resettable job
        :param uuid: str -> unique id of job provided on creation
        :return: dict -> {jobId:str, isResettable:bool} on success
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid, self.__reset)
        resp = base_requests.send_post_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[reset]:failed start reset on resettable job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return str(resp.text)

    # ===============================================tasks api's========================================================
    def tasks(self, uuid):
        """
        This method will get all tasks under provided id of job
        :param uuid: str -> unique id of job provided on creation
        :return: list[dict] -> list of dicts representing all tasks under provided job
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid, self.__tasks)
        resp = base_requests.send_get_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[tasks]:failed get tasks of job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def create_task(self, uuid, body):
        """
        This method will get all tasks under provided id of job
        * example of body:
            {
              "description": "string",
              "parameters": {},
              "reason": "string",
              "percentage": 100,
              "type": "string",
              "status": "Pending",
              "attempts": 0
            }
        :param uuid: str -> unique id of job provided on creation
        :param body: dict -> body contain of the fields to insert on new task
        :return: dict -> id: <new id of the created task>
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, uuid, self.__tasks)
        resp = base_requests.send_post_request(url, body)
        if resp.status_code != config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'[create_task]:failed insert new task to job, return with error:[{resp.status_code}]:error msg:[{str(resp.content)}]')

        return json.loads(resp.content)

    def get_task_by_task_id(self, job_id, task_id):
        """
        This method return task data by providing job-uuid and task-uuid
        :param job_id: uuid of related job
        :param task_id: uuid of requested task
        :return: dict(json) of task
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, job_id, self.__tasks, task_id)
        resp = base_requests.send_get_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[get_task_by_task_id]:failed retrieve task data, return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return json.loads(resp.content)

    def update_task_by_task_id(self, job_id, task_id, params):
        """
        This method update task data by providing job-uuid and task-uuid + body with changes:
        example for body:
            {
              "description": "string",
              "parameters": {},
              "status": "Failed", # mendatory
              "percentage": 0,
              "reason": "string",
              "attempts": 0
            }
        :param job_id: uuid of related job
        :param task_id: uuid of requested task
        :param params: dict with body params
        :return: status
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, job_id, self.__tasks, task_id)
        resp = base_requests.send_put_request(url, json.dumps(params))
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[update_task_by_task_id]:failed update task data, return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return resp.text

    def delete_task_by_task_id(self, job_id, task_id):
        """
        This method delete task data by providing job-uuid and task-uuid
        :param job_id: uuid of related job
        :param task_id: uuid of requested task
        :return: status
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, job_id, self.__tasks, task_id)
        resp = base_requests.send_delete_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[update_task_by_task_id]:failed delete task data, return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return resp.text

    def get_all_tasks_status(self, job_id):
        """
        This method get all tasks statuses of a job
        :param job_id: uuid of job
        :return: json-> {
                          "allTasksCompleted": true,
                          "failedTasksCount": 0,
                          "completedTasksCount": 0,
                          "resourceId": "string",
                          "resourceVersion": "string"
                        }
        """
        url = common.combine_url(self.__end_point_url, self.__jobs_api, job_id, self.__tasks_status)
        resp = base_requests.send_get_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[get_all_tasks_status]:failed get tasks status for job: [{job_id}], return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return json.loads(resp.content)

    def find_tasks(self, params):
        """
        This method will find and return list of tasks that answer the params requirements.
        example of body:
            {
              "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
              "percentage": 0,
              "jobId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
              "creationTime": "2021-12-01T15:14:45.283Z",
              "updateTime": "2021-12-01T15:14:45.283Z",
              "description": "string",
              "type": "string",
              "reason": "string",
              "status": "Pending",
              "attempts": 0,
              "parameters": {}
            }
        :param params: dict of mutual parameters for task
        :return: params-> [
                              {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "jobId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "description": "string",
                                "parameters": {},
                                "created": "2021-12-01T15:14:45.284Z",
                                "updated": "2021-12-01T15:14:45.284Z",
                                "status": "Pending",
                                "percentage": 0,
                                "reason": "string",
                                "attempts": 0
                              }
                        ]
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, self.__find)
        resp = base_requests.send_post_request(url, params)
        s_code, content = common.response_parser(resp)
        if s_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[find_tasks]:failed find tasks , return with error:[{s_code}]:error msg:[{content})]')

        return content

    # ===========================================tasks management api's=================================================

    def start_pending(self, job_type, task_type):
        """
        This method will retrieve the highest priority pending task and update its status to In-Progress.
        :param job_type: str -> the type of the job on job manager
        :param task_type: str -> the type of the task on job manager
        :return: dict-> {
                              "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                              "jobId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                              "description": "string",
                              "parameters": {},
                              "created": "2021-12-01T16:19:51.873Z",
                              "updated": "2021-12-01T16:19:51.873Z",
                              "status": "Pending",
                              "percentage": 0,
                              "reason": "string",
                              "attempts": 0
                           }
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, task_type, self.__start_pending)
        resp = base_requests.send_post_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[start_pending]:failed find pending tasks , return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return json.loads(resp.content)

    def find_inactive(self, params):
        """
        This method will retrieve list of inactive tasks ids
        :param params: dict -> the type of inactive task to retrieve, example to request body:
            {
              "inactiveTimeSec": 0,
              "types": [
                {
                  "jobType": "string",
                  "taskType": "string"
                }
              ],
              "ignoreTypes": [
                {
                  "jobType": "string",
                  "taskType": "string"
                }
              ]
            }
        :return: list[str] -> list of id's of inactive tasks
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, self.__find_inactive)
        resp = base_requests.send_post_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[find_inactive]:failed retrieve inactive tasks , return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return json.loads(resp.content)

    def release_inactive(self, list_of_ids):
        """
        This method will release all inactive tasks ids
        :param list_of_ids: list of id's to release
        :return: list[str] -> list of id's of inactive tasks
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, self.__release_inactive)
        resp = base_requests.send_post_request(url, list_of_ids)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[release_inactive]:failed release inactive tasks , return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return json.loads(resp.content)

    def update_expired_status(self):
        """
        This method will update status of open jobs and tasks to "Expired" if their expiration date has passed
        :return:
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, self.__update_expired_status)
        resp = base_requests.send_post_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[update_expired_status]:failed update, return with error:[{resp.status_code}]:error msg:[{str(resp.text)}]')

        return str(resp.text)

    # ========================================== Shared components =====================================================
    def follow_running_job_manager(self, product_id, product_version, product_type='Discrete-Tiling', timeout=300,
                                   internal_timeout=80):
        """This method will follow running ingestion task and return results on finish"""

        t_end = time.time() + timeout
        running = True
        find_job_params = {
            'resourceId': product_id,
            'version': product_version,
            'shouldReturnTasks': str(True).lower(),  # example to make it compatible to query params
            'type': product_type
        }
        resp = self.find_jobs_by_criteria(find_job_params)[0]
        if not resp:
            raise Exception(f'Job for {product_id}:{product_version} not found')
        _log.info(f'Found job with details:\n'
                  f'id: [{resp["id"]}]\n'
                  f'resourceId (product id): [{resp["resourceId"]}]\n'
                  f'version: [{resp["version"]}]\n'
                  f'parameters: [{resp["parameters"]}]\n'
                  f'status: [{resp["status"]}]\n'
                  f'percentage: [{resp["percentage"]}]\n'
                  f'reason: [{resp["reason"]}]\n'
                  f'isCleaned: [{resp["isCleaned"]}]\n'
                  f'priority: [{resp["priority"]}]\n'
                  f'Num of tasks related to job: [{len(resp["tasks"])}]')
        job = resp

        while running:
            time.sleep(internal_timeout // 4)
            job_id = job['id']
            job = self.get_job_by_id(job_id)  # now getting job info by unique job id

            job_id = job['id']
            status = job['status']
            reason = job['reason']
            tasks = job['tasks']

            completed_task = sum(1 for task in tasks if task['status'] == config.JobStatus.Completed.name)
            _log.info(f'\nStatus of job for resource: {product_id}:{product_version} is [{status}]\n'
                      f'finished tasks for current job: {completed_task} / {len(tasks)}')

            if status == config.JobStatus.Completed.name:
                return {'status': status, 'message': " ".join(['OK', reason]), 'job_id': job_id, 'tasks': tasks}
            elif status == config.JobStatus.Failed.name:
                return {'status': status, 'message': " ".join(['Failed: ', reason]), 'job_id': job_id, 'tasks': tasks}

            current_time = time.time()

            if t_end < current_time:
                return {'status': status, 'message': " ".join(['Failed: ', 'got timeout while following job running']),
                        'job_id': job_id, 'tasks': tasks}
