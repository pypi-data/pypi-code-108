# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import logging
import os
import time
from retry import retry

from ibm_ai_openscale_cli.enums import ResetType
from ibm_ai_openscale_cli.openscale.openscale import OpenScale
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)
parent_dir = os.path.dirname(__file__)

DATAMART_MAX_DELETION_ATTEMPTS = 10


class NonExistingDatamartDeleteErrorFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('Failure during delete of data mart')


class OpenScaleReset(OpenScale):

    def __init__(self, args, credentials, database_credentials, ml_engine_credentials):
        super().__init__(args, credentials, database_credentials, ml_engine_credentials)

    def reset(self, reset_type):
        if reset_type is ResetType.METRICS:
            self.reset_metrics()
        elif reset_type is ResetType.MONITORS:
            self.reset_metrics()
            self.reset_monitors()
        # "factory reset" the system
        elif reset_type is ResetType.DATAMART:
            self.delete_datamart()
            self.clean_database()

    @retry(tries=5, delay=4, backoff=2)
    def reset_metrics(self):
        '''
        Clean up the payload logging table, monitoring history tables etc, so that it restores the system
        to a fresh state with datamart configured, model deployments added, all monitors configured,
        but no actual metrics in the system yet. The system is ready to go.
        '''
        if self._database is None:
            logger.log_info('Internal database metrics cannot be reset - skipping')
        else:
            logger.log_info('Deleting datamart metrics ...')
            self._database.reset_metrics_tables(self._datamart_name)
            logger.log_info('Datamart metrics deleted successfully')

    @retry(tries=5, delay=4, backoff=2)
    def reset_monitors(self):
        '''
        Remove all configured monitors and corresponding metrics and history, but leave the actual model deployments
        (if any) in the datamart. User can proceed to configure the monitors via user interface, API, or fastpath.
        '''
        logger.log_info('Deleting datamart monitors ...')
        subscription_uids = self._client.data_mart.subscriptions.get_uids()
        for subscription_uid in subscription_uids:
            try:
                start = time.time()
                subscription = self._client.data_mart.subscriptions.get(subscription_uid)
                elapsed = time.time() - start
                logger.log_timer('data_mart.subscriptions.get in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.explainability.disable()
                elapsed = time.time() - start
                logger.log_timer('subscription.explainability.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.fairness_monitoring.disable()
                elapsed = time.time() - start
                logger.log_timer('subscription.fairness_monitoring.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.performance_monitoring.disable()
                elapsed = time.time() - start
                logger.log_timer('subscription.performance_monitoring.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.payload_logging.disable()
                elapsed = time.time() - start
                logger.log_timer('subscription.payload_logging.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.quality_monitoring.disable()
                elapsed = time.time() - start
                logger.log_timer('subscription.quality_monitoring.disable in {:.3f} seconds'.format(elapsed))
                logger.log_info('Datamart monitors deleted successfully')
            except Exception as e:
                logger.log_warning('Problem during monitor reset: {}'.format(str(e)))
        logger.log_info('Datamart monitors deleted successfully')

        # finally, drop the monitor-related tables
        if self._database is None:
            logger.log_info('Internal database monitor-related tables cannot be deleted - skipping')
        else:
            logger.log_info('Deleting datamart monitor-related tables ...')
            self._database.drop_metrics_tables(self._datamart_name)
            logger.log_info('Datamart monitor-related tables deleted successfully')

    @retry(tries=5, delay=4, backoff=2)
    def delete_datamart(self):
        attempt = 0
        added_filter = False
        try:
            start = time.time()
            while attempt < DATAMART_MAX_DELETION_ATTEMPTS:  # Wait until exception is thrown to confirm datamart is completely deleted
                if attempt == 1:
                    logger.log_info('Confirming datamart deletion ...')
                elif attempt > 1:
                    logger.log_info('Confirming datamart deletion (attempt {}) ...'.format(attempt))
                data_marts = self._client.data_marts.list().result.data_marts
                specified_datamart_found = False
                if len(data_marts) > 0:
                    if self._args.datamart_id:
                        for dm in data_marts:
                            dm_id = dm.metadata.id
                            if dm_id == self._args.datamart_id:
                                specified_datamart_found = True
                                logger.log_info("Deleting datamart with id: {} ...".format(dm_id))
                                self._client.data_marts.delete(data_mart_id=dm_id, background_mode=False)
                                logger.log_info("Waiting 10 seconds for datamart cleanup")
                                time.sleep(10)  # wait a few seconds to give time for datamart cleanup
                                break
                    else:
                        for dm in data_marts:
                            dm_id = dm.metadata.id
                            logger.log_info("Deleting datamart with id: {} ...".format(dm_id))
                            self._client.data_marts.delete(data_mart_id=dm_id, background_mode=False)
                            logger.log_info("Waiting 10 seconds for datamart cleanup")
                            time.sleep(10)  # wait a few seconds to give time for datamart cleanup
                else:
                    logger.log_info('No existing datamarts found ...')
                if not specified_datamart_found:
                    break
                attempt = attempt + 1
            elapsed = time.time() - start
            logger.log_timer('data_mart.delete in {:.3f} seconds'.format(elapsed))
            logger.log_info('Datamart deleted successfully')
        except Exception as e:
            ignore_exceptions = ['AIQCS0005W', 'AIQC50005W', 'AISCS0005W']  # datamart does not exist, so cannot delete
            if any(word in str(e) for word in ignore_exceptions):
                added_filter = True
                logger.logger.addFilter(NonExistingDatamartDeleteErrorFilter())
                if attempt == 0:
                    logger.log_exception(str(e))
                    logger.log_info('Datamart not present, nothing to delete')
                else:
                    logger.log_info('Confirmed datamart deletion')
            else:
                raise e
        if added_filter:
            logger.logger.removeFilter(NonExistingDatamartDeleteErrorFilter())

    @retry(tries=5, delay=4, backoff=2)
    def clean_database(self):
        if self._database is None:
            logger.log_info('Internal database instance cannot be deleted - skipping')
        else:
            logger.log_info('Cleaning database ...')
            self._database.drop_existing_schema(self._datamart_name, self._keep_schema)
            logger.log_info('Database cleaned successfully')
