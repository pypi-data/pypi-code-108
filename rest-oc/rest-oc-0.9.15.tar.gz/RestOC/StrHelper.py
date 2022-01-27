# coding=utf8
""" StrHelper Module

Several useful helper methods for use with strings
"""

__author__ = "Chris Nasr"
__copyright__ = "OuroborosCoding"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2018-11-11"

# Python imports
from base64 import b64encode, b64decode
from random import randint

# The sets available for the random function
_mdRandomSets = {
	"0x":	"0123456789abcdef",
	"0":	"01234567",
	"10":	"0123456789",
	"10*":  "123456789",
	"az":	"abcdefghijklmnopqrstuvwxyz",
	"az*":	"abcdefghijkmnopqrstuvwxyz",
	"AZ":	"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"AZ*":	"ABCDEFGHJKLMNPQRSTUVWXYZ",
	"aZ":	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"aZ*":	"abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
	"!":	"!@#$%^&*-_+.?",
	"!*":	"!@$^*-_."
}

def decrypt(key, val):
	"""Decrypt

	Decrypts a string using the key and returns it. Key must be in multiples of
	16 bytes

	Arguments:
		key (str): A key that was used to encrypt the original value
		val (str): The value to decrypt

	Returns:
		str
	"""

	# Load PyCrypto
	try:
		from Cryptodome.Cipher import AES
	except Exception as e:
		print('%s\n' % str(e))
		return None

	# base64 decode the value; this can explode because of padding errors
	try: val = b64decode(val)
	except TypeError: return None

	# Recreate the IV
	sIV = val[:16]

	# Strip out the IV from the encrypted value
	val = val[16:]

	# Create the cipher and store the decrypted value
	oC = AES.new(key, AES.MODE_CFB, sIV, segment_size=128)

	# Return the decrypted value
	return oC.decrypt(val)

def digits(val):
	"""Digits

	Returns only the digits in the string

	Arguments:
		val (str): The string to strip all non-digit characters from

	Returns:
		str
	"""

	# Init list of valid characters
	lRet = []

	# Go through each character in the string and only keep it if it's a digit
	for c in val:
		if c.isdigit():
			lRet.append(c)

	# Return the new string
	return ''.join(lRet)

def encrypt(key, val):
	"""Encrypt

	Encrypts a string using the passed key and returns it. Key must be in
	multiples of 16 bytes

	Arguments:
		key (str): The key used to encrypt the value
		val (str): The value to encrypt and return

	Returns:
		str
	"""

	# Try to load PyCrypto
	try:
		from Crypto import Random
		from Cryptodome.Cipher import AES
	except Exception as e:
		print('%s\n' % str(e))
		return None

	# Generate an IV
	sIV = Random.new().read(AES.block_size)

	# Create a new cipher using the key and the IV
	oC = AES.new(key, AES.MODE_CFB, sIV, segment_size=128)

	# Encrypt the value
	val = oC.encrypt(val)

	# Add the IV
	val = '%s%s' % (sIV, val)

	# Return the entire thing as a base 64 encoded string
	return b64encode(val)

