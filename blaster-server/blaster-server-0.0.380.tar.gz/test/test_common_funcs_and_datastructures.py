

##verify multiple collection query works as expected
from blaster.common_funcs_and_datastructures import get_time_overlaps, retry
from datetime import datetime
from blaster.utils.data_utils import parse_string_to_units, parse_currency_string


def test_sanitized_dicts_list():
	from blaster.common_funcs_and_datastructures import SanitizedDict, SanitizedList
	sd = SanitizedDict(a="<a>", b="<b>")
	sd["c"] = "<c>"
	sd["d"] = {"e": "<e>", "f": "<f>"}

	for k, v in sd.items():
		print(k, v)
	for k, v in sd["d"].items():
		print(k, v)

	sl = SanitizedList(["<a>", "<b>"])
	sl.append({"c": "<c>", "d": "<d>"})
	sl.extend(["<e>", "<f>"])
	for i in sl:
		print(i)
	for k, v in sl[2].items():
		print(k, v)



print(
	get_time_overlaps(
		datetime(year=2021, month=10, day=1),
		datetime(year=2021, month=10, day=20),
		["Monday 10:30 - 12:30", "Tuesday 10:30 - 12:30"]
	)
)

print(
	get_time_overlaps(
		datetime(year=2021, month=10, day=1),
		datetime(year=2021, month=10, day=20),
		["5/12/2021 10:30 - 12:30"]
	)
)
print(
	get_time_overlaps(
		datetime(year=2021, month=10, day=1),
		datetime(year=2021, month=10, day=20),
		["5/10/2021 10:30 - 12:30"]
	)
)


@retry(10)
def can_retry():
	print("trying")
	raise Exception


#can_retry()



print(parse_string_to_units(".9 units"))

print(parse_string_to_units("0.9 units"))
print(parse_string_to_units("rs -1.9"))
print(parse_currency_string("INR 2000"))
