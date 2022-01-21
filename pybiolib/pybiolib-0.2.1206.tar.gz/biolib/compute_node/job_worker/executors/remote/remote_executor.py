import base64

# necessary for making RSA import work TODO: figure out if this can be removed
from Crypto.IO import PEM  # pylint: disable=redefined-builtin, unused-import

from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_binary_format import RsaEncryptedAesPackage, AesEncryptedPackage
from biolib.biolib_logging import logger
from biolib.compute_node.job_worker.executors.types import RemoteExecuteOptions
from biolib.compute_node.job_worker.executors.remote.nitro_enclave_utils import NitroEnclaveUtils


class RemoteExecutor:

    @staticmethod
    def execute_job(options: RemoteExecuteOptions, module_input_serialized: bytes) -> bytes:
        job_id = options['job']['public_id']
        cloud_job = BiolibJobApi.create_cloud_job(module_name='main', job_id=job_id)
        logger.debug(f"Cloud: Job created with id {cloud_job['public_id']}")
        node_url = cloud_job['compute_node_info']['url']
        aes_key_buffer = None
        if 'attestation_document_base64' in cloud_job['compute_node_info']:
            attestation_document_bytes = base64.b64decode(cloud_job['compute_node_info']['attestation_document_base64'])
            expected_pcrs_and_aws_cert = BiolibJobApi.get_enclave_json(options['biolib_base_url'])

            rsa_public_key_der = NitroEnclaveUtils().attest_enclave_and_get_rsa_public_key(
                expected_pcrs_and_aws_cert,
                attestation_document_bytes,
            )
            serialized_data_to_send, aes_key_buffer = RsaEncryptedAesPackage().create(
                rsa_public_key_der,
                module_input_serialized,
            )
        else:
            serialized_data_to_send = module_input_serialized

        BiolibJobApi.start_cloud_job(job_id, serialized_data_to_send, node_url)
        BiolibJobApi.await_compute_node_status(
            compute_type='Cloud',
            node_url=node_url,
            retry_interval_seconds=1.5,
            retry_limit_minutes=30,
            status_to_await='Result Ready',
            aes_key_buffer=aes_key_buffer,
            job=options['job']
        )
        compute_result = BiolibJobApi.get_cloud_result(job_id, node_url)

        if 'attestation_document_base64' in cloud_job['compute_node_info']:
            serialized_module_output: bytes = AesEncryptedPackage(compute_result).decrypt(aes_key_buffer)
        else:
            serialized_module_output = compute_result
        return serialized_module_output
