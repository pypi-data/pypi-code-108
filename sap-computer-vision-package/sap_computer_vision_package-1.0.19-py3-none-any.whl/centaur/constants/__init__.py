from centaur._.pyvmps.cfg.config import PyvmpProtocol


UNDERSCORE = "_"
CONTENT_TYPE = PyvmpProtocol.CONTENT_TYPE  # "content_type"


class TF:
    signature_name = "signature_name"
    inputs = "inputs"


class KwargsKeys:
    orig_parsed_usr_payload = "orig_parsed_usr_payload"
    orig_parsed_usr_payload_content_types = "orig_parsed_usr_payload_content_types"
    pre_processed_usr_payload = "pre_processed_usr_payload"
    pre_processed_kwargs = "pre_processed_kwargs"
