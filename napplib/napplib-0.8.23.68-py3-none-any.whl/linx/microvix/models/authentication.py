from lxml import objectify as xml, etree

class MicrovixAuthentication:


	def __init__(self, user: str, password: str, key: str, cnpj: str):

		self.user     = user
		self.password = password
		self.key      = key.upper()
		self.cnpj     = cnpj

		E = xml.ElementMaker(annotate=False)

		self.__parameters = E.Parameters()

		self['chave'] = key
		self['cnpjEmp'] = cnpj

		self.__command = E.Command()

		authentication = E.Authentication()
		authentication.set('user', user)
		authentication.set('password', password)

		self.__linxMicrovix = E.LinxMicrovix()
		self.__linxMicrovix.append(authentication)
		self.__linxMicrovix.append(self.__command)


	def setCommandName(self, name):
		self.__command.Name = xml.DataElement(name, nsmap='', _pytype='')


	def __str__(self):

		self.__command.append(self.__parameters)
		string =  etree.tostring(self.__linxMicrovix, pretty_print=True, xml_declaration=True,encoding='utf-8').decode()

		return string 


	def __setitem__(self, name, value):

		parameter = xml.StringElement(str(value) if value is not None else 'NULL')
		parameter.set('id', name)

		self.__parameters.addattr('Parameter', parameter)


	def copy(self):
		return MicrovixAuthentication(
			self.user,
			self.password,
			self.key,
			self.cnpj
		)
