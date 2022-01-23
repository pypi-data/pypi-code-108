import ctypes,os,datetime
def SystemMsgBox(icon,message,title,buttons): ctypes.windll.user32.MessageBoxW(icon, f"{message}", f"{title}", buttons)

def ReadFile(name): 
	pp = open(f"{name}","r")
	ppp = pp.read()
	pp.close()
	return ppp
def WriteFile(name,content): (open(f"{name}","w").write(f"{content}")).close()
def Write2File(name,content): (open(f"{name}","w").write(str(ReadFile(name)) + f"{content}")).close()
def Delete(fullPath): os.system(f"del {fullPath}")
def Send2Trash(fullPath): os.system("send2trash " + f"{fullPath}")
def String2Integer(string):
	return int(string)

def Integer2String(integer): return str(integer)
def TodayInFormatting(formatting):
	# Good Formatting: [year]-[day]-[month] [hour]:[minute] [m]
	# M is replaced by AM or PM.
	dtt = datetime.datetime.today()
	dt = str(formatting)
	dt = dt.replace("[year]",str(dtt.year))
	dt = dt.replace("[month]",str(dtt.month))
	dt = dt.replace("[day]",str(dtt.day))
	dt = dt.replace("[hour]",str(dtt.hour))
	dt = dt.replace("[minute]",str(dtt.minute))
	dt = dt.replace("[second]",str(dtt.second))
	dt = dt.replace("[microSecond]",str(dtt.microsecond))
	if dtt.hour >= 12:
		m = "PM"
	elif dtt.hour <= 12:
		m = "AM"
	dt = dt.replace("[m]",str(m))
	return dt

def ReadFileLines(file): 
	pp = open(f"{file}","r")
	ppp = pp.readlines()
	pp.close()
	return ppp

def GetWebpageInfo(url):
	try:
		import requests
	except:
		os.system("echo You have used the get or post package, which require the requests package. Installing")
		os.system("python3 -m pip install requests")
	else:
		import requests
		requests.get(url)