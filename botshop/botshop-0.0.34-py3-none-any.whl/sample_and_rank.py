import sys

import numpy as np


def response_score(scores):
    response_length = len(scores)
    if response_length == 0:
        return float('inf')

    response_prob = np.prod(scores)
    if response_prob == 0.0:
        return float('inf')
    else:
        return -np.sum(np.log(scores))/response_length


class SampleAndRank:

    def __init__(self, *args, num_candidate_responses=20, **kwargs):
        """
        Mixin for conversation engines to generate multiple candidate responses and choose the best one.

        :param num_candidate_responses:

        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self._num_candidate_responses = num_candidate_responses

    def respond(self, inputs, conversation_start=False):
        processed_inputs = self._io_processor.process_inputs(inputs, conversation_start)

        self._model_evaluator.update_context(processed_inputs, self._conversation_context, conversation_start)

        responses = []
        response_scores = []

        while len(responses) < self._num_candidate_responses:
            response, scores = self._create_response()

            if response in responses:
                continue

            responses += [response]
            response_scores += [response_score(scores)]

        sort_idx = np.argsort(response_scores)
        response_scores = [response_scores[i] for i in sort_idx]
        responses = [responses[i] for i in sort_idx]

        if self._debug:
            self._log.debug("Potential responses : ")
            for r, s in zip(responses, response_scores):
                s = round(s*100)/100 if s != float('inf') else "INF"
                sys.stdout.write(f"[{s}]\t: {r}\n")

        response_idx = np.argmin(response_scores)

        return responses[response_idx], [response_scores[response_idx]]

