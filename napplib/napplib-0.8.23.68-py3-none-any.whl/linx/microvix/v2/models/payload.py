from lxml import objectify as xml, etree

class MicrovixPayload:

	def __init__(self, user: str, password: str, key: str, cnpj: str):
		E = xml.ElementMaker(annotate=False)

		self.__parameters = E.Parameters()

		self['chave'] = key
		self['cnpjEmp'] = cnpj

		self.__command = E.Command()

		authentication = E.Authentication()
		authentication.set('user', user)
		authentication.set('password', password)

		self.__linx_microvix = E.LinxMicrovix()
		self.__linx_microvix.append(authentication)
		self.__linx_microvix.append(self.__command)

	def setCommandName(self, name):
		self.__command.Name = xml.DataElement(name, nsmap='', _pytype='')

	def __str__(self):
		self.__command.append(self.__parameters)
		string =  etree.tostring(self.__linx_microvix, pretty_print=True, xml_declaration=True, encoding='utf-8').decode()

		return string 

	def __setitem__(self, name, value):
		parameter = xml.StringElement(str(value) if value else 'NULL')
		parameter.set('id', name)

		self.__parameters.addattr('Parameter', parameter)
