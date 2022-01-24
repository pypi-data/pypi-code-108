import os ,sqlite3 ,glob ,json 



_all_ = ['find_db','DB','is_exist']


def find_db(extension='.db'):

	all_ = []

	for name in glob.glob(os.getcwd()+"/*"):
		if name.endswith(extension):
			all_.append(os.path.join(name))

	return all_



def is_exist(path):
	if os.path.exists(path):
		return True 
	else:
		return False


class DB:
	def __init__(self):
		self.table = None 


	def _db_(self,name):
		if name.endswith(".db"):
			self.db = sqlite3.connect(name)
			self.cur = self.db.cursor()
			return True

		else:
			return False

	def setTable(self,name):
		if name is not None:
			self.table = name 


	def run(self,cmd):
		self.cur.execute(cmd)



	def create_table(self,name,types=()):
		self.cur.execute(f'''CREATE TABLE {name}({types})''')
		return "Table Created "

	def show(self,table=None):
		if table is None and self.table is not None:
			all_ =  self.cur.execute(f"SELECT * FROM {self.table}").fetchall()
			return all_
		if table is not None:
			all_ =  self.cur.execute(f"SELECT * FROM {table}").fetchall()
			return all_

		else:
			return '''INSERT A TABLE NAME OR SET TABLE'''

		


	def add(self,tablename=None,values=()):
		if tablename is None and self.table is not None:
			self.cur.execute(f'''INSERT INTO {self.table} VALUES{values}''')
		if tablename is not None:
			self.cur.execute(f'''INSERT INTO {tablename} VALUES{values} ''')


	def commit(self):
		self.db.commit()





class JsonDB:
	def __init__(self):
		self.db = {}
		self.db_name= None 

	def connect(self,name):
		if is_exist(name) ==  True:
			data = self.load(name)
			self.db = self.load(name)
			self.db_name = name 
		else:
			self.commit(name,data={})


	def add(self,values={}):
		for k,v in values.items():
			self.db[k] = v 

		return "Done"

	def commit(self,name=None,data=None ):
		if name is None:
			name = self.db_name

		if data is None:
			data = self.db 
		with open(name,'w') as f:
			json.dump(data,f)

		return True 

			

	def load(self,name):
		if is_exist(name) ==  True:
			with open(name,'r') as f:
				data = json.load(f)

		return data 

	def show(self):
		return self.db 

	

if __name__ == '__main__':
	pass 
	







