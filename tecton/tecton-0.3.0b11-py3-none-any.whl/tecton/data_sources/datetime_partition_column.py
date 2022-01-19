import tecton_proto.data.batch_data_source_pb2 as batch_pb2
from tecton._internals import errors


# NOTE: When adding a new format, change data_source_helper.py:_partition_value_for_time if needed
class DatetimePartitionColumn:
    # pass zero_padded=True if the partition column is a string that is zero-padded
    def __init__(self, column_name, datepart, zero_padded):
        self.column_name = column_name
        self.datepart = datepart
        self.zero_padded = zero_padded

        datepart = datepart.lower()
        if datepart == "year":
            self.format_string = "%Y"
            self.minimum_seconds = 365 * 24 * 60 * 60
        elif datepart == "month":
            self.format_string = "%m"
            self.minimum_seconds = 28 * 24 * 60 * 60
        elif datepart == "day":
            self.format_string = "%d"
            self.minimum_seconds = 24 * 60 * 60
        elif datepart == "hour":
            self.format_string = "%H"
            self.minimum_seconds = 60 * 60
        elif datepart == "date":
            if not zero_padded:
                # we don't support non-zero-padded date strings because we use string comparison for them which would get broken
                raise errors.UNSUPPORTED_OPERATION(
                    "DatetimePartitionColumn for date with zero_padded=False", "Must have zero-padded=True"
                )
            self.format_string = "%Y-%m-%d"
            self.minimum_seconds = 24 * 60 * 60
        else:
            raise errors.UNSUPPORTED_OPERATION(
                "DatetimePartitionColumn with datepart=%s" % datepart,
                "Supported dateparts: year, month, day, hour, date",
            )
        if not zero_padded:
            self.format_string = self.format_string.replace("%", "%-")

    def _to_proto(self):
        proto = batch_pb2.DatetimePartitionColumn()
        proto.column_name = self.column_name
        proto.format_string = self.format_string
        proto.minimum_seconds = self.minimum_seconds
        return proto
