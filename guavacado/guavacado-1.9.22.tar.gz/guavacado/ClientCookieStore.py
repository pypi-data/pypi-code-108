#! /usr/bin/env python

from datetime import datetime, timedelta

class ClientCookieStore(object):
	'''An object used to encapsulate the client-side cookies to be used with a request'''
	def __init__(self):
		self.cookie_list = []
	
	def AddCookie(self, cookie):
		for rem_cookie in self.GetCookiesMatchingCriteria(name=cookie.name, Domain=cookie.Domain, Path=cookie.Path):
			self.cookie_list.remove(rem_cookie)
		self.cookie_list.append(cookie)
	
	def GetCookiesMatchingCriteria(self, name=None, Domain=None, Path=None, Expiration=None, HttpOnly=None, Secure=None, RequestIsSameSite=None):
		ret = []
		for cookie in self.cookie_list:
			if name is None or cookie.matches_name(name):
				if Domain is None or cookie.matches_Domain(Domain):
					if Path is None or cookie.matches_Path(Path):
						if Expiration is None or cookie.matches_Expiration(Expiration):
							if HttpOnly is None or cookie.matches_HttpOnly(HttpOnly):
								if Secure is None or cookie.matches_Secure(Secure):
									if RequestIsSameSite is None or cookie.matches_SameSite(RequestIsSameSite):
										ret.append(cookie)
		return ret
	
	def copy(self):
		ret = ClientCookieStore()
		for cookie in self.cookie_list:
			ret.AddCookie(cookie.copy())
		return ret
	
	@staticmethod
	def GetClientCookiesHeaderText(cookies):
		ret = '; '.join([c.getHeaderTextClient() for c in cookies])
		return ret

class ClientCookie(object):
	'''An object representing the properties of a cookie as stored on the client'''
	def __init__(self, name, value, Domain, Path, Expires=None, MaxAge=None, HttpOnly=False, Secure=False, SameSite=None):
		self.createdtime = datetime.now()
		self.name = name
		self.value = value
		self.Domain = Domain
		self.Path = Path
		self.Expires = Expires
		self.MaxAge = MaxAge
		self.HttpOnly = HttpOnly
		self.Secure = Secure
		self.SameSite = SameSite

	@staticmethod
	def gen_blank_cookie_object():
		return ClientCookie(None, None, None, None)

	@staticmethod
	def from_header(header_text, default_Domain, default_Path):
		ret = ClientCookie.gen_blank_cookie_object()
		segments = header_text.split('; ')
		is_first_segment = True
		ret.Domain = default_Domain # set Domain and Path to the defaults - they will be overwritten if they are specified
		ret.Path = default_Path
		for segment in segments:
			if '=' in segment:
				(key, val) = tuple(segment.split('='))
			else:
				key = segment
				val = True
			if is_first_segment:
				ret.name = key
				ret.value = val
				is_first_segment = False
			else:
				if key in ['Max-Age']:
					key = key.replace('-','')
				if key in ['domain', 'path', 'expires', 'secure']:
					key = key[0].upper()+key[1:]
				if key in ['maxage', 'max-age', 'httponly', 'samesite']:
					if key in ['maxage', 'max-age']:
						key = 'MaxAge'
					elif key=='httponly':
						key = 'HttpOnly'
					elif key=='samesite':
						key = 'SameSite'
				if key in ['Domain', 'Path', 'Expires', 'MaxAge', 'HttpOnly', 'Secure', 'SameSite']:
					setattr(ret, key, val)
		return ret
	
	def copy(self):
		return ClientCookie(self.name, self.value, self.Domain, self.Path, Expires=self.Expires, MaxAge=self.MaxAge, HttpOnly=self.HttpOnly, Secure=self.Secure, SameSite=self.SameSite)
	
	def getExpireTime(self):
		if self.MaxAge is None:
			if self.Expires is None:
				return None
			else:
				return datetime.strptime(self.Expires, '%a, %d %b %Y %H:%M:%S GMT')
		else:
			return self.createdtime + timedelta(seconds=int(self.MaxAge))
	
	def getHeaderTextClient(self):
		return self.name+'='+self.value
	
	def getHeaderTextServer(self):
		def gen_keyval(key,val):
			return key+'='+val
		keyvals = [
			gen_keyval(self.name,self.value),
			gen_keyval('Domain',self.Domain),
			gen_keyval('Path',self.Path),
		]
		ExpireTime = self.getExpireTime()
		if ExpireTime is not None:
			keyvals.append(gen_keyval('Expires',ExpireTime.strftime('%a, %d %b %Y %H:%M:%S GMT')))
		if self.HttpOnly:
			keyvals.append('HttpOnly')
		if self.Secure:
			keyvals.append('Secure')
		if self.Secure:
			keyvals.append(gen_keyval('SameSite',self.SameSite))
		return '; '.join(keyvals)
	
	def matches_name(self, name):
		return name==self.name
	def matches_Domain(self, Domain):
		return (Domain.endswith(self.Domain) and (len(self.Domain)==len(Domain) or self.Domain.startswith('.') or Domain[:(-1*len(self.Domain))].endswith('.')))
	def matches_Path(self, Path):
		return (Path.startswith(self.Path) and (len(self.Path)==len(Path) or self.Path.endswith('/') or Path[len(self.Path):].startswith('/')))
	def matches_Expiration(self, Expiration):
		ExpireTime = self.getExpireTime()
		if ExpireTime is None:
			return True
		return Expiration >= ExpireTime
	def matches_HttpOnly(self, HttpOnly):
		return HttpOnly==self.HttpOnly
	def matches_Secure(self, Secure):
		if self.Secure:
			return Secure
		else:
			return True
	def matches_SameSite(self, RequestIsSameSite):
		if self.SameSite=='Strict':
			return RequestIsSameSite
		if self.SameSite=='Lax':
			return RequestIsSameSite
		if self.SameSite=='None':
			return self.matches_Secure(True)
		return False
