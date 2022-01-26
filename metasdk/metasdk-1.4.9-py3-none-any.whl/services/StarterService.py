import json
from time import sleep

import requests
import time


class StarterService:
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, app, db, starter_api_url):
        """
        Прямые запросы к БД скорее всего уйдут в апи запускатора, так как скорее всего пбудет много БД для тасков запускатора, так как
        Если будет 100500 шард, то врядли все будет в одной БД

        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__metadb = db
        self.__starter_api_url = starter_api_url
        self.log = app.log
        self.max_retries = 30

    def update_task_result_data(self, task):
        self.log.info("Сохраняем состояние в БД", {"result_data": task['result_data']})
        self.__metadb.update("""
            UPDATE job.task
            SET result_data=:result_data::jsonb
            WHERE id=:task_id::uuid
            AND service_id=:service_id::job.service_id
        """, {
            "task_id": task.get('taskId'),
            "service_id": task.get('serviceId'),
            "result_data": json.dumps(task['result_data'])
        })

    def await_task(self, task_id, service_id, callback_fn=None, sleep_sec=15):
        """
        Подождать выполнения задачи запускатора

        :param task_id: ID задачи, за которой нужно следить
        :param service_id: ID сервиса
        :param callback_fn: Функция обратного вызова, в нее будет передаваться task_info и is_finish как признак, что обработка завершена
        :param sleep_sec: задержка между проверкой по БД. Не рекомендуется делать меньше 10, так как это может очень сильно ударить по производительности БД
        :return: None|dict
        """
        while True:
            time.sleep(sleep_sec)
            task_info = self.__metadb.one("""
                SELECT id, service_id, status, result_data 
                FROM job.task
                WHERE id=:task_id::uuid
                AND service_id=:service_id::job.service_id
                LIMIT 1
            """, {
                "task_id": task_id,
                "service_id": service_id,
            })
            self.log.info("Ждем выполнения задачи", {
                "task_info": task_info
            })
            if task_info is None:
                return None

            is_finish = task_info['status'] != 'NEW' and task_info['status'] != 'PROCESSING'

            if callback_fn:
                # Уведомляем вызывающего
                callback_fn(task_info, is_finish)

            if is_finish:
                return task_info

    def submit(self, service_id: str, data: dict = None):
        """
        Отправить задачу в запускатор

        :param service_id: ID службы. Например "meta.docs_generate"
        :param data: Полезная нагрузка задачи
        :return: dict
        """
        # импорт тут, так как глобально над классом он не работает
        from metasdk import DEV_STARTER_STUB_URL

        if self.__starter_api_url == DEV_STARTER_STUB_URL:
            self.log.info('STARTER DEV. Задача условно поставлена', {
                "service_id": service_id,
                "data": data,
            })
            return

        task = {"serviceId": service_id, "data": data}
        url = self.__starter_api_url + '/services/' + service_id + '/tasks'
        last_e = None
        for _idx in range(self.max_retries):
            try:
                resp = requests.post(
                    url=url,
                    data=json.dumps(task),
                    headers=self.headers,
                    timeout=15
                )
                try:
                    return json.loads(resp.text)
                except Exception:
                    raise IOError("Starter response read error: " + resp.text)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # При ошибках подключения пытаемся еще раз
                last_e = e
                sleep(3)
        raise last_e
