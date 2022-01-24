# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import gc
import os
import uuid
from typing import Any, Callable, cast, List, Union

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory
from azureml.automl.core.shared.exceptions import AutoMLException, TransformException, \
    ResourceException
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.transformer_runtime_exceptions import DataTransformerInconsistentRowCountException
from scipy import sparse


class FeaturizedDataCombiners:
    """
    Given featurized data from one or more featurizers, these combiners as the name suggests, combine the data into
    a single object.

    Default being numpy based hstack; when under memory pressure, we trade diskIO for more memory efficient hstack;
    especially in the case of sparse features. Otherwise, we use scipy based sparse hstack.
    """
    @classmethod
    def get(cls,
            is_sparse: bool = True,
            is_inference_time: bool = True,
            is_low_memory: bool = False) -> Callable[..., Any]:
        """
        Factory method to obtain a combiner for featurized data. Default being np.hstack; when under memory pressure,
        we trade diskIO for more memory efficient hstack; especially in the case of sparse features.  Otherwise, we use
        scipy based sparse hstack.

        :param is_sparse: Does the featurized data contain any column that is sparse.
        :param is_inference_time: Is the combiner needed during inference time.
        :param is_low_memory: Whether we are experiencing low memory.
        :return: A callable featurized-data combiner.
        """
        if is_sparse is False:
            return FeaturizedDataCombiners.default_combiner

        if is_inference_time is False and is_low_memory is True:
            return FeaturizedDataCombiners.disk_based_sparse_combiner

        return FeaturizedDataCombiners.sparse_combiner

    @staticmethod
    def default_combiner(
        features: List[Union[np.ndarray, pd.DataFrame, sparse.spmatrix]],
        **kwargs: Any
    ) -> np.ndarray:
        """
        Default numpy based featurized combiner.

        :param features: Featurized data from individual featurizers.
        :param kwargs: The kwargs. In this case, we don't need any.
        :return: Combined featurized data.
        """
        return cast(np.ndarray, np.hstack(features))

    @staticmethod
    def sparse_combiner(
            features: List[Union[np.ndarray, pd.DataFrame, sparse.spmatrix]],
            **kwargs: Any) -> sparse.spmatrix:
        """
        Default scipy based sparse featurized data combiner.

        :param features: Featurized data from individual featurizers.
        :param kwargs: The kwargs. In this case, we don't need any.
        :return: Combined featurized data.
        """
        return sparse.hstack(features).tocsr()

    @staticmethod
    def disk_based_sparse_combiner(
            features: List[Union[np.ndarray, pd.DataFrame, sparse.spmatrix]],
            **kwargs: Any) -> sparse.spmatrix:
        """
        Memory is under pressure, trade of diskIO for a more memory-efficient way than hstack to combine feature sets.

        Solution:
        1. convert each feature set into csr matrix, collecting information for the final result arrays,
           then dump csr matrix into pickle file
        2. release memory held by feature sets
        3. allocation memory for final result arrays
        4. load csr matrix back from pickle and update the final result arrays
        5. construct final csr matrix from final result arrays without any copying

        :param features: Individual feature sets.
        :param kwargs: The kwargs containing `working_directory` and `logger` and `pickler`.
        :return: Combined features in a sparse csr matrix.
        """
        working_directory = kwargs.get('working_directory', os.getcwd())
        logger = kwargs.get('logger', None) or logging_utilities.NULL_LOGGER
        pickler = kwargs.get('pickler', DefaultPickler())
        try:
            logger.info('1. convert each feature set into csr matrix, '
                        'collecting information for the final result arrays,'
                        'then dump csr matrix into pickle file')

            final_size = 0
            column_count = 0
            row_count = -1
            offset_by_row = np.array([])  # type: np.ndarray
            dtypes = []
            pickle_files = []

            tmp_dir = os.path.join(working_directory, 'tmp_{}'.format(uuid.uuid4()))
            os.mkdir(tmp_dir)

            for i, fea in enumerate(features):
                csr = sparse.csr_matrix(fea)
                # shape info
                final_size += csr.size
                column_count += csr.shape[1]

                if row_count == -1:
                    row_count = csr.shape[0]
                    offset_by_row = np.zeros([row_count], dtype=np.int64)
                elif not row_count == csr.shape[0]:
                    raise DataTransformerInconsistentRowCountException(
                        "features have inconsistent row count", has_pii=False,
                        reference_code="data_transformer.DataTransformer.transform")

                # offset for first element in each row
                for row_index in range(row_count):
                    offset_by_row[row_index] += csr.indptr[row_index]

                # dtype info
                dtypes.append(csr.dtype)
                # pickle info
                file_name = os.path.join(tmp_dir, 'fea_{}'.format(i))
                pickle_files.append(file_name)
                pickler.dump(csr, file_name)
                del csr
                gc.collect()

            final_shape = (row_count, column_count)
            data_dtype = np.find_common_type(dtypes, [])
            logger.info('2. release memory held by feature sets')

            del features
            gc.collect()

            logger.info('3. allocation memory for final result arrays')
            final_data = np.zeros([final_size], dtype=data_dtype)
            final_indices = np.zeros(
                [final_size], dtype=sparse.sputils.get_index_dtype(maxval=max(final_shape)))
            final_indptr = np.zeros(
                [row_count + 1], dtype=sparse.sputils.get_index_dtype(maxval=final_size))

            logger.info("4. load coo matrix back from pickle and update the final result arrays")

            col_offset = 0
            for file_name in pickle_files:
                csr = pickler.load(file_name)
                # reference for csr spec:
                # https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format)
                row_offset = 0

                for i in range(row_count):
                    row_size = csr.indptr[i + 1] - csr.indptr[i]
                    row_offset += row_size
                    final_indptr[i + 1] += row_offset
                    if row_size == 0:
                        continue
                    from_slice = slice(
                        csr.indptr[i], csr.indptr[i] + row_size)
                    to_slice = slice(
                        offset_by_row[i], offset_by_row[i] + row_size)
                    final_data[to_slice] = csr.data[from_slice]
                    final_indices[to_slice] = csr.indices[from_slice] + col_offset
                    offset_by_row[i] += row_size

                col_offset += csr.shape[1]
                del csr
                gc.collect()

            logger.info('5. construct csr matrix from final result arrays without any copying')
            # the three numpy arrays won't be copied when constructing sparse matrix
            #  https://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html
            csr = sparse.csr_matrix((final_data, final_indices, final_indptr), shape=final_shape, copy=False)

            logger.info('6. Done')
            return csr
        except AutoMLException:
            raise
        except MemoryError as me:
            raise ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemory,
                    reference_code=ReferenceCodes._DISK_BASED_SPARSE_COMBINER_MEMORY,
                ), inner_exception=me) from me
        except Exception as ex:
            raise TransformException.from_exception(ex,
                                                    msg="Exception while trying to combine transformed data",
                                                    target='FeaturizedDataCombiner.disk_based_sparse_combiner',
                                                    has_pii=False,
                                                    reference_code=ReferenceCodes._DISK_BASED_SPARSE_COMBINER_EXCEPTION
                                                    )
        finally:
            # This finally block may run in a memory constrained scenario. Any
            # possible allocations should be wrapped in a try/except to ensure
            # the original exception is the outer-most.
            for f in pickle_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception:
                    logger.error(
                        'Error while removing pickle files in \
                            _featurized_data_combiners.disk_based_sparse_combiner.')
                try:
                    if len(os.listdir(tmp_dir)) == 0:
                        os.rmdir(tmp_dir)
                except Exception:
                    logger.error(
                        'Error while removing temp directory in \
                            _featurized_data_combiners.disk_based_sparse_combiner.')
