class ValueEnum(object):
    NULL = 0
    BOOLEAN = 10
    DECIMAL = 20
    FLOAT = 30
    DOUBLE = 40

    DOUBLE_SUMMARY = 45
    LONG_SUMMARY = 46

    TEXT = 50
    TEXT_HASH = 51
    BLOB = 60
    IP4ADDR = 61

    LIST = 70

    ARRAY_INT = 71
    ARRAY_FLOAT = 72
    ARRAY_TEXT = 73
    ARRAY_LONG = 74

    MAP = 80

    @staticmethod
    def create(code):
        from whatap.value.blob_value import BlobValue
        from whatap.value.boolean_value import BooleanValue
        from whatap.value.decimal_value import DecimalValue
        from whatap.value.double_summary import DoubleSummary
        from whatap.value.double_value import DoubleValue
        from whatap.value.float_array import FloatArray
        from whatap.value.float_value import FloatValue
        from whatap.value.int_array import IntArray
        from whatap.value.ip4_value import IP4Value
        from whatap.value.list_value import ListValue
        from whatap.value.long_array import LongArray
        from whatap.value.long_summary import LongSummary
        from whatap.value.map_value import MapValue
        from whatap.value.null_value import NullValue
        from whatap.value.text_array import TextArray
        from whatap.value.text_hash_value import TextHashValue
        from whatap.value.text_value import TextValue

        if code is None:
            return NullValue()
        elif code == ValueEnum.BOOLEAN:
            return BooleanValue()
        elif code == ValueEnum.DECIMAL:
            return DecimalValue()
        elif code == ValueEnum.FLOAT:
            return FloatValue()
        elif code == ValueEnum.DOUBLE:
            return DoubleValue()
        elif code == ValueEnum.TEXT:
            return TextValue()
        elif code == ValueEnum.TEXT_HASH:
            return TextHashValue()
        elif code == ValueEnum.BLOB:
            return BlobValue()
        elif code == ValueEnum.IP4ADDR:
            return IP4Value()
        elif code == ValueEnum.LIST:
            return ListValue()
        elif code == ValueEnum.MAP:
            return MapValue()
        elif code == ValueEnum.LONG_SUMMARY:
            return LongSummary()
        elif code == ValueEnum.DOUBLE_SUMMARY:
            return DoubleSummary()
        elif code == ValueEnum.ARRAY_INT:
            return IntArray()
        elif code == ValueEnum.ARRAY_FLOAT:
            return FloatArray()
        elif code == ValueEnum.ARRAY_TEXT:
            return TextArray()
        elif code == ValueEnum.ARRAY_LONG:
            return LongArray()
        else:
            return None
