# --*-- encodng: urf8 --*--
# !/usr/bin/env python3

# =================== Cript Username ====================

from random import randrange

class EncriptAll():
	def __init__(self):

		# define differents var to generate criptfile and keys

		# var from input
		self.account_ = None
		self.cript_password = None
		self.uncript_password = None
			

		# beginning handing process

	# Afther calling this function we return list values we containt keys and crypt values

	def cript(self, target):
		# create dic var we contaitn first value and keys to uncrypt values

		# __init__ variours
			
		key_val = list()
		key = list()
		values = list()
		
		container_cript = list()
		for el in range(len(target)):
			if ord(target[el]) < 10:
				key_val.append((ord(target[el]), chr(randrange(1, 10))))

			elif ord(target[el]) < 100:
				interline = randrange(10, 100)
				if interline in range(48, 58):
					interline = 71
				key_val.append((ord(target[el]), chr(interline)))

			elif ord(target[el]) < 1000:
				key_val.append((ord(target[el]), chr(randrange(100, 1000))))
			
			elif ord(target[el]) < 10000:
				key_val.append((ord(target(el)), chr(randrange(1000, 10000))))

			else: key_val.append((ord(target[el]), chr(randrange(10000, 1000000))))

		for el in key_val:
			values.append(el[1])
			values.append(el[0])

		# print(values)
		string_int_ = [str(int) for int in values]
		#save_
		self.cript_password = "".join(string_int_)

		return self.cript_password

	
	def uncript(self, target):
		key = list()
		keys = list()
		values = list()


		for el in range(len(target)):
			try:
				chr(int((target[el])))

			except:
				key.append(ord(target[el]))	

		for el in key:
			if el < 10 :keys.append(1)

			elif el < 100:keys.append(2)

			elif el < 1000:keys.append(3)

			elif el < 10000:keys.append(4)

			else:keys.append(5)

		n = 1
		for key in keys:
			values.append(chr(int(target[n:n+key])))
			n+=(key+1)

		self.uncript_password = "".join(values)
		
		return self.uncript_password
		
		

if __name__ == "__main__":
	enc = EncriptAll()

	
		