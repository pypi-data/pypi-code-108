import itertools
import abfn.configuration as configuration

def detect_lang(text):
	for c in list(text):
		if c in configuration.symbols:
			continue
		else:
			if "ऀ" <= c <= "ॿ":
				return "HI"
			
			if "ঀ" <= c <= "৾":
				return "BN"
			
			if "ઁ" <= c <= "૿":
				return "GU"
			
			if "ਁ" <= c <= "੶":
				return "GUR"
			
			if "ஂ" <= c <= "௺":
				return "TA"
			
			if "ఀ" <= c <= "౿":
				return "TE"
			
			if "ಀ" <= c <= "೯":
				return "KN"
			
			if "ഀ" <= c <= "ൿ":
				return "ML"
			
			if "ଁ" <= c <= "୷":
				return "OR"
			
			if "؀" <= c <= "ۿ":
				return "AR"
			
			if "!" <= c <= "~":
				return "EN"
			
			else:
				print("unknown language !!! text: {}".format(c))
				return None


def get_configuration_based_on_lang(text):
	lang = detect_lang(text)
	if lang == "HI":
		return (configuration.HI_m, configuration.HI_v, configuration.HI_V, configuration.HI_C, \
		        configuration.HI_symbols, configuration.HI_H)
	
	if lang == "GUR":
		return (configuration.GUR_m, configuration.GUR_v, configuration.GUR_V, configuration.GUR_C, \
		        configuration.GUR_symbols, configuration.GUR_H)
	if lang == "GU":
		return (configuration.GU_m, configuration.GU_v, configuration.GU_V, configuration.GU_C, \
		        configuration.GU_symbols, configuration.GU_H)
	
	if lang == "BN":
		return (configuration.BN_m, configuration.BN_v, configuration.BN_V, configuration.BN_C, \
		        configuration.BN_symbols, configuration.BN_H)
	
	if lang == "TE":
		return (configuration.TE_m, configuration.TE_v, configuration.TE_V, configuration.TE_C, \
		        configuration.TE_symbols, configuration.TE_H)
	
	if lang == "TA":
		return (configuration.TA_m, configuration.TA_v, configuration.TA_V, configuration.TA_C, \
		        configuration.TA_symbols, configuration.TA_H)
	
	if lang == "ML":
		return (configuration.ML_m, configuration.ML_v, configuration.ML_V, configuration.ML_C, \
		        configuration.ML_symbols, configuration.ML_H)
	
	if lang == "KN":
		return (configuration.KN_m, configuration.KN_v, configuration.KN_V, configuration.KN_C, \
		        configuration.KN_symbols, configuration.KN_H)
	
	if lang == "OR":
		return (configuration.OR_m, configuration.OR_v, configuration.OR_V, configuration.OR_C, \
		        configuration.OR_symbols, configuration.OR_H)
	
	return None


def print_unicode_characters_in_range(a, b):
	s = ""
	ch = a
	while (ch <= b):
		s += ch
		s += " "
		# print(ch, end=" ")
		ch = chr(ord(ch) + 1)
	
	return s


def get_unicode_value(ch):
	return ord(ch)


def print_in_range(xx):
	str = ""
	for x in xx:
		if "." in x:
			s = x.replace(".", "")
			s = [s[:4], s[4:]]
			s[0] = chr(int(s[0], 16))
			s[1] = chr(int(s[1], 16))
		else:
			s = []
			s.append(chr(int(x, 16)))
			s.append(chr(int(x, 16)))
		
		str += print_unicode_characters_in_range(s[0], s[1])
	print("")
	print(str)


def print_unused_char(a, b):
	from configuration import TE_symbols, TE_C, TE_H, TE_m, TE_V, TE_v
	ch = a
	while (ch <= b):
		if ch not in (TE_V + TE_v + TE_m + TE_H + TE_C + TE_symbols):
			print(ch, end=" ")
		ch = chr(ord(ch) + 1)


class ABFN:
	def is_valid_label(self, text):
		state = 0
		valid = True
		out = get_configuration_based_on_lang(text)
		
		if not out:
			print("text filtering rule not defined for give text language")
			return True
		
		m, v, V, C, symbols,H = out
		
		for ch in list(text):
			
			if not (ch in list(itertools.chain.from_iterable(out))):
				return False
			
			if ch in symbols:
				state = 0
				continue
			
			if ch in C:
				state = 2
				continue
			
			if ch in V:
				state = 1
				continue
			
			if state == 0:
				if ch in v or ch in m or ch in H:
					valid = False
					break
					
			if state == 1:
				if ch in v or ch in H:
					valid = False
					break
				
				if ch in m:
					state = 0
					continue
			
			if state == 2:
				if ch in v:
					state = 3
					continue
				
				if ch in m:
					state = 0
					continue
				
				if ch in H:
					state = 4
					continue
				
			if state == 3:
				if ch in m:
					state = 0
					continue
				
				if ch in v or ch in H:
					valid = False
					break
					
			if state ==4 :
				if ch in C:
					state = 2
					continue
				else:
					valid=False
					break
				
		return valid
	

if __name__ == "__main__":
	
	a = ABFN()
	s= ["/home/shubham/Documents/MTP/SyntheticDetectionTextGenration/SynthText/data/newsgroup/newsgroup_KN.txt"]
	for x in s:
		valid_cnt = 0
		invalid_count = 0
		
		with open(x) as f:
			for i , line in enumerate(f):
				if (i+1)%1000 ==0:
					print(i*100," ", "valid :", valid_cnt , "invalid: ", invalid_count)
					#break
					
				for word in line.split(" "):
					word=word.strip()
					if a.is_valid_label(word):
						valid_cnt+=1
					else:
						invalid_count+=1
						#print(word)
		
		print("invalid: ", invalid_count)
		print("valid: ",valid_cnt)
	
