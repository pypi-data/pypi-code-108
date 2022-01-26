


from .LicenseInfo import LicenseInfo




class AvailableLicenseList(object):

	__LICENSES = [
		LicenseInfo(
			bIsFreeSoftware = False,
			bIsNamedLicense = False,
			shortLicenseName = "Proprietary",
			longLicenseName = None,
			licenseCopyrightOwner = None,
			versions = None,
			url = None,
			fullText = [
				"Copyright {{$YEAR}} by {{$COPYRIGHTHOLDER}}",
				"This software is genuine work created by {{$COPYRIGHTHOLDER}}. Distribution of source code, object code or any associated files of this work is generally prohibited.",
				"For licensing details see EULA.txt or LICENSE.txt."
			]),
		LicenseInfo(
			bIsFreeSoftware = False,
			bIsNamedLicense = False,
			shortLicenseName = "Scientific",
			longLicenseName = None,
			licenseCopyrightOwner = None,
			versions = None,
			url = None,
			fullText = [
				"Copyright {{$YEAR}} by {{$COPYRIGHTHOLDER}}",
				"This software is genuine work created by {{$COPYRIGHTHOLDER}}. Permission is hereby granted to run, copy and archive this software (source code and object code) and associated documentation files (the \"Software\") in scientific context (and scientific context only).",
				"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
			]),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "AGPL",
			longLicenseName = "GNU Affero General Public License",
			licenseCopyrightOwner = "Free Software Foundation",
			versions = "3+",
			url = "https://www.gnu.org/licenses/agpl-3.0.en.html"),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "GPL",
			longLicenseName = "GNU General Public License",
			licenseCopyrightOwner = "Free Software Foundation",
			versions = "3+",
			url = "https://www.gnu.org/licenses/gpl-3.0.en.html"),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "LGPL",
			longLicenseName = "GNU Lesser General Public License",
			licenseCopyrightOwner = "Free Software Foundation",
			versions = "3+",
			url = "https://www.gnu.org/licenses/lgpl-3.0.en.html"),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "Apache",
			longLicenseName = "Apache Software License",
			licenseCopyrightOwner = "Apache Software Foundation",
			versions = "2",
			url = "https://www.apache.org/licenses/LICENSE-2.0"),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "MPL",
			longLicenseName = "Mozilla Public License",
			licenseCopyrightOwner = "Mozilla Foundation",
			versions = "2",
			url = "https://www.apache.org/licenses/MPL-2.0"),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "MIT",
			longLicenseName = "MIT License",
			licenseCopyrightOwner = "Massachusetts Institute of Technology",
			url = "https://opensource.org/licenses/MIT",
			fullText = [
				"Copyright {{$YEAR}} by {{$COPYRIGHTHOLDER}}",
				"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:",
				"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.",
				"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
			]),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "BSD",
			longLicenseName = "Berkeley Software Distribution License",
			licenseCopyrightOwner = "University of California, Berkeley",
			url = "https://opensource.org/licenses/BSD-3-Clause",
			fullText = [
				"Copyright {{$YEAR}} by {{$COPYRIGHTHOLDER}}",
				"Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:",
				"1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.",
				"2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.",
				"3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.",
				"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
			]),
		LicenseInfo(
			bIsFreeSoftware = True,
			bIsNamedLicense = True,
			shortLicenseName = "FreeBSD",
			longLicenseName = "FreeBSD Berkeley Software Distribution License",
			licenseCopyrightOwner = "University of California, Berkeley",
			url = "https://opensource.org/licenses/BSD-2-Clause",
			fullText = [
				"Copyright {{$YEAR}} by {{$COPYRIGHTHOLDER}}",
				"Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:",
				"1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.",
				"2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.",
				"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
			]),
	]



	def __init__(self):
		self.__licenseInfos = {}

		for li in AvailableLicenseList.__LICENSES:
			if li is not None:
				self.__licenseInfos[li.id] = li
	#



	@property
	def ids(self):
		ids = list(self.__licenseInfos.keys())
		ids.sort()
		return ids
	#



	def getText(self, id, **kwargs):

		id = id.lower()
		li = self.__licenseInfos.get(id, None)
		if li is None:
			return None
		if len(kwargs) == 0:
			return li.toString()
		else:
			return li.toString(**kwargs)
	#



	def get(self, id):
		id = id.lower()
		li = self.__licenseInfos.get(id, None)
		if li is None:
			return None
		return li
	#



#





