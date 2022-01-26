from collections import Counter, defaultdict

def pairwise(a):
   return zip(a[::2], a[1::2])


class Wordlist(Counter):
	def bigrams(self):
		bigrams = defaultdict(set)
		for word in self.keys():
			for a,b in pairwise(word):
				bigrams[a+b].add(word)
		return bigrams

	def filter_popularity(self, threshold=3):
		return Wordlist({x: count for x, count in self.items() if count >= threshold})

	def filter_length(self, threshold=3):
		return Wordlist({x: count for x, count in self.items() if len(x) >= threshold})

	def filter_unicodes(self, codepoint_ranges):
		def _included_letter(l):
			return any(ord(l) in r for r in codepoint_ranges)
		def _included(word):
			return all(_included_letter(l) for l in word)

		return Wordlist({x: count for x, count in self.items() if _included(x)})
