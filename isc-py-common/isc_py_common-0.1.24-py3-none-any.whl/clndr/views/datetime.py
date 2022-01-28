# from datetime import datetime, time, timedelta
#
#
# class dateTime():
#
#     def __init__(self, value):
#         if isinstance(value, datetime):
#             self.value = datetime(
#                 year=value.year,
#                 month=value.month,
#                 day=value.day,
#                 hour=value.hour,
#                 minute=value.minute,
#                 second=value.second,
#                 microsecond=value.microsecond,
#                 tzinfo=value.tzinfo,
#                 fold=value.fold
#             )
#         elif isinstance(value, time):
#             self.value = time(
#                 fold=value.fold,
#                 hour=value.hour,
#                 minute=value.minute,
#                 second=value.second,
#                 microsecond=value.microsecond,
#             )
#
#     def __add__(self, other):
#         if isinstance(other, dateTime):
#             if isinstance(other.value, time):
#                 return self.value + timedelta(
#                     hours=other.value.hour,
#                     minutes=other.value.minute,
#                     seconds=other.value.second,
#                     microseconds=other.value.microsecond,
#                 )
#             elif isinstance(other.value, datetime):
#                 return self.value + other.value
#         elif isinstance(other, time):
#             if isinstance(other.value, time):
#                 return self.value + timedelta(
#                     hours=other.value.hour,
#                     minutes=other.value.minute,
#                     seconds=other.value.second,
#                     microseconds=other.value.microsecond,
#                 )
#             elif isinstance(other.value, datetime):
#                 return self.value + other.value
#
#     def __str__(self):
#         return str(self.value)
