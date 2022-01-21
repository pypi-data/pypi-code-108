import re

FIXTURE_RE = re.compile(r'//\s*fixture\s*:\s*(\[[^]]+]|-)?\s*(\w+(?:\s*,\s*\w+)*)?', flags=re.IGNORECASE)


def get_fields(names, fields):
	for x in fields:
		if x['name'] in names:
			x['fixture'] = 1
	field_map = {x['name']: x for x in fields}
	return [field_map[x] for x in names]


class Column(dict):
	def __str__(self):
		return self["Name"]


class List(list):
	def __str__(self):
		return 'And'.join(map(str, self))


class Comment(str):
	def __str__(self):
		return '\n// '.join(self.split("\n"))


class Table(dict):
	def __init__(self, *args, **kw):
		super(Table, self).__init__(*args, **kw)
		if "primaryKey" in self:
			self["primaryKey"] = List(map(Column, self["primaryKey"]))
		if "indexes" in self:
			for x in self["indexes"]:
				x["fields"] = List(map(Column, x["fields"]))
		if "comment" in self:
			self["comment"] = Comment(self["comment"])
		if 'docs' in self:
			for x in self.__getitem__('docs'):
				m = FIXTURE_RE.match(x)
				if m:
					if m[1] == '-':
						self['fixture'] = None
					elif m[1] is None:
						var_names = re.split(r'\s*,\s*', m[2]) if m[2] else []
						self['fixture'] = {
							'fields': get_fields(var_names, self['fields']),
						}
