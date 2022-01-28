#!python

import os
import io
import sys
import gzip
import re
import argparse
import tempfile
from collections import Counter
from argparse import RawTextHelpFormatter
from itertools import zip_longest, chain

from rapidfuzz import fuzz

def is_valid_file(x):
	if not os.path.exists(x):
		raise argparse.ArgumentTypeError("{0} does not exist".format(x))
	return x

def nint(x):
    return int(x.replace('<','').replace('>',''))

def rev_comp(dna):
	a = 'acgtrykmbvdh'
	b = 'tgcayrmkvbhd'
	tab = str.maketrans(a,b)
	return dna.translate(tab)[::-1]

def mask(seq1, seq2):
    out1 = out2 = ''
    for tup in zip(seq1,seq2):
        if 'X' not in tup:
            out1 += tup[0]
            out2 += tup[1]
    return out1,out2

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

class Translate:
	def __init__(self):
		nucs = 'acgt'
		codons = [a+b+c for a in nucs for b in nucs for c in nucs]
		amino_acids = 'KNKNTTTTRSRSIIMIQHQHPPPPRRRRLLLLEDEDAAAAGGGGVVVV#Y+YSSSS*CWCLFLF'
		self.translate = dict(zip(codons, amino_acids))
		ambi = """aarK aayN acrT acyT ackT acmT acbT acvT acdT achT agrR agyS atyI atmI athI 
		carQ cayH ccrP ccyP cckP ccmP ccbP ccvP ccdP cchP cgrR cgyR cgkR cgmR cgbR cgvR cgdR 
		cghR ctrL ctyL ctkL ctmL ctbL ctvL ctdL cthL garE gayD gcrA gcyA gckA gcmA gcbA gcvA 
		gcdA gchA ggrG ggyG ggkG ggmG ggbG ggvG ggdG gghG gtrV gtyV gtkV gtmV gtbV gtvV gtdV 
		gthV tar* tayY tcrS tcyS tckS tcmS tcbS tcvS tcdS tchS tgyC ttrL ttyF tra* ytaL ytgL 
		ytrL mgaR mggR mgrR"""
		for item in ambi.split():
			self.translate[item[0:3]] = item[-1]
		self.amino_acids = sorted(set(amino_acids))

	def rev_comp(self, seq):
		seq_dict = {'a':'t','t':'a','g':'c','c':'g',
					'n':'n',
					'r':'y','y':'r','s':'s','w':'w','k':'m','m':'k',
					'b':'v','v':'b','d':'h','h':'d'}
		return "".join([seq_dict[base] for base in reversed(seq)])

	def codon(self, codon):
		if len(codon) == 3:
			return self.translate.get(codon.lower(), 'X')
		else:
			return ''

	def sequence(self, seq, strand):
		aa = ''
		if strand > 0:
			for i in range(0, len(seq), 3):
				aa += self.codon(seq[i:i+3])
			return aa
		else:
			for i in range(0, len(seq), 3):
				aa += self.codon(self.rev_comp(seq[i:i+3]))
			return aa[::-1]
	
	def counts(self, seq, strand):
		aa = self.sequence(seq, strand)
		return Counter(aa)

	def frequencies(self, seq, strand):
		counts = self.counts(seq, strand)
		total = sum(counts.values())
		for aa in counts:
			counts[aa] = counts[aa] / total
		return counts

	def dimers(self, seq, strand):
		peptides = self.sequence(seq, strand)
		counts = { (a,b):0 for a in self.amino_acids + ['X'] for b in self.amino_acids + ['X'] }
		for i in range(len(peptides)-1):
			counts[ ( peptides[i] , peptides[i+1] ) ] += 1
		t = sum(counts.values()) if sum(counts.values()) else 1
		return [ counts[(a,b)]/t for a in self.amino_acids for b in self.amino_acids ]

translate = Translate()

class Feature:
	def __init__(self, line):
		self.line = line
		self.type = line.split()[0]
		self.partial  = 'left' if '<' in line else ('right' if '>' in line else False)
		self.direction = -1 if 'complement' in line else 1
		pairs = [pair.split('..') for pair in re.findall(r"<*\d+\.\.>*\d+", line)]
		# this is for weird malformed features
		if ',1)' in line:
			pairs.append(['1','1'])
		# tuplize the pairs
		self.pairs = tuple([tuple(pair) for pair in pairs])
		self.tags = dict()
		self.dna = ''

	def hypothetical(self):
		function = self.tags['product'] if 'product' in self.tags else ''
		if 'hypot'  in function or \
		   'etical' in function or \
		   'unchar' in function or \
		   ('orf' in function and 'orfb' not in function):
			return True
		else:
			return False

	def __str__(self):
		"""Compute the string representation of the feature."""
		return "%s\t%s\t%s\t%s" % (
				repr(self.locus),
				repr(self.type),
				repr(self.pairs),
				repr(self.tags))

	def __repr__(self):
		"""Compute the string representation of the feature."""
		return "%s(%s, %s, %s, %s)" % (
				self.__class__.__name__,
				repr(self.locus),
				repr(self.type),
				repr(self.pairs),
				repr(self.tags))

	def base_locations(self, full=False):
		if full and self.partial == 'left': 
			for i in range(-((3 - len(self.dna) % 3) % 3), 0, 1):
				yield i+1
		for pair in self.pairs:
			left,right = map(int, [ item.replace('<','').replace('>','') for item in pair ] )
			for i in range(left,right+1):
				yield i

	def codon_locations(self):
		assert self.type == 'CDS'
		for triplet in grouper(self.base_locations(full=True), 3):
			if triplet[0] >= 1:
				yield triplet

	def translation(self):
		global translate
		aa = []
		codon = ''
		first = 0 if '<' not in self.pairs[0][0] else len(self.dna) % 3
		for i in range(first, len(self.dna), 3):
			codon = self.dna[ i : i+3 ]
			if self.direction > 0:
				aa.append(translate.codon(codon))
			else:
				aa.append(translate.codon(rev_comp(codon)))
		if self.direction < 0:
			aa = aa[::-1]
		if aa[-1] in '#*+':
			aa.pop()
		#aa[0] = 'M'
		return "".join(aa)

	def integrity_check(self):
		seq2 = self.translation()
		if 'translation' not in self.tags:
			return 1 - ( seq2.count('#') + seq2.count('*') + seq2.count('+') ) / len(seq2)
		else:
			seq1 = self.tags['translation']
			seq1,seq2 = mask(seq1, seq2)
			seq1,seq2 = (seq1[1:], seq2[1:])
			return max(
					fuzz.ratio(seq1, seq2),
					fuzz.ratio(seq1, seq2.replace('*', 'W'))
					) / 100

