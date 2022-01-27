import Famcy

LOCAL_USER = "/home/%U/.local/share/famcy"

def main(args):
	# Write famcy.ini
	content = """[uwsgi]
module = wsgi:app
master = true
processes = 5
http-socket = :9090
chmod-socket = 660
vacuum = true
die-on-term = true
enable-threads = true
single-interpreter = true
http-websockets = true
logto = %s""" % (LOCAL_USER + "/" + args[0] + "/logs/" + args[0] + ".log")

	f = open(Famcy.famcy_dir + "/famcy.ini", "w")
	f.write(content)
	f.close()
	
	# Write wsgi.py
	content = """from Famcy import create_app

app = create_app('%s',True)

if __name__ == "__main__":
    app.run()"""% (args[0])

	f = open(Famcy.famcy_dir + "/wsgi.py", "w")
	f.write(content)
	f.close()

	print("Deployed to wsgi")