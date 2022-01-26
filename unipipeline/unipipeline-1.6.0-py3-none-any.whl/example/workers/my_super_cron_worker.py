# from example.messages.ender_after_cron_answer_message import EnderAfterCronAnswerMessage
# from example.messages.ender_after_cron_input_message import EnderAfterCronInputMessage
# from unipipeline.answer.uni_answer_message import UniAnswerMessage
from unipipeline.message.uni_cron_message import UniCronMessage
from unipipeline.worker.uni_worker import UniWorker
from unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage


class MySuperCronWorker(UniWorker[UniCronMessage, None]):
    def handle_message(self, msg: UniWorkerConsumerMessage[UniCronMessage]) -> None:
        print(f'!!!!! MySuperCronWorker MESSAGE {msg.payload}')  # noqa
        # answ: UniAnswerMessage[EnderAfterCronAnswerMessage] = self.manager.get_answer_from('ender_after_cron_worker', EnderAfterCronInputMessage(value=f'cron>>>{msg.payload.task_name}'))
        #
        # print(answ.payload.value)  # noqa