class Locus(dict):
	def __init__(self, fp, current=None):
		self.locus = None
		self.current = current
		self.dna = False
		in_features = False

		for line in fp:
			line = line.decode("utf-8")
			if line.startswith('LOCUS'):
				self.locus = line.split()[1]
			elif line.startswith('ORIGIN'):
				in_features = False
				self.dna = ''
			elif line.startswith('FEATURES'):
				in_features = True
			elif in_features:
				line = line.rstrip()
				if not line.startswith(' ' * 21):
					while line.endswith(','):
						line += next(fp).decode('utf-8').strip()
					self.add_feature(line)
				else:
					while line.count('"') == 1:
						line += next(fp).decode('utf-8').strip()
					tag,_,value = line[22:].partition('=')
					self.current.tags[tag] = value.replace('"', '')
			elif self.dna != False:
				self.dna += line[10:].rstrip().replace(' ','').lower()
		# set dna for features and check integrity
		for feature in self.features():
			for i in feature.base_locations():
				feature.dna += self.dna[ i-1 : i ]
			if feature.type == 'CDS':
				if len(feature.dna) % 3 and not feature.partial and 'transl_except' not in feature.tags:
					raise ValueError("Out of frame: %s" % feature)
				if feature.integrity_check() < 0.95:
					raise ValueError("Error in translation:\n%s\n%s" % (feature.tags['translation'], feature.translation()) )

	def features(self, include=None, exclude=None):
		for  feature in self:
			if not include or feature.type in include:
				yield feature

	def add_feature(self, line):
		"""Add a feature to the factory."""
		feature = Feature(line)
		feature.location = line
		feature.locus = self.locus
		if feature not in self:
			self[feature] = True
			self.current = feature


class GenbankFile(dict):
	def __init__(self, filename, current=None):
		''' use tempfiles since using next inside a for loop is easier'''
		temp = tempfile.TemporaryFile()
		
		lib = gzip if filename.endswith(".gz") else io
		with lib.open(filename, mode="rb") as fp:
			for line in fp:
				temp.write(line)
				if line.startswith(b'//'):
					temp.seek(0)
					locus = Locus(temp)
					self[locus.locus] = locus
					temp.seek(0)
					temp.truncate()
		temp.close()

	def features(self, include=None, exclude=None):
		for locus in self.values():
			for feature in locus.features(include=include):
				yield feature

	def gene_coverage(self):
		''' This calculates the protein coding gene coverage, which should be around 1 '''
		cbases = tbases = 0	
		for locus in self.values():
			dna = [False] * len(locus.dna)
			seen = dict()
			for feature in locus.features(include=['CDS']):
				for i in feature.codon_locations():
					dna[i-1] = True
			cbases += sum(dna)
			tbases += len(dna)
		return 3 * cbases / tbases
	

if __name__ == "__main__":
	usage = '%s [-opt1, [-opt2, ...]] infile' % __file__
	parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
	parser.add_argument('infile', type=is_valid_file, help='input file in genbank format')
	parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
	parser.add_argument('-f', '--format', help='Output the features in the specified format', type=str, default='tabular', choices=['tabular','genbank','fasta', 'fna','faa', 'coverage'])
	args = parser.parse_args()

	genbank = GenbankFile(args.infile)

	if args.format == 'tabular':
		for feature in genbank.features(include=['CDS']):
			args.outfile.write(str(feature))
			args.outfile.write("\n")
	elif args.format == 'coverage':
		args.outfile.write(str(genbank.gene_coverage()))
		args.outfile.write("\n")
	elif args.format == 'faa':
		for feature in genbank.features(include=['CDS']):
			args.outfile.write(">")
			args.outfile.write(feature.locus)
			args.outfile.write("[")
			args.outfile.write(feature.location.split()[1])
			args.outfile.write("]")
			args.outfile.write("\n")
			args.outfile.write(feature.translation())
			args.outfile.write("\n")

