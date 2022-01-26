from datetime import datetime

from example.messages.ender_after_input_message import EnderAfterInputMessage
from example.messages.input_message import InputMessage
from example.messages.some_external_message import SomeExternalMessage
from example.workers.ender_after_input_worker import EnderAfterInputWorker
from unipipeline.worker.uni_worker import UniWorker
from unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage


class InputWorker(UniWorker[InputMessage, None]):
    def handle_message(self, msg: UniWorkerConsumerMessage[InputMessage]) -> None:
        # answ = '!!!'

        answ = self.manager.get_answer_from(EnderAfterInputWorker, EnderAfterInputMessage(
            value=f'from input_worker {datetime.now()}'
        ))

        self.manager.send_to('some_external_worker', SomeExternalMessage(
            value=f'answ: {answ} ==> from input_worker {datetime.now()}'
        ))