def normalize(val):
	"""Normalize

	Replaces all special alpha characters with their ascii equivalent

	Args:
		val (str): The text to normalize

	Returns:
		str
	"""
	return strtr(val, {
		'Ъ': "'", 'ъ': "'", 'Ь': "'", 'ь': "'",

		'Á': 'A', 'Ă': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ằ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
		'Ǎ': 'A', 'Â': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ầ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
		'Ä': 'A', 'Ǟ': 'A', 'Ȧ': 'A', 'Ǡ': 'A', 'Ạ': 'A', 'Ȁ': 'A', 'À': 'A',
		'Ả': 'A', 'Ȃ': 'A', 'Ā': 'A', 'Ą': 'A', 'Å': 'A', 'Ǻ': 'A', 'Ḁ': 'A',
		'Ⱥ': 'A', 'Ã': 'A', 'Ɐ': 'A', 'ᴀ': 'A',
		 'á': 'a', 'ă': 'a', 'ắ': 'a', 'ặ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a',
		 'ǎ': 'a', 'â': 'a', 'ấ': 'a', 'ậ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a',
		 'ä': 'a', 'ǟ': 'a', 'ȧ': 'a', 'ǡ': 'a', 'ạ': 'a', 'ȁ': 'a', 'à': 'a',
		 'ả': 'a', 'ȃ': 'a', 'ā': 'a', 'ą': 'a', 'ᶏ': 'a', 'ẚ': 'a', 'å': 'a',
		 'ǻ': 'a', 'ḁ': 'a', 'ⱥ': 'a', 'ã': 'a', 'ɐ': 'a', 'ₐ': 'a', 'А': 'a',
		 'а': 'a',

		'Ꜳ': 'AA', 'Æ': 'AE', 'Ǽ': 'AE', 'Ǣ': 'AE', 'ᴁ': 'AE', 'Ꜵ': 'AO',
		'Ꜷ': 'AU', 'Ꜹ': 'AV', 'Ꜻ': 'AV', 'Ꜽ': 'AY',
		'ꜳ': 'aa', 'æ': 'ae', 'ǽ': 'ae', 'ǣ': 'ae', 'ᴂ': 'ae', 'ꜵ': 'ao',
		'ꜷ': 'au', 'ꜹ': 'av', 'ꜻ': 'av', 'ꜽ': 'ay',

		'Ḃ': 'B', 'Ḅ': 'B', 'Ɓ': 'B', 'Ḇ': 'B', 'Ƀ': 'B', 'Ƃ': 'B', 'ʙ': 'B',
		'ᴃ': 'B', 'Б': 'B',
		'ḃ': 'b', 'ḅ': 'b', 'ɓ': 'b', 'ḇ': 'b', 'ᵬ': 'b', 'ᶀ': 'b', 'ƀ': 'b',
		'ƃ': 'b', 'б': 'b',

		'Ć': 'C', 'Č': 'C', 'Ç': 'C', 'Ḉ': 'C', 'Ĉ': 'C', 'Ċ': 'C', 'Ƈ': 'C',
		'Ȼ': 'C', 'Ꜿ': 'C', 'ᴄ': 'C',
		'ć': 'c', 'č': 'c', 'ç': 'c', 'ḉ': 'c', 'ĉ': 'c', 'ɕ': 'c', 'ċ': 'c',
		'ƈ': 'c', 'ȼ': 'c', 'ↄ': 'c', 'ꜿ': 'c',

		'Ч': 'CH',
		'ч': 'ch',

		'Ď': 'D', 'Ḑ': 'D', 'Ḓ': 'D', 'Ḋ': 'D', 'Ḍ': 'D', 'Ɗ': 'D', 'Ḏ': 'D',
		'ǲ': 'D', 'ǅ': 'D', 'Đ': 'D', 'Ƌ': 'D', 'Ꝺ': 'D', 'ᴅ': 'D', 'Д': 'D',
		'ď': 'd', 'ḑ': 'd', 'ḓ': 'd', 'ȡ': 'd', 'ḋ': 'd', 'ḍ': 'd', 'ɗ': 'd',
		'ᶑ': 'd', 'ḏ': 'd', 'ᵭ': 'd', 'ᶁ': 'd', 'đ': 'd', 'ɖ': 'd', 'ƌ': 'd',
		'ꝺ': 'd', 'д': 'd',

		'Ǳ': 'DZ', 'Ǆ': 'DZ',
		'ǳ': 'dz', 'ǆ': 'dz',

		'É': 'E', 'Ĕ': 'E', 'Ě': 'E', 'Ȩ': 'E', 'Ḝ': 'E', 'Ê': 'E', 'Ế': 'E',
		'Ệ': 'E', 'Ề': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ḙ': 'E', 'Ë': 'E', 'Ė': 'E',
		'Ẹ': 'E', 'Ȅ': 'E', 'È': 'E', 'Ẻ': 'E', 'Ȇ': 'E', 'Ē': 'E', 'Ḗ': 'E',
		'Ḕ': 'E', 'Ę': 'E', 'Ɇ': 'E', 'Ẽ': 'E', 'Ḛ': 'E', 'Ɛ': 'E', 'Ǝ': 'E',
		'ᴇ': 'E', 'ⱻ': 'E', 'Е': 'E', 'Э': 'E',
		'é': 'e', 'ĕ': 'e', 'ě': 'e', 'ȩ': 'e', 'ḝ': 'e', 'ê': 'e', 'ế': 'e',
		'ệ': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ḙ': 'e', 'ë': 'e', 'ė': 'e',
		'ẹ': 'e', 'ȅ': 'e', 'è': 'e', 'ẻ': 'e', 'ȇ': 'e', 'ē': 'e', 'ḗ': 'e',
		'ḕ': 'e', 'ⱸ': 'e', 'ę': 'e', 'ᶒ': 'e', 'ɇ': 'e', 'ẽ': 'e', 'ḛ': 'e',
		'ɛ': 'e', 'ᶓ': 'e', 'ɘ': 'e', 'ǝ': 'e', 'ₑ': 'e', 'е': 'e', 'э': 'e',

		'Ꝫ': 'ET',
		'ꝫ': 'et',

		'Ḟ': 'F', 'Ƒ': 'F', 'Ꝼ': 'F', 'ꜰ': 'F', 'Ф': 'F',
		'ḟ': 'f', 'ƒ': 'f', 'ᵮ': 'f', 'ᶂ': 'f', 'ꝼ': 'f', 'ф': 'f',

		'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬁ': 'fi', 'ﬂ': 'fl',

		'Ǵ': 'G', 'Ğ': 'G', 'Ǧ': 'G', 'Ģ': 'G', 'Ĝ': 'G', 'Ġ': 'G', 'Ɠ': 'G',
		'Ḡ': 'G', 'Ǥ': 'G', 'Ᵹ': 'G', 'ɢ': 'G', 'ʛ': 'G', 'Г': 'G',
		'ǵ': 'g', 'ğ': 'g', 'ǧ': 'g', 'ģ': 'g', 'ĝ': 'g', 'ġ': 'g', 'ɠ': 'g',
		'ḡ': 'g', 'ᶃ': 'g', 'ǥ': 'g', 'ᵹ': 'g', 'ɡ': 'g', 'ᵷ': 'g', 'г': 'g',

		'Ḫ': 'H', 'Ȟ': 'H', 'Ḩ': 'H', 'Ĥ': 'H', 'Ⱨ': 'H', 'Ḧ': 'H', 'Ḣ': 'H',
		'Ḥ': 'H', 'Ħ': 'H', 'ʜ': 'H', 'Х': 'H',
		'ḫ': 'h', 'ȟ': 'h', 'ḩ': 'h', 'ĥ': 'h', 'ⱨ': 'h', 'ḧ': 'h', 'ḣ': 'h',
		'ḥ': 'h', 'ɦ': 'h', 'ẖ': 'h', 'ħ': 'h', 'ɥ': 'h', 'ʮ': 'h', 'ʯ': 'h',
		'х': 'h',

		'ƕ': 'hv',

		'Í': 'I', 'Ĭ': 'I', 'Ǐ': 'I', 'Î': 'I', 'Ï': 'I', 'Ḯ': 'I', 'İ': 'I',
		'Ị': 'I', 'Ȉ': 'I', 'Ì': 'I', 'Ỉ': 'I', 'Ȋ': 'I', 'Ī': 'I', 'Į': 'I',
		'Ɨ': 'I', 'Ĩ': 'I', 'Ḭ': 'I', 'ɪ': 'I', 'Й': 'I', 'Ы': 'I', 'И': 'I',
		'ı': 'i', 'í': 'i', 'ĭ': 'i', 'ǐ': 'i', 'î': 'i', 'ï': 'i', 'ḯ': 'i',
		'ị': 'i', 'ȉ': 'i', 'ì': 'i', 'ỉ': 'i', 'ȋ': 'i', 'ī': 'i', 'į': 'i',
		'ᶖ': 'i', 'ɨ': 'i', 'ĩ': 'i', 'ḭ': 'i', 'ᴉ': 'i', 'ᵢ': 'i', 'й': 'i',
		'ы': 'i', 'и': 'i',

		'Ĳ': 'IJ', 'Ꝭ': 'IS',
		'ĳ': 'ij', 'ꝭ': 'is',

		'Ĵ': 'J', 'Ɉ': 'J', 'ᴊ': 'J',
		'ȷ': 'j', 'ɟ': 'j', 'ʄ': 'j', 'ǰ': 'j', 'ĵ': 'j', 'ʝ': 'j', 'ɉ': 'j',
		'ⱼ': 'j',

		'Ḱ': 'K', 'Ǩ': 'K', 'Ķ': 'K', 'Ⱪ': 'K', 'Ꝃ': 'K', 'Ḳ': 'K', 'Ƙ': 'K',
		'Ḵ': 'K', 'Ꝁ': 'K', 'Ꝅ': 'K', 'ᴋ': 'K', 'К': 'K',
		'ḱ': 'k', 'ǩ': 'k', 'ķ': 'k', 'ⱪ': 'k', 'ꝃ': 'k', 'ḳ': 'k', 'ƙ': 'k',
		'ḵ': 'k', 'ᶄ': 'k', 'ꝁ': 'k', 'ꝅ': 'k', 'ʞ': 'k', 'к': 'k',

		'Ĺ': 'L', 'Ƚ': 'L', 'Ľ': 'L', 'Ļ': 'L', 'Ḽ': 'L', 'Ḷ': 'L', 'Ḹ': 'L',
		'Ⱡ': 'L', 'Ꝉ': 'L', 'Ḻ': 'L', 'Ŀ': 'L', 'Ɫ': 'L', 'ǈ': 'L', 'Ł': 'L',
		'Ꞁ': 'L', 'ʟ': 'L', 'ᴌ': 'L', 'Л': 'L',
		'ĺ': 'l', 'ƚ': 'l', 'ɬ': 'l', 'ľ': 'l', 'ļ': 'l', 'ḽ': 'l', 'ȴ': 'l',
		'ḷ': 'l', 'ḹ': 'l', 'ⱡ': 'l', 'ꝉ': 'l', 'ḻ': 'l', 'ŀ': 'l', 'ɫ': 'l',
		'ᶅ': 'l', 'ɭ': 'l', 'ł': 'l', 'ꞁ': 'l', 'л': 'l',

		'Ǉ': 'LJ',
		'ǉ': 'lj',

		'Ḿ': 'M', 'Ṁ': 'M', 'Ṃ': 'M', 'Ɱ': 'M', 'Ɯ': 'M', 'ᴍ': 'M', 'М': 'M',
		'ḿ': 'm', 'ṁ': 'm', 'ṃ': 'm', 'ɱ': 'm', 'ᵯ': 'm', 'ᶆ': 'm', 'ɯ': 'm',
		'ɰ': 'm', 'м': 'm',

		'Ń': 'N', 'Ň': 'N', 'Ņ': 'N', 'Ṋ': 'N', 'Ṅ': 'N', 'Ṇ': 'N', 'Ǹ': 'N',
		'Ɲ': 'N', 'Ṉ': 'N', 'Ƞ': 'N', 'ǋ': 'N', 'Ñ': 'N', 'ɴ': 'N', 'ᴎ': 'N',
		'Н': 'N',
		'ń': 'n', 'ň': 'n', 'ņ': 'n', 'ṋ': 'n', 'ȵ': 'n', 'ṅ': 'n', 'ṇ': 'n',
		'ǹ': 'n', 'ɲ': 'n', 'ṉ': 'n', 'ƞ': 'n', 'ᵰ': 'n', 'ᶇ': 'n', 'ɳ': 'n',
		'ñ': 'n', 'н': 'n',

		'Ǌ': 'NJ',
		'ǌ': 'nj',

		'Ó': 'O', 'Ŏ': 'O', 'Ǒ': 'O', 'Ô': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ồ': 'O',
		'Ổ': 'O', 'Ỗ': 'O', 'Ö': 'O', 'Ȫ': 'O', 'Ȯ': 'O', 'Ȱ': 'O', 'Ọ': 'O',
		'Ő': 'O', 'Ȍ': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Ơ': 'O', 'Ớ': 'O', 'Ợ': 'O',
		'Ờ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ȏ': 'O', 'Ꝋ': 'O', 'Ꝍ': 'O', 'Ō': 'O',
		'Ṓ': 'O', 'Ṑ': 'O', 'Ɵ': 'O', 'Ǫ': 'O', 'Ǭ': 'O', 'Ø': 'O', 'Ǿ': 'O',
		'Õ': 'O', 'Ṍ': 'O', 'Ṏ': 'O', 'Ȭ': 'O', 'Ɔ': 'O', 'ᴏ': 'O', 'ᴐ': 'O',
		'О': 'O',
		'ɵ': 'o', 'ó': 'o', 'ŏ': 'o', 'ǒ': 'o', 'ô': 'o', 'ố': 'o', 'ộ': 'o',
		'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ö': 'o', 'ȫ': 'o', 'ȯ': 'o', 'ȱ': 'o',
		'ọ': 'o', 'ő': 'o', 'ȍ': 'o', 'ò': 'o', 'ỏ': 'o', 'ơ': 'o', 'ớ': 'o',
		'ợ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ȏ': 'o', 'ꝋ': 'o', 'ꝍ': 'o',
		'ⱺ': 'o', 'ō': 'o', 'ṓ': 'o', 'ṑ': 'o', 'ǫ': 'o', 'ǭ': 'o', 'ø': 'o',
		'ǿ': 'o', 'õ': 'o', 'ṍ': 'o', 'ṏ': 'o', 'ȭ': 'o', 'ɔ': 'o', 'ᶗ': 'o',
		'ᴑ': 'o', 'ᴓ': 'o', 'ₒ': 'o', 'о': 'o',

		'Œ': 'OE', 'ɶ': 'OE', 'Ƣ': 'OI', 'Ꝏ': 'OO', 'Ȣ': 'OU', 'ᴕ': 'OU',
		'ᴔ': 'oe', 'œ': 'oe', 'ƣ': 'oi', 'ꝏ': 'oo', 'ȣ': 'ou',

		'Ṕ': 'P', 'Ṗ': 'P', 'Ꝓ': 'P', 'Ƥ': 'P', 'Ꝕ': 'P', 'Ᵽ': 'P', 'Ꝑ': 'P',
		'ᴘ': 'P', 'П': 'P',
		'ṕ': 'p', 'ṗ': 'p', 'ꝓ': 'p', 'ƥ': 'p', 'ᵱ': 'p', 'ᶈ': 'p', 'ꝕ': 'p',
		'ᵽ': 'p', 'ꝑ': 'p', 'п': 'p',

		'Ꝙ': 'Q', 'Ꝗ': 'Q',
		'ꝙ': 'q', 'ʠ': 'q', 'ɋ': 'q', 'ꝗ': 'q',

		'Ꞃ': 'R', 'Ŕ': 'R', 'Ř': 'R', 'Ŗ': 'R', 'Ṙ': 'R', 'Ṛ': 'R', 'Ṝ': 'R',
		'Ȑ': 'R', 'Ȓ': 'R', 'Ṟ': 'R', 'Ɍ': 'R', 'Ɽ': 'R', 'ʁ': 'R', 'ʀ': 'R',
		'ᴙ': 'R', 'ᴚ': 'R', 'Р': 'R',
		'ꞃ': 'r', 'ŕ': 'r', 'ř': 'r', 'ŗ': 'r', 'ṙ': 'r', 'ṛ': 'r', 'ṝ': 'r',
		'ȑ': 'r', 'ɾ': 'r', 'ᵳ': 'r', 'ȓ': 'r', 'ṟ': 'r', 'ɼ': 'r', 'ᵲ': 'r',
		'ᶉ': 'r', 'ɍ': 'r', 'ɽ': 'r', 'ɿ': 'r', 'ɹ': 'r', 'ɻ': 'r', 'ɺ': 'r',
		'ⱹ': 'r', 'ᵣ': 'r', 'р': 'r',

		'Ꞅ': 'S', 'Ś': 'S', 'Ṥ': 'S', 'Š': 'S', 'Ṧ': 'S', 'Ş': 'S', 'Ŝ': 'S',
		'Ș': 'S', 'Ṡ': 'S', 'Ṣ': 'S', 'Ṩ': 'S', 'ꜱ': 'S', 'С': 'S',
		'ꞅ': 's', 'ſ': 's', 'ẜ': 's', 'ẛ': 's', 'ẝ': 's', 'ś': 's', 'ṥ': 's',
		'š': 's', 'ṧ': 's', 'ş': 's', 'ŝ': 's', 'ș': 's', 'ṡ': 's', 'ṣ': 's',
		'ṩ': 's', 'ʂ': 's', 'ᵴ': 's', 'ᶊ': 's', 'ȿ': 's', 'с': 's',

		'Щ': 'SCH', 'Ш': 'SH',
		'щ': 'sch', 'ш': 'sh', 'ß': 'ss', 'ﬆ': 'st',

		'Ꞇ': 'T', 'Ť': 'T', 'Ţ': 'T', 'Ṱ': 'T', 'Ț': 'T', 'Ⱦ': 'T', 'Ṫ': 'T',
		'Ṭ': 'T', 'Ƭ': 'T', 'Ṯ': 'T', 'Ʈ': 'T', 'Ŧ': 'T', 'ᴛ': 'T', 'Т': 'T',
		'ꞇ': 't', 'ť': 't', 'ţ': 't', 'ṱ': 't', 'ț': 't', 'ȶ': 't', 'ẗ': 't',
		'ⱦ': 't', 'ṫ': 't', 'ṭ': 't', 'ƭ': 't', 'ṯ': 't', 'ᵵ': 't', 'ƫ': 't',
		'ʈ': 't', 'ŧ': 't', 'ʇ': 't', 'т': 't',

		'Ц': 'TS', 'Ꜩ': 'TZ',
		'ᵺ': 'th', 'ц': 'ts', 'ꜩ': 'tz',

		'Ú': 'U', 'Ŭ': 'U', 'Ǔ': 'U', 'Û': 'U', 'Ṷ': 'U', 'Ü': 'U', 'Ǘ': 'U',
		'Ǚ': 'U', 'Ǜ': 'U', 'Ǖ': 'U', 'Ṳ': 'U', 'Ụ': 'U', 'Ű': 'U', 'Ȕ': 'U',
		'Ù': 'U', 'Ủ': 'U', 'Ư': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ừ': 'U', 'Ử': 'U',
		'Ữ': 'U', 'Ȗ': 'U', 'Ū': 'U', 'Ṻ': 'U', 'Ų': 'U', 'Ů': 'U', 'Ũ': 'U',
		'Ṹ': 'U', 'Ṵ': 'U', 'ᴜ': 'U', 'У': 'U',
		'ᴝ': 'u', 'ú': 'u', 'ŭ': 'u', 'ǔ': 'u', 'û': 'u', 'ṷ': 'u', 'ü': 'u',
		'ǘ': 'u', 'ǚ': 'u', 'ǜ': 'u', 'ǖ': 'u', 'ṳ': 'u', 'ụ': 'u', 'ű': 'u',
		'ȕ': 'u', 'ù': 'u', 'ủ': 'u', 'ư': 'u', 'ứ': 'u', 'ự': 'u', 'ừ': 'u',
		'ử': 'u', 'ữ': 'u', 'ȗ': 'u', 'ū': 'u', 'ṻ': 'u', 'ų': 'u', 'ᶙ': 'u',
		'ů': 'u', 'ũ': 'u', 'ṹ': 'u', 'ṵ': 'u', 'ᵤ': 'u', 'у': 'u',

		'ᵫ': 'ue', 'ꝸ': 'um',

		'Ʌ': 'V', 'Ꝟ': 'V', 'Ṿ': 'V', 'Ʋ': 'V', 'Ṽ': 'V', 'ᴠ': 'V', 'В': 'V',
		'ʌ': 'v', 'ⱴ': 'v', 'ꝟ': 'v', 'ṿ': 'v', 'ʋ': 'v', 'ᶌ': 'v', 'ⱱ': 'v',
		'ṽ': 'v', 'ᵥ': 'v', 'в': 'v',

		'Ꝡ': 'VY',
		'ꝡ': 'vy',

		'Ẃ': 'W', 'Ŵ': 'W', 'Ẅ': 'W', 'Ẇ': 'W', 'Ẉ': 'W', 'Ẁ': 'W', 'Ⱳ': 'W',
		'ᴡ': 'W',
		'ʍ': 'w', 'ẃ': 'w', 'ŵ': 'w', 'ẅ': 'w', 'ẇ': 'w', 'ẉ': 'w', 'ẁ': 'w',
		'ⱳ': 'w', 'ẘ': 'w',

		'Ẍ': 'X', 'Ẋ': 'X',
		'ẍ': 'x', 'ẋ': 'x', 'ᶍ': 'x', 'ₓ': 'x',

		'Ý': 'Y', 'Ŷ': 'Y', 'Ÿ': 'Y', 'Ẏ': 'Y', 'Ỵ': 'Y', 'Ỳ': 'Y', 'Ƴ': 'Y',
		'Ỷ': 'Y', 'Ỿ': 'Y', 'Ȳ': 'Y', 'Ɏ': 'Y', 'Ỹ': 'Y', 'ʏ': 'Y',
		'ʎ': 'y', 'ý': 'y', 'ŷ': 'y', 'ÿ': 'y', 'ẏ': 'y', 'ỵ': 'y', 'ỳ': 'y',
		'ƴ': 'y', 'ỷ': 'y', 'ỿ': 'y', 'ȳ': 'y', 'ẙ': 'y', 'ɏ': 'y', 'ỹ': 'y',

		'Ё': 'YO', 'Ю': 'YU', 'Я': 'Ya',
		'я': 'ya', 'ё': 'yo', 'ю': 'yu',

		'Ź': 'Z', 'Ž': 'Z', 'Ẑ': 'Z', 'Ⱬ': 'Z', 'Ż': 'Z', 'Ẓ': 'Z', 'Ȥ': 'Z',
		'Ẕ': 'Z', 'Ƶ': 'Z', 'ᴢ': 'Z', 'З': 'Z',
		'ź': 'z', 'ž': 'z', 'ẑ': 'z', 'ʑ': 'z', 'ⱬ': 'z', 'ż': 'z', 'ẓ': 'z',
		'ȥ': 'z', 'ẕ': 'z', 'ᵶ': 'z', 'ᶎ': 'z', 'ʐ': 'z', 'ƶ': 'z', 'ɀ': 'z',
		'з': 'z',

		'Ж': 'ZH',
		'ж': 'zh'
	})

