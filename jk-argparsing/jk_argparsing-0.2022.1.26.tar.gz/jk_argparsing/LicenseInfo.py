



class LicenseInfo(object):



	def __init__(self, bIsFreeSoftware = None, bIsNamedLicense = None, shortLicenseName = None, longLicenseName = None,
			licenseCopyrightOwner = None, versions = None, url = None, fullText = None):
		assert isinstance(bIsFreeSoftware, bool)
		assert isinstance(bIsNamedLicense, bool)
		assert isinstance(shortLicenseName, str)
		if bIsNamedLicense:
			assert isinstance(longLicenseName, str)
		if bIsNamedLicense:
			assert isinstance(licenseCopyrightOwner, str)
		if versions != None:
			assert isinstance(versions, str)
		if url != None:
			assert isinstance(url, str)
		if fullText != None:
			assert isinstance(fullText, list)
			for s in fullText:
				assert isinstance(s, str)

		self.isNamedLicense = bIsNamedLicense or bIsFreeSoftware
		self.isFreeSoftware = bIsFreeSoftware
		self.id = shortLicenseName.lower()
		self.shortLicenseName = shortLicenseName
		self.longLicenseName = longLicenseName
		self.licenseCopyrightOwner = licenseCopyrightOwner
		self.url = url
		self.newerVersionsAllowed = False
		if versions is None:
			self.version = None
		else:
			if versions.endswith("+"):
				self.newerVersionsAllowed = True
				versions = versions[:-1]
			self.version = int(versions)
		self.fullText = fullText
	#



	def __tostr(self, data):
		if isinstance(data, (tuple, list)):
			if len(data) == 0:
				return ""
			elif (len(data) == 2) and isinstance(data[0], int) and isinstance(data[1], int):
				return str(data[0]) + "-" + str(data[1])
			else:
				return ", ".join([ str(d) for d in data ])
		else:
			return str(data)
	#



	def toString(self, **kwargs):
		ret = []

		sb = ""

		if self.isFreeSoftware:
			sb += "This program is free software: you can redistribute it and/or modify it under the terms of the "
			sb += self.longLicenseName
		elif self.isNamedLicense:
			sb += "This program is distributed under the terms of the "
			sb += self.longLicenseName

		if self.isNamedLicense:
			sb += " as published by " + self.licenseCopyrightOwner

		if (self.version != None) and (self.version > 0):
			if self.newerVersionsAllowed:
				sb += " either version " + str(self.version) + " or later."
			else:
				sb += " in version " + str(self.version) + "."
		elif self.isNamedLicense:
			sb += "."

		if self.fullText is None:
			if (self.url != None) and (self.longLicenseName != None):
				sb += " For more details see the " + self.longLicenseName + ", which should be vailable at: "
				sb += self.url

		if sb:
			ret.append(sb)

		if self.fullText != None:
			textLines = self.fullText
			for key in kwargs:
				value = kwargs[key]
				skey = "{{$" + key + "}}"
				for i in range(0, len(textLines)):
					curlen = -1
					while True:
						curlen = len(textLines[i])
						textLines[i] = textLines[i].replace(skey, self.__tostr(value))
						if len(textLines[i]) == curlen:
							break
			ret.extend(textLines)

		return ret
	#



#



