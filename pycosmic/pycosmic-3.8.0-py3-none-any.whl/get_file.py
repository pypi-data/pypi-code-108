import requests 



class SetCode:

	def __init__(self,repo=None,filename=None,user="rishabh-creator601",branch='main',newfilename=None,mode='wb'):

		self.user = user
		self.branch = branch
		self.repo = repo
		self.filename = filename 


		self.url = f"https://raw.githubusercontent.com/{self.user}/{self.repo}/{self.branch}/{self.filename}"

		self.start(repo,filename,user,branch,newfilename,mode)


	def start(self,repo,filename,user="rishabh-creator601",branch='main',newfilename=None,mode='wb'):
		if newfilename is not None:
			newfilename = newfilename
		else:
			newfilename = filename





		cont = requests.get(self.url)



		with open(newfilename,mode) as f:
			f.write(cont.content)
		f.close()

		print('File {} Loaded '.format(newfilename))









if __name__ == '__main__':
	SetCode(filename="data.json",repo="codes")