def random(length = 8, sets='_aZ', duplicates=True):
	"""Random

	Generates a random string. By default this function will generate an 8
	character string using lowercase letters with possible repeating characters

	Arguments:
		length (int): Requested length of the password
		sets (str|str[]): A list of names from the standard sets, a string
			starting with an underscore representing one named set, or any other
			string to be used as an array of characters to chose from. If you
			want certain characters to have a greater chance of appearing, use
			them more times, e.g. twice the 'A's, "AABC", or three times the
			'B's, "ABBBC". Make sure not to turn off duplicates for this to be
			effective
		duplicates (bool): Defaults to True, allowing characters to be used
			more than once

	Sets:
		0x:		0123456789abcdef
		0:		01234567
		10:		0123456789
		az:		abcdefghijklmnopqrstuvwxyz
		az*:	abcdefghijkmnopqrstuvwxyz
		AZ:		ABCDEFGHIJKLMNOPQRSTUVWXYZ
		AZ*:	ABCDEFGHJKLMNPQRSTUVWXYZ
		aZ:		abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
		aZ*:	abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
		!:		!@#$%^&*-_+.?
		!*:		!@$%^*-_.

	Examples:
		> random(8, '_0x')
		"baadbeef"

	Returns:
		str
	"""

	# If the sets are a list
	if isinstance(sets, list):

		# If there is no count
		if not sets:
			raise ValueError('sets must contain at least one set name')

		# Init the string to be used as the allowed characters
		sChars = ''

		# Go through the list
		for s in sets:

			# If the set doesn't exist
			if s not in _mdRandomSets:
				raise ValueError('%s is not a valid set' % s)

			# Else, add it to the allowed characters
			sChars += _mdRandomSets[s]

	# Else if we have a string
	elif isinstance(sets, str):

		# If it starts with an underscore
		if sets[0] == '_':

			# If the set doesn't exist
			if sets[1:] not in _mdRandomSets:
				raise ValueError('%s is not a valid set for %s' % (sets[1:], sys._getframe().f_code.co_name))

			# Else, set it to the allowed characters
			sChars = _mdRandomSets[sets[1:]]

		# Else, use the string as is
		else:
			sChars = sets

	else:
		raise ValueError('%s is not a valid value for sets argument of %s' % (str(sets), sys._getframe().f_code.co_name))

	# Init the return variable
	sText = '';

	# Count the number of characters we can use
	iCount = len(sChars)

	# Create a [length] of random character
	i = 0
	while i < length:
		sFound = sChars[randint(0, iCount - 1)]
		bDup = sText.find(sFound)

		if duplicates or bDup == -1:
			sText += sFound
			i += 1

	# Return the generated string
	return sText

def bytes_human(num, suffix='B'):
	"""Bytes Human

	Returns the size of bytes in the closest binary prefix so that they are
	clearly understood by humans

	Arguments:
		num (uint): The bytes to convert to human readable

	Returns:
		str
	"""

	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:

		if abs(num) < 1024.0:
			return "%3.1f%sB" % (num, unit)

		num /= 1024.0

	return "%.1fYiB" % num

def strtr(text, table):
	"""String Translate

	Port of PHP strtr (string translate)

	Args:
		text (str): The string to translate
		table (dict): The translation table

	Returns:
		str
	"""
	text = str(text)
	buff = []
	i = 0
	n = len(text)
	while i < n:
		for s, r in table.items():
			if text[i:len(s)+i] == s:
				buff.append(r)
				i += len(s)
				break
		else:
			buff.append(text[i])
			i += 1

	return ''.join(buff)
