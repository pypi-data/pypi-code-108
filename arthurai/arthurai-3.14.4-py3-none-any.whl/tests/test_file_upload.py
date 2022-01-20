from collections import namedtuple
from http import HTTPStatus
from typing import Any, Type, Optional, Union, List, NamedTuple

import os
from unittest.mock import patch

import pandas as pd
import pytest
import responses

from arthurai import ArthurModel
from arthurai.common.exceptions import UserValueError, ResponseClientError, ResponseServerError, ArthurInternalError
from arthurai.core.inferences import add_inference_metadata_to_dataframe
from tests.helpers import mock_post, MockShortUUID, MockDatetime, mock_patch
from tests.fixtures.mocks import client
from tests.fixtures.models.regression import batch_model, INT_INPUT, FLOAT_NONINPUT, PRED, GROUND_TRUTH, TABULAR_MODEL_ID


class TestBulkInferences:

    INT_INPUT_VALUES = [1, 2, 3, 4]
    FLOAT_INPUT_VALUES = [1.1, 2.2, 3.3, 4.4]
    PRED_VALUES = [0.6, 0.4, 0.7, 0.3]
    GROUND_TRUTH_VALUES = [1, 1, 1, 0]
    TIMESTAMP_VALUE = 'ts1'
    INFERENCE_TIMESTAMP_VALUES = [TIMESTAMP_VALUE] * 4
    GROUND_TRUTH_TIMESTAMP_VALUES = [TIMESTAMP_VALUE] * 4
    PARTNER_INFERENCE_ID_VALUES = ['inf1', 'inf2', 'inf3', 'inf4']

    INFERENCE_DATA = {
        INT_INPUT: INT_INPUT_VALUES,
        FLOAT_NONINPUT: FLOAT_INPUT_VALUES,
        PRED: PRED_VALUES
    }

    INFERENCE_ONLY_DF = pd.DataFrame({**INFERENCE_DATA, 'inference_timestamp': INFERENCE_TIMESTAMP_VALUES,
                                      'partner_inference_id': PARTNER_INFERENCE_ID_VALUES})
    INFERENCE_AND_GT_DF = pd.DataFrame({**INFERENCE_DATA, 'inference_timestamp': INFERENCE_TIMESTAMP_VALUES,
                                        'partner_inference_id': PARTNER_INFERENCE_ID_VALUES,
                                        GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                        'ground_truth_timestamp': GROUND_TRUTH_TIMESTAMP_VALUES})
    GT_ONLY_DF = pd.DataFrame({'partner_inference_id': PARTNER_INFERENCE_ID_VALUES, GROUND_TRUTH: GROUND_TRUTH_VALUES,
                               'ground_truth_timestamp': GROUND_TRUTH_TIMESTAMP_VALUES})

    DATASET_CLOSE_SUCCESS_RESULT = {"dataset_close_result": {'message': "success"}}

    def _mock_sending_reference_set(self, model_id):
        server_response = {
            "counts": {
                "success": 0,
                "failure": 1,
                "total": 1
            },
            "failures": [
                {
                    "message": "missing field",
                    "status": 400
                }
            ]
        }

        mock_post(f"/api/v3/models/{model_id}/reference_data", server_response, status=207)
        mock_patch(f"/api/v3/models/{model_id}/reference_data", status=200,
                   response_body={"message": "success"})

    def _mock_batch_upload(self, model_id, batch_id):
        server_response = {
            "counts": {
                "success": 100,
                "failure": 0,
                "total": 100
            },
            "failures": []
        }

        mock_post(f"/api/v3/models/{model_id}/inferences/file", server_response, status=207)
        mock_patch(f"/api/v3/models/{model_id}/batches/{batch_id}", status=200,
                   response_body={"message": "success"})

    def _mock_failed_batch_upload(self, model_id, batch_id):
        mock_post(f"/api/v3/models/{model_id}/inferences/file", {}, status=HTTPStatus.SERVICE_UNAVAILABLE)

    def _mock_failed_batch_close(self, model_id, batch_id):
        server_response = {
            "counts": {
                "success": 100,
                "failure": 0,
                "total": 100
            },
            "failures": []
        }

        mock_post(f"/api/v3/models/{model_id}/inferences/file", server_response, status=207)
        mock_patch(f"/api/v3/models/{model_id}/batches/{batch_id}", {}, status=HTTPStatus.SERVICE_UNAVAILABLE)

    @responses.activate
    def test_send_set_reference_data(self, batch_model):
        self._mock_sending_reference_set(TABULAR_MODEL_ID)
        resp, resp_close = batch_model.set_reference_data(data=pd.DataFrame(
            {**self.INFERENCE_DATA, GROUND_TRUTH: self.GROUND_TRUTH_VALUES}))
        assert resp["counts"]["failure"] == 1
        assert resp_close is None

    @responses.activate
    def test_send_bulk_inferences(self, batch_model):
        self._mock_batch_upload(TABULAR_MODEL_ID, 'batch_1')
        resp, resp_close = batch_model.send_bulk_inferences(
            data=pd.DataFrame({
                INT_INPUT: self.INT_INPUT_VALUES,
                FLOAT_NONINPUT: self.FLOAT_INPUT_VALUES,
                PRED: self.PRED_VALUES,
                "inference_timestamp": self.INFERENCE_TIMESTAMP_VALUES,
                "partner_inference_id": self.PARTNER_INFERENCE_ID_VALUES,
            }),
            batch_id='batch_1')
        self._assert_result(resp)
        assert resp_close == self.DATASET_CLOSE_SUCCESS_RESULT

    @responses.activate
    def test_send_batch_inferences_auto_retry(self, batch_model):
        self._mock_failed_batch_upload(TABULAR_MODEL_ID, "batch_1")
        with pytest.raises(ArthurInternalError) as e:
            batch_model.send_batch_inferences(
                data=pd.DataFrame({
                    INT_INPUT: self.INT_INPUT_VALUES,
                    FLOAT_NONINPUT: self.FLOAT_INPUT_VALUES,
                    PRED: self.PRED_VALUES,
                    "inference_timestamp": self.INFERENCE_TIMESTAMP_VALUES,
                    "partner_inference_id": self.PARTNER_INFERENCE_ID_VALUES
                }),
                batch_id='batch_1')
        # assert this internal exception came from a ResponseServerError
        assert isinstance(e.value.__cause__, ResponseServerError)
        assert len(responses.calls) == 4
        resp_500 = 0
        for http_call in responses.calls:
            if http_call.response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                resp_500 += 1
        assert resp_500 == 4

    @responses.activate
    def test_send_batch_close_auto_retry(self, batch_model):
        self._mock_failed_batch_close(TABULAR_MODEL_ID, "batch_1")
        with pytest.raises(ArthurInternalError) as e:
            batch_model.send_bulk_inferences(
                data=pd.DataFrame({
                    INT_INPUT: self.INT_INPUT_VALUES,
                    FLOAT_NONINPUT: self.FLOAT_INPUT_VALUES,
                    PRED: self.PRED_VALUES,
                    "inference_timestamp": self.INFERENCE_TIMESTAMP_VALUES,
                    "partner_inference_id": self.PARTNER_INFERENCE_ID_VALUES,
                }),
                batch_id='batch_1')
        # assert this internal exception came from a ResponseServerError
        assert isinstance(e.value.__cause__, ResponseServerError)
        assert len(responses.calls) == 5
        resp_500 = 0
        for http_call in responses.calls:
            if http_call.response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                resp_500 += 1
        assert resp_500 == 4

    @responses.activate
    def test_send_bulk_ground_truth(self, batch_model):
        self._mock_batch_upload(TABULAR_MODEL_ID, 'batch_1')
        resp = batch_model.send_batch_ground_truths(
            data=pd.DataFrame({GROUND_TRUTH: self.GROUND_TRUTH_VALUES,
                               "partner_inference_id": self.PARTNER_INFERENCE_ID_VALUES,
                               "ground_truth_timestamp": self.GROUND_TRUTH_TIMESTAMP_VALUES}))
        self._assert_result(resp)

    @responses.activate
    def test_send_parquet_batch(self, batch_model):
        self._mock_batch_upload(TABULAR_MODEL_ID, 'batch_1')
        file_loc = os.path.join(os.path.dirname(__file__), 'data', 'inference_batch_data')
        resp, close_resp = batch_model.send_bulk_inferences(batch_id="batch_1", directory_path=file_loc)
        self._assert_result(resp)
        assert close_resp == self.DATASET_CLOSE_SUCCESS_RESULT

    # these cases are used  by two tests below: primarily for testing of the add_inference_metadata_to_dataframe()
    #  method but also include a broader test of send_bulk_inferences() to ensure no exceptions occur along the full
    #  processing chain
    class BulkInferencesCase(NamedTuple):
        input_dataframe: pd.DataFrame
        partner_inf_ids: Optional[List[str]]
        expected_result: Union[pd.DataFrame, Type[BaseException]]
        ignore_join_errors: Optional[bool] = None

    bulk_inferences_metadata_cases = [
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, GROUND_TRUTH: GROUND_TRUTH_VALUES}),
            partner_inf_ids=PARTNER_INFERENCE_ID_VALUES, expected_result=INFERENCE_AND_GT_DF),
            id="inf-and-gt-data-no-metadata"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                          'inference_timestamp': INFERENCE_TIMESTAMP_VALUES}),
            partner_inf_ids=PARTNER_INFERENCE_ID_VALUES, expected_result=INFERENCE_AND_GT_DF),
            id="inf-and-gt-data-inf-ts-only"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                          'ground_truth_timestamp': GROUND_TRUTH_TIMESTAMP_VALUES}),
            partner_inf_ids=PARTNER_INFERENCE_ID_VALUES, expected_result=INFERENCE_AND_GT_DF),
            id="inf-and-gt-data-gt-ts-only"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                          'partner_inference_id': PARTNER_INFERENCE_ID_VALUES}),
            partner_inf_ids=None, expected_result=INFERENCE_AND_GT_DF), id="inf-and-gt-data-gt-partner-ids-only"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                          'partner_inference_id': PARTNER_INFERENCE_ID_VALUES}),
            partner_inf_ids=None, expected_result=GT_ONLY_DF), id="gt-data-only-no-ts"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({GROUND_TRUTH: GROUND_TRUTH_VALUES,
                                          'ground_truth_timestamp': GROUND_TRUTH_TIMESTAMP_VALUES,
                                          'partner_inference_id': PARTNER_INFERENCE_ID_VALUES}),
            partner_inf_ids=None, expected_result=GT_ONLY_DF), id="gt-data-only-with-ts"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({GROUND_TRUTH: GROUND_TRUTH_VALUES}), partner_inf_ids=None,
            expected_result=UserValueError), id="gt-data-only-missing-ids"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame(INFERENCE_DATA), partner_inf_ids=PARTNER_INFERENCE_ID_VALUES,
            expected_result=INFERENCE_ONLY_DF, ignore_join_errors=True), id="inf-data-no-metadata"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame(INFERENCE_DATA), partner_inf_ids=None,
            expected_result=UserValueError), id="inf-data-no-metadata-error"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, 'partner_inference_id': PARTNER_INFERENCE_ID_VALUES}),
            partner_inf_ids=None, expected_result=INFERENCE_ONLY_DF), id="inf-data-partner-ids-only"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, 'inference_timestamp': INFERENCE_TIMESTAMP_VALUES}),
            partner_inf_ids=PARTNER_INFERENCE_ID_VALUES, expected_result=INFERENCE_ONLY_DF, ignore_join_errors=True),
            id="inf-data-ts-only"),
        pytest.param(BulkInferencesCase(
            input_dataframe=pd.DataFrame({**INFERENCE_DATA, 'inference_timestamp': INFERENCE_TIMESTAMP_VALUES}),
            partner_inf_ids=None, expected_result=UserValueError),
            id="inf-data-ts-only-error")
    ]

    @responses.activate
    @pytest.mark.parametrize("case", bulk_inferences_metadata_cases)
    def test_send_bulk_inferences_missing_metadata(self, batch_model, case: BulkInferencesCase):
        self._mock_batch_upload(TABULAR_MODEL_ID, 'batch_1')
        uuid_generator = MockShortUUID(case.partner_inf_ids)
        datetime_generator = MockDatetime([self.TIMESTAMP_VALUE], return_raw_strings=True)

        with patch("arthurai.core.inferences.shortuuid.uuid") as uuid_mock:
            with patch("arthurai.core.inferences.datetime") as datetime_mock:
                uuid_mock.side_effect = uuid_generator.next
                datetime_mock.now.side_effect = datetime_generator.next
                kwargs = {'data': case.input_dataframe, 'batch_id': 'batch_1'}
                if case.ignore_join_errors is not None:
                    kwargs['ignore_join_errors'] = case.ignore_join_errors
                if isinstance(case.expected_result, pd.DataFrame):
                    resp, resp_close = batch_model.send_bulk_inferences(**kwargs)
                else:
                    with pytest.raises(case.expected_result):
                        batch_model.send_bulk_inferences(**kwargs)

        if isinstance(case.expected_result, pd.DataFrame):
            self._assert_result(resp)
            assert resp_close == self.DATASET_CLOSE_SUCCESS_RESULT

        assert uuid_generator.call_count() == (len(case.partner_inf_ids) if case.partner_inf_ids is not None else 0)

    @pytest.mark.parametrize("case", bulk_inferences_metadata_cases)
    def test_add_inference_metadata_to_dataframe(self, batch_model, case: BulkInferencesCase):
        uuid_generator = MockShortUUID(case.partner_inf_ids)
        datetime_generator = MockDatetime([self.TIMESTAMP_VALUE], return_raw_strings=True)

        input_df_copy = case.input_dataframe.copy(deep=True)

        with patch("arthurai.core.inferences.shortuuid.uuid") as uuid_mock:
            with patch("arthurai.core.inferences.datetime") as datetime_mock:
                uuid_mock.side_effect = uuid_generator.next
                datetime_mock.now.side_effect = datetime_generator.next
                kwargs = {'df': case.input_dataframe, 'model_attributes': batch_model.attributes}
                if case.ignore_join_errors is not None:
                    kwargs['ignore_join_errors'] = case.ignore_join_errors
                if isinstance(case.expected_result, pd.DataFrame):
                    actual_output_df = add_inference_metadata_to_dataframe(**kwargs)
                else:
                    with pytest.raises(case.expected_result):
                        add_inference_metadata_to_dataframe(**kwargs)

        if isinstance(case.expected_result, pd.DataFrame):
            # don't care about column order so sort before comparing
            pd.testing.assert_frame_equal(actual_output_df.reindex(sorted(actual_output_df.columns), axis=1),
                                          case.expected_result.reindex(sorted(case.expected_result.columns), axis=1))

        assert uuid_generator.call_count() == (len(case.partner_inf_ids) if case.partner_inf_ids is not None else 0)
        # assert input dataframe not modified
        pd.testing.assert_frame_equal(case.input_dataframe, input_df_copy)

    @staticmethod
    def _assert_result(resp: Any, success_count: int = 100, failure_count: int = 0, total_count: int = 100):
        assert resp["counts"]["success"] == success_count
        assert resp["counts"]["failure"] == failure_count
        assert resp["counts"]["total"] == total_count
