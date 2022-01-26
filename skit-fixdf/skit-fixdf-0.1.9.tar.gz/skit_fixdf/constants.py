DEBUG_METADATA = "debug_metadata"
STATE = "state"
TYPE = "type"
SUB_TYPE = "sub_type"
AUDIO = "audio"
CONVERSATION_UUID = "conversation_uuid"
CALL_UUID = "call_uuid"
CALL_AUDIO = "call_audio"
CREATED_AT = "created_at"
END_STATE = "end_state"
FLOW_VERSION = "flow_version"
IS_REPORTED = "is_reported"
LANGUAGE_CODE = "language_code"
VIRTUAL_NUMBER = "virtual_number"
CALL_DURATION = "call_duration"
BOT = "bot"
CURRENT_INTENT = "current_intent"
AUDIO_URL = "audio_url"
PREDICTED_INTENT = "predicted_intent"
PREDICTION = "prediction"
USER = "user"
VIVA_CALL_DURATION = "viva_call_duration"
COLUMNS = "columns"

DATA = "data"
DATA_ID = "data_id"
ID = "id"
NAME = "name"
INTENT = "intent"
INTENTS = f"{INTENT}s"
SLOTS = "slots"
VALUES = "values"
ENTITIES = "entities"
TEXT = "text"
BODY = "body"
TYPE = "type"
ENTITY_TYPE = "entity_type"
TRANSCRIPTION = "transcription"
SCORE = "score"
VALUE = "value"
STATE_TRANSITIONS = "state_transitions"
METADATA = "metadata"
ASR_PROVIDER = "asr_provider"
UTTERANCES = "utterances"
PLUTE_REQUEST = "plute_request"
ALTERNATIVES = "alternatives"
REFTIME = "reftime"
TAG = "tag"
TYPE = "type"
RAW = "raw"
IS_GOLD = "is_gold"
CALL_ID = "call_id"
CONVERSATION_ID = "conversation_id"


REQUIRED_COLS_FOR_CALLS = [
    # Identifiers
    CONVERSATION_UUID,
    CALL_UUID,
    REFTIME,
    # audio url
    CALL_AUDIO,
    AUDIO_URL,
    # flow params
    FLOW_VERSION,
    STATE,
    END_STATE,
    IS_REPORTED,
    LANGUAGE_CODE,
    VIRTUAL_NUMBER,
    STATE_TRANSITIONS,
    CALL_DURATION,
    # slu metadata
    UTTERANCES,
    CURRENT_INTENT,
    PREDICTION,
    INTENT,
    ENTITIES,
    BOT,
    USER,
]

LABEL_COLS_FROM_METADATA = [
    CALL_UUID,
    CONVERSATION_UUID,
    (CALL_ID, CALL_UUID),
    (CONVERSATION_ID, CONVERSATION_UUID),
    STATE,
    AUDIO_URL,
    ALTERNATIVES,
    REFTIME,
    PREDICTION,
    INTENT,
    ENTITIES,
    LANGUAGE_CODE,
]

SUPPORTED_SUB_TYPES = lambda l: [v for v in l if v.lower() != AUDIO]

LOCALE = "locale"
TIMEZONE = "tz"
DIMS = "dims"
LATENT = "latent"
DATE = "date"
TIME = "time"
DATETIME = "datetime"
NUMBER = "number"
DURATION = "duration"
SUPPORTED_ENTITIES = [DATE, TIME, DATETIME, NUMBER, DURATION]
DATASET_TYPE__INTENT = "intent"
DATASET_TYPE__ENTITY = "entity"
DATASET_TYPE__TRANSCRIPTION = "transcription"
SUPPORTED_DATASET_TYPES = [
    DATASET_TYPE__TRANSCRIPTION,
    DATASET_TYPE__INTENT,
    DATASET_TYPE__ENTITY,
]
TO = "to"
FROM = "from"
DIM = "dim"
DURATION = "duration"
SECOND = "second"
NORMALIZED = "normalized"
DUCKLING_SERVICE_URL = "DUCKLING_SERVICE_URL"
UNIT = "unit"
CALLS = "calls"
LABELS = "labels"
INNER = "inner"
