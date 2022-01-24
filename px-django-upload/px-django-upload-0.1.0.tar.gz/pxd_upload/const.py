import re


B = 1
KiB = 2**10 * B
MiB = 2**20 * B
GiB = 2**30 * B
TiB = 2**40 * B
PiB = 2**50 * B

UUID4_REGEXP = re.compile('^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$', re.I)
