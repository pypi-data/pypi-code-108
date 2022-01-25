#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from ibmfl.party.training.local_training_handler import \
    LocalTrainingHandler

logger = logging.getLogger(__name__)


class FedAvgLocalTrainingHandler(LocalTrainingHandler):

    def train(self,  fit_params=None):
        """
        Train locally using fl_model. At the end of training, a
        model_update with the new model information is generated and
        send through the connection.

        :param fit_params: (optional) Query instruction from aggregator
        :type fit_params: `dict`
        :return: ModelUpdate
        :rtype: `ModelUpdate`
        """
        train_data, (_) = self.data_handler.get_data()
        _train_count = train_data[0].shape[0]

        self.update_model(fit_params['model_update'])

        logger.info('Local training started...')

        self.fl_model.fit_model(train_data, fit_params)

        update = self.fl_model.get_model_update()
        update.add('train_counts', _train_count)

        logger.info('Local training done, generating model update...')

        return update
