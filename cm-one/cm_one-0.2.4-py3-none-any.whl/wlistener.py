import socket
from time import sleep
import logging
from traceback import format_exc
from cm.configs import config as s
import pickle
import threading

class WListener():
	'''Прослушиватель ком портов, к которым линкуются периферийные
	железки, при создании экземпляра необходимо задать имя железки,
	номер ком-порта, порт'''
	def __init__ (self, name='def', comnum='25', port='1488', bs = 8, py = 'N',
	sb = 1, to = 1, ip='localhost', ar_ip='localhost'):
		self.name = name
		self.ip = ip
		self.comnum = comnum
		self.port = port
		self.bs = bs
		self.ar_ip = ar_ip
		self.sb = sb
		self.to = to
		self.py = py
		self.smlist = ['0']
		self.status = 'Готов'
		self.addInfo = {'carnum':'none', 'status':'none','notes':'none'}
		self.cmInterfaceComms = []
		self.activity = True
		#if s.cmUseInterfaceOn == True:
			#print('Интерфейс взаимодействия с Watchman-CM активирован')
			#threading.Thread(target=self.cmUseInterface, args=()).start()
	'''
	def wlisten(self):
		По строково читает приходящие значения и
			сохраняет последнее значение в переменную self.rval
		ser = serial.Serial(self.comnum, bytesize=self.bs,
			parity=self.py, stopbits=self.sb, timeout=self.to)
		sleep(0.5)
		self.data = ser.readline()
		ser.close()
		return self.data
	'''

	def wlisten_tcp(self):
		try:
			return self.smlist[-1]
		except:
			logging.error(format_exc())

	def get_value(self):
		'''Геттер для последнего прослушанного значения'''
		return self.data

	def parse_weight(self, weight):
		datal = weight.split(',')
		for el in datal:
			if 'kg' in el and len(el) > 2: pass

	def scale_reciever(self, scale_ip):
		client = socket.socket()
		while True:
			try:
				self.connect_cps(client, scale_ip)
				self.interact_cps(client)
			except:
				print(format_exc())
				sleep(3)
				
	def connect_cps(self, client, scale_ip):
		while True:
			try:
				client.connect((scale_ip, s.scale_splitter_port))
				break
			except:
				print('Have no connection with CPS. Retry')
				sleep(3)
				
	def interact_cps(self, client):
		while True:
			data = client.recv(1024)
			if not data: break
			data = data.decode(encoding='utf-8')
			self.smlist.append(data)
			#self.format_weight(data)

	def format_weight(self, weight):
		#print('ORMATING WEIGHT', weight)
		#print(type(weight))
		datal = weight.split(',')
		for el in datal:
			if 'kg' in el and len(el) > 2:
				el = el.replace("kg", '')
				el = el.split(' ')
				try:
					self.rcv_data = el[-2]
				except IndexError:
					###УДАЛИТЬ ПОСЛЕ ТЕСТА###
					#logging.error(format_exc())
					#logging.error('el is',el)
					self.rcv_data = '0'
					print('incorrect weight')
					#seven.close()
				self.smlist.append(self.rcv_data)
				#print(self.rcv_data)

	'''
	def tcp_listener_server(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1024)
		while True:
			conn,addr = serv.accept()
			from_client = ''
			while True:
				while 1:
					try:
						data = conn.recv(1024)
						break
					except:
						sleep(1)
				if not data: break
				data = str(data)
				#print('Получны данные с весов -', data)
				self.format_weight(data)
			conn.close()

	def tcp_listener_server2(self):
		print('\nЗапуск сервера для получения показания весов')
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1024)
		while True:
			conn,addr = serv.accept()
			while True:
				while 1:
						data = conn.recv(1024)
						if not data: break
						data = str(data)
						self.format_weight(data)
				#conn.close()
	'''

	def tcpLoggingServ(self):
		self.dispatcher()

	def handleClient(self, conn):
		while True:
			print('Есть подключение к серверу сообщений. Ждем Id чата')
			chatid = conn.recv(1024)
			chatid = chatid.decode()
			print('chatid -', chatid)
			logfilepath = '/home/watchman/watchman/chatlogs/log_{}id.txt'.format(chatid)
			try:
				logfile = open(logfilepath, 'r')
				chatdata = logfile.read()
				chatdata = pickle.dumps(chatdata)
				conn.send(chatdata)
				logfile.close()
			except FileNotFoundError:
				chatdata = b''
				chatdata = pickle.dumps(chatdata)
				conn.send(chatdata)
			while 1:
				logfile = open(logfilepath,'a')
				print('Ожидаются данные для логирования')
				data = conn.recv(1024)
				if not data:
					print('Нет данных')
					break
				print('Есть сообщение!')
				data = pickle.loads(data)
				msg = '  END&MSG  ' + data['username'] + '  FRAG&END  ' + data['data'] + '  FRAG&END  ' + data['time']
				logfile.write(msg)
				logfile.close()
			conn.close()

	def dispatcher(self):
		#while True:
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1488)
		while True:
			print('\n\nСервер сообщений запущен.')
			conn, addr = serv.accept()
			print('Есть клиент')
			threading.Thread(target=self.handleClient, args=(conn,)).start()

	def statusSocket(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((s.statusSocketIp, s.statusSocketPort))
		serv.listen(10)
		print('c0')
		while True:
		#	try:
			print('Ожидание СМ для передачи статуса')
			conn,addr = serv.accept()
			print('CM для статуса подключен')
			while 1:
				sleep(0.5)
				d = pickle.dumps(self.status)
				conn.send(d)
				#print('Отправлеяется статус', self.status)
				while self.status != 'Готов':
					#print('Занят. Отправляется статус.')
					sleep(0.5)
					x = pickle.dumps(self.addInfo)
					conn.send(x)
			#conn.close()
		#	except:
		#		sleep(1)
		#		print('retry')

	def cmUseInterface(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((s.cmUseInterfaceIp, s.cmUseInterfacePort))
		print('Ожидание подключения')
		serv.listen(1488)
		while True:
			try:
				conn,addr = serv.accept()
				print('Есть соединение с CM')
				while 1:
					sleep(0.5)
					print('Ожидаются комманды')
					comm = conn.recv(1024)
					if not comm: break
					comm = comm.decode()
					print('Got', comm)
					#self.cmInterfaceComms.append(comm)
					print('cpre0')
					response = self.executeComm(comm)
					print('sending response', response)
					conn.send(bytes(response, encoding='utf-8'))
					print('sent with success')
				conn.close()
			except:
				sleep(1)
				print('Потеряна связь с CM.\n')

	def executeComm(self, comm):
		comm = comm.strip()
		if comm == 'block':
			self.activity = False
			response = 'Watchman-AR freeze'
		elif comm == 'unblock':
			self.activity = True
			response = 'Watchman-AR unfreeze'
		elif 'createStr' in comm:
			#response = self.parseComm(comm)
			self.cmInterfaceComms.append(comm)
			response = 'none'
		elif 'closeRec' in comm:
			self.cmInterfaceComms.append(comm)
			response = 'closeRec comm added to stream'
		elif comm == 'status':
			response = self.status
		else:
			response = 'Unknown command'
		return response

	def parseComm(self, comm):
		commlist = comm.split('%&%')
		comm = commlist[1]
		return comm

	def setStatus(self, status):
		self.status = status

	def setStatusObj(self, obj):
		self.statusObj = obj

	def getStatus(self):
		return self.status

	def parseComms(self, data): pass
if __name__ == "__main__":
	scale = WListener('scale', 'COM11', 1337)
	scale.tcp_listener_server()
	#scale.tcp_listener_client()
# while 1:
		# scale.wlisten()
