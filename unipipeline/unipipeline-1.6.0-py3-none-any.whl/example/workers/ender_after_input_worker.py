from example.messages.ender_after_answer_message import EnderAfterAnswerMessage
from example.messages.ender_after_input_message import EnderAfterInputMessage
from unipipeline.worker.uni_worker import UniWorker
from unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage


class EnderAfterInputWorker(UniWorker[EnderAfterInputMessage, EnderAfterAnswerMessage]):
    def handle_message(self, msg: UniWorkerConsumerMessage[EnderAfterInputMessage]) -> EnderAfterAnswerMessage:
        print(f'>>>>> {msg.payload}')  # noqa
        return EnderAfterAnswerMessage(
            value=f'EnderAfterInputWorker answer on >>> {msg.payload.value}'
        )
