import json
import time
from datetime import datetime
import datetime
from os.path import exists
import os

import pyotp 
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import cv2 
import pytesseract
import argparse
import mysql.connector
import yaml
import wget

__version__ = "1.5.1"

def main():
	ruta = os.path.dirname(os.path.abspath(__file__))
	
	parser = argparse.ArgumentParser(description='Una API per a recullir informacio de la web de CatBackup.')
	parser.add_argument('-q', '--quiet', help='Nomes mostra els errors i el missatge de acabada per pantalla.', action="store_false")
	parser.add_argument('-tr','--tesseractpath', help='La ruta fins al fitxer tesseract.exe', default=ruta+'/tesseract/tesseract.exe', metavar='RUTA')
	parser.add_argument('-g', '--graphicUI', help='Mostra el navegador graficament.', action="store_false")
	parser.add_argument('-v', '--versio', help='Mostra la versio', action='version', version='CatBackupAPI-NPP v'+__version__)

	conf = ruta+"/config/config.yaml"
	if not(os.path.exists(ruta+"/config")):
		os.mkdir(ruta+"/config")
	if not(os.path.exists(ruta+"/errorLogs")):
		os.mkdir(ruta+"/errorLogs")
	if not(os.path.exists(ruta+"/chromedriver.exe")):
		wget.download("https://github.com/NilPujolPorta/CatbackupAPI-NPP/blob/master/CatBackupAPI/chromedriver.exe?raw=true", ruta+"/chromedriver.exe")


	if not(exists(conf)):
		print("Emplena el fitxer de configuracio de Base de Dades a config/config.yaml")
		article_info = [
			{
				'BD': {
				'host' : 'localhost',
				'user': 'root',
				'passwd': 'patata'
				}
			}
		]

		with open(conf, 'w') as yamlfile:
			data = yaml.dump(article_info, yamlfile)

	with open(conf, "r") as yamlfile:
		data = yaml.load(yamlfile, Loader=yaml.FullLoader)

	servidor = data[0]['BD']['host']
	usuari = data[0]['BD']['user']
	contrassenya = data[0]['BD']['passwd']

	try:
		mydb =mysql.connector.connect(
			host=servidor,
			user=usuari,
			password=contrassenya,
			database="CatBackup"
			)
		mycursor = mydb.cursor(buffered=True)
		print("Access BDD correcte")
	except:
		try:
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya
				)
			print("Base de dades no existeix, creant-la ...")
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE DATABASE CatBackup")
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya,
				database="CatBackup"
				)
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE TABLE credencials (usuari VARCHAR(255), contassenya VARCHAR(255), host VARCHAR(255));")
		except:
			print("Login BDD incorrecte")
			quit()

	mycursor.execute("SELECT * FROM credencials")
	resultatbd = mycursor.fetchall()

	parser.add_argument('-w', '--web', help="Especificar la web de Catbackup a on accedir. Per defecte es l'aconsegueix de la basa de dades", default=resultatbd[0][2], metavar="URL")
	args = parser.parse_args()
	if not(os.path.exists(ruta+"/tesseract") and os.path.isfile(ruta+"/tesseract/tesseract.exe")):
		os.mkdir(ruta+"/tesseract")
		wget.download("https://github.com/NilPujolPorta/CatbackupAPI-NPP/blob/master/CatBackupAPI/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe?raw=true", ruta+"/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe")
		print("=========================================================")
		print("INSTALA EL TESSERACT EN LA CARPETA CatBackupAPI/tesseract")
		print("=========================================================")
		time.sleep(20)
		os.popen(ruta+"/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe")
		quit()

	pytesseract.pytesseract.tesseract_cmd = (args.tesseractpath)

	options = Options()
	if args.graphicUI:
		options.headless = True
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('window-size=1200x600')
	browser = webdriver.Chrome(executable_path = ruta+"/chromedriver.exe", options=options)

	browser.get(args.web)

	find_user = browser.find_element(by='id', value="txtLogin")
	find_user.send_keys(resultatbd[0][0])

	find_passwd = browser.find_element(by='id', value="txtPassword")
	find_passwd.send_keys(resultatbd[0][1])

	find_login = browser.find_element(by='id', value="btnLogin")
	find_login.click()


	time.sleep(5)


	find_key = browser.find_element(by='id', value="txtSecretCode")
	totp = pyotp.TOTP(resultatbd[0][3])
	find_key.send_keys(totp.now())

	find_login2 = browser.find_element(by='id', value="btnLogin")
	find_login2.click()

	time.sleep(20)


	browser.save_screenshot('screenshot.png')
	browser.quit()


	img = cv2.imread('screenshot.png')
	text = pytesseract.image_to_string(img)

	if os.path.exists("screenshot.png"):
		os.remove("screenshot.png")
	else:
		print("The file does not exist")

	x = text.find("Success: ")
	if x == -1:
		x = text.find("success: ")
	if x == -1:
		correctes = 0
	else:
		y= x+9
		x= y+2
		correctes = int(text[y:x])

	x = text.find("Failed: ")
	if x == -1:
		erronis = 0
	else:
		y= x+8
		x= y+2
		erronis = int(text[y:x])

	x = text.find("Overdue: ")
	if x == -1:
		atrasats = 0
	else:
		y= x+9
		x= y+2
		atrasats = int(text[y:x])

	x = text.find("Warning: ")
	if x == -1:
		advertencies = 0
	else:
		y= x+9
		x= y+2
		advertencies = int(text[y:x])

	if args.quiet:
		print("Correctes: "+str(correctes))
		print("Erronis: "+str(erronis))
		print("Atrasats: "+str(atrasats))
		print("Advertencies: "+str(advertencies))
		print("total: "+str(correctes+erronis+atrasats+advertencies))


	Lcorrectes = []
	x = 0
	while x < correctes:
		Lcorrectes.append({"Status":"Correctes"})
		x = x+1
	Lerronis = []
	x = 0
	while x < erronis:
		Lerronis.append({"Status":"Erronis"})
		x = x+1
	Latrasats = []
	x = 0
	while x < atrasats:
		Latrasats.append({"Status":"Atrasats"})
		x = x+1
	Ladvertencies = []
	x = 0
	while x < advertencies:
		Ladvertencies.append({"Status":"Warning"})
		x = x+1

	dictionary = {'Correctes':Lcorrectes, 'Erronis':Lerronis, 'Atrasats':Latrasats, 'Advertencies':Ladvertencies}
	if exists("dadesCatBackup.json") == True:
			os.remove("dadesCatBackup.json")
	try:
		with open("dadesCatBackup.json", 'w') as f:
			json.dump(dictionary, f, indent = 4)
	except Exception as e:
			print("Error d'escriptura de json"+str(e))
			now = datetime.datetime.now()
			date_string = now.strftime('%Y-%m-%d--%H-%M-%S-json')
			f = open(ruta+"/errorLogs/"+date_string+".txt",'w')
			f.write("Error d'escriptura de json "+str(e))
			f.close()
	if not(args.quiet):
		print("Done")

if __name__ =='__main__':
    main()