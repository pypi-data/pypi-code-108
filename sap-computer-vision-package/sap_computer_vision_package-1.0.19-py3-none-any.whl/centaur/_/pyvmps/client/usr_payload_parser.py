import re
import ujson

from io import BytesIO
from collections import defaultdict
from typing import List, Dict, Union, NamedTuple
from requests_toolbelt.multipart import decoder
from requests.structures import CaseInsensitiveDict

from centaur import constants as public_constants
from centaur._.pyvmps.cfg import constants
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.cfg.config import SupportedHTTPCodecs
from centaur._.pyvmps.models.tf import constants as tf_constants


_logger = get_logger(__name__)


class ParsedUsrPayload(NamedTuple):
    payload: Union[
        dict,
        list,
        bytes,
        "numpy.ndarray",  # <- _parse_npy + anonymous field
        "pandas.DataFrame",  # <- _parse_pd_feather or _prase_pd_parquet + anonymous field
    ]

    content_types: Dict[str, Union[str, list]] = {}


def parse_usr_payload(content: bytes, content_type: List[str], encoding: str = "utf-8") -> ParsedUsrPayload:
    _logger.debug("Content-Type=%s, encoding=%s", content_type, encoding)

    ct = [x.lower() for x in content_type]

    if "application/json" in ct:
        return ParsedUsrPayload(payload=_parse_json(content))

    multipart_ct = ""
    for x in ct:
        if "multipart/form-data; boundary=" in x:
            multipart_ct = x
            break

    if multipart_ct:
        parsed_payload, cts, tf_sig_name = {}, {}, ""
        multipart_data = decoder.MultipartDecoder(content, multipart_ct, encoding)
        part_counter = defaultdict(int)

        for p in multipart_data.parts:
            _logger.debug("multipart/form-data part headers=%s", p.headers)

            if len(p.content) == 0:
                raise ValueError("empty multipart/form-data part: {}".format(p.headers))

            cd_h = p.headers[b"Content-Disposition"]
            l_idx = cd_h.index(b'form-data; name="') + 17
            r_idx = cd_h.index(b'"', l_idx)
            name = cd_h[l_idx:r_idx].decode(encoding)

            # Note:
            #   tf_constants.SIGNATURE_NAME ('signature_name') needs to be treated as a reserved keyword,
            #   that is: it should only appear in the requests for tf models.
            if name == tf_constants.SIGNATURE_NAME:
                tf_sig_name = p.content.decode(encoding)
            else:
                if cts:
                    if name.startswith(public_constants.UNDERSCORE):
                        if public_constants.UNDERSCORE in cts:
                            raise ValueError(
                                "more than 1 anonymous field (key starts with '%s') is not allowed: %s"
                                % (public_constants.UNDERSCORE, name)
                            )
                        raise ValueError(
                            "using anonymous field (key starts with '%s') and named field (key not starts with '%s') together is not allowed"
                            % (public_constants.UNDERSCORE, public_constants.UNDERSCORE)
                        )
                    else:
                        if public_constants.UNDERSCORE in cts:
                            raise ValueError(
                                "using anonymous field (key starts with '%s') and named field (key not starts with '%s') together is not allowed"
                                % (public_constants.UNDERSCORE, public_constants.UNDERSCORE)
                            )

                part_counter[name] += 1

                ct_h = p.headers.get(b"Content-Type", b"")
                p_ct = p_ct_to_relay = ""
                p_v, as_list = p.content, False

                if ct_h:
                    p_ct = p_ct_to_relay = ct_h.decode(encoding)

                    as_list = constants.ContentTypes.AS_LIST in p_ct
                    if as_list:
                        _logger.warning(
                            "multipart/form-data part '%s' activated '%s' feature",
                            p.headers,
                            constants.ContentTypes.AS_LIST,
                        )

                        p_ct = p_ct.replace(constants.ContentTypes.AS_LIST, "")
                        p_ct_to_relay = [p_ct]

                    parser = _parsers.get(p_ct, None)
                    if parser:
                        p_v = parser(p.content)
                        p_ct_to_relay = [""] if as_list else ""

                    if as_list:
                        p_v = [p_v]

                if name.startswith(public_constants.UNDERSCORE):
                    cts[public_constants.UNDERSCORE] = p_ct_to_relay
                    parsed_payload = p_v
                else:
                    if part_counter[name] == 1:
                        cts[name] = p_ct_to_relay
                        parsed_payload[name] = p_v
                    elif part_counter[name] == 2:
                        cts[name] = [cts[name], p_ct_to_relay]
                        parsed_payload[name] = [parsed_payload[name], p_v]
                    else:
                        cts[name].append(p_ct_to_relay)
                        parsed_payload[name].append(p_v)

        filtered_cts = {k: v for k, v in cts.items() if not re.match("^[\[\]', ]*$", str(v))}

        if tf_sig_name:
            return ParsedUsrPayload(
                payload={tf_constants.SIGNATURE_NAME: tf_sig_name, tf_constants.INPUTS: parsed_payload},
                content_types=filtered_cts,
            )

        return ParsedUsrPayload(payload=parsed_payload, content_types=filtered_cts)

    return ParsedUsrPayload(payload=content)


def _parse_json(data):
    return ujson.loads(data)


def _parse_npy(data):
    import numpy as np

    v = np.load(BytesIO(data), allow_pickle=True)
    if not isinstance(v, np.ndarray):
        raise ValueError("payload is not a valid ndarray")
    return v


def _parse_npz(data):
    import numpy as np

    v = np.load(BytesIO(data), allow_pickle=True)
    if not isinstance(v, np.lib.npyio.NpzFile):
        raise ValueError("payload is not a valid 'np.lib.npyio.NpzFile'")
    d = {}
    for k in v.keys():
        d[k] = v[k]
    return d


def _parse_pd_feather(data):
    import pandas as pd

    return pd.read_feather(BytesIO(data))


def _prase_pd_parquet(data):
    import pandas as pd

    return pd.read_parquet(BytesIO(data))


_parsers = CaseInsensitiveDict(
    {
        SupportedHTTPCodecs.JSON.value: _parse_json,
        SupportedHTTPCodecs.NPY.value: _parse_npy,
        SupportedHTTPCodecs.NPZ.value: _parse_npz,
        SupportedHTTPCodecs.PD_FEATHER.value: _parse_pd_feather,
        SupportedHTTPCodecs.PD_PARQUET.value: _prase_pd_parquet,
    }
)
