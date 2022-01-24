import logging

from config.settings import TGA, DATA_BASE
import json
import time
import requests
import os

logger = logging.getLogger('download')


class DownloadUtil:
    def __init__(self, obj):
        self.base_server_url = TGA['base_url']
        self.token = TGA['token']
        self.format = 'csv'
        self.name = obj['name']
        self.sql = obj['sql']

    def run(self):
        try:
            preset_data = self._prepare()
            logger.info("download %s" % preset_data.text)
            ret = json.loads(preset_data.text)
            if 'return_code' in ret and ret['return_code'] == 0:
                return self._get_all(ret['data'])
        except Exception as e:
            logger.info('download %s' % e)
        return None

    def _get_all(self, preset_data):
        """ 获取所有数据
        获取分页信息，循环调用_get_data方法获取当前页面数据，并写入csv
        """
        task_id = preset_data['taskId']
        file_name = (self.name + '_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.csv')
        path = os.path.join(DATA_BASE, 'tga_user_tag_csv_files', file_name)

        with open(path, 'w') as f:
            for i in range(preset_data['pageCount']):
                page_result = self._get_data(task_id, i)
                if page_result.text[0] == '{':
                    logger.error('download page %s', page_result.text)
                    return None
                f.write(page_result.text)

        return path

    def _prepare(self):
        """ 预处理函数

        预处理，返回分页信息
        """
        return requests.post(f'{self.base_server_url}/open/execute-sql', headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, params={
            ('token', self.token),
        }, data={
            'format': self.format, 'sql': self.sql
        }, timeout=900)

    def _get_data(self, task_id, page_id):
        """ 获取单页数据

        根据page_id获取数据
        """
        return requests.get(f'{self.base_server_url}/open/sql-result-page', headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, params=(
            ('token', self.token),
            ('taskId', task_id),
            ('pageId', page_id),
        ), timeout=900)


if __name__ == '__main__':
    du = DownloadUtil({
        'name': 'test',
        'sql': '''
          SELECT "$part_event" , count(distinct "#country_code") as country_code 
            from  ta.v_event_46
            WHERE    "$part_date" BETWEEN '2021-09-27' AND '2021-10-27' group by  "$part_event" order by count(distinct "#country_code")
           '''

    })
    result = du.run()
    print(result)
