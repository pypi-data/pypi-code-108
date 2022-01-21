from fact_explorer.config import get_logger, get_configuration

from typing import Any, List, Dict, Optional

log = get_logger("crypto_helpers")
configuration = get_configuration()

try:
    from cryptoshred.asynchronous.convenience import find_and_decrypt
    from cryptoshred.backends import KeyBackend, DynamoDbSsmBackend

    default_key_backend = DynamoDbSsmBackend(
        iv_param=configuration.cryptoshred_init_vector_path
    )

    async def decrypt_result(
        *, data: List[Dict[str, Any]], key_backend: Optional[KeyBackend] = None
    ) -> List[Dict[str, Any]]:
        log.debug("Decrypting data")
        if not key_backend:
            key_backend = default_key_backend
        result = []
        for item in data:
            decrypted = await find_and_decrypt(
                x=item["payload"], key_backend=key_backend
            )

            result.append({"header": item["header"], "payload": decrypted})

        return result

    async def cryptoshred_enabled() -> bool:
        return True

except ImportError:
    KeyBackend = None

    if configuration.cryptoshred_init_vector_path:
        log.warning(
            (
                "Cryptoshred configured but library not available"
                "Cryptoshredding related features will not be available."
            )
        )

    async def decrypt_result(
        *, data: List[Dict[str, Any]], key_backend: Optional[KeyBackend] = None
    ) -> List[Dict[str, Any]]:
        log.debug("Cryptoshred not installed returning raw data")
        return data

    async def cryptoshred_enabled() -> bool:
        return False
