import time

import codefast as cf
from telegram import Update

from dofast.bots.processors.base import TextProcessor


class PcloudProcessor(TextProcessor):
    """ Receive file url from input text, parse out url and relative information.
    Then download the file(s) and finally upload file(s) to pcloud.
    """
    def match(self, text: str) -> bool:
        file_formats = 'mp4/mp3/jpg/png/bin/m3u8/gif/pdf/docx/doc/ppt/pptx/xls/xlsx/txt/mkv/avi/mpg/mpeg/mov'
        file_formats = file_formats.split('/')
        if not text.startswith('http'):
            return False
        return any(ext in text for ext in file_formats)

    def run(self, text: str, update: Update) -> str:
        # celery.handle_task(update.message.chat_id, text)
        # update.message.reply
        from celery.states import EXCEPTION_STATES
        from dofast.bots.asyncjobs import cloudsync
        update.message.delete()
        update.message = update.message.reply_text(
            '{} \nMission received, processing...'.format(text))
        task = cloudsync.delay(text)
        TIMEOUT, MAX_FAILURE = 1200, 3
        timeout_msg = "TIMEOUT. Task {} did not finish in {} seconds".format(
            text, TIMEOUT)

        while TIMEOUT >= 0:
            if task.status in EXCEPTION_STATES:
                if MAX_FAILURE <= 0:
                    return 'FAILED'
                msg = '❌ Task {} failed with status {}. Retrying ...'.format(
                    text, task.status)
                update.message.reply_text(msg)
                task = cloudsync.delay(text)
                MAX_FAILURE -= 1
            elif task.status == 'SUCCESS':
                msg = '✅ Task 【 {} 】 finished. File URL is: \n{}'.format(
                    text, task.result)
                update.message.delete()
                update.message.reply_text(msg)
                return 'SUCCESS'
            time.sleep(10)
            TIMEOUT -= 10
        update.message.reply_text(timeout_msg)
        return 'FAILED'
