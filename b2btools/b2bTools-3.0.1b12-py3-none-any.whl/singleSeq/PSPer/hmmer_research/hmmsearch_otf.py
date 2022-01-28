#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hmmsearch_otf.py
#
#  Copyright 2018 scimmia <scimmia@scimmia-ThinkPad-L540>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  parseHmmer.py
#
#  Copyright 2018 Daniele Raimondi <daniele.raimondi@vub.be>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

def parseBoundaries(line):
	# qwwe  42 IFVGQLDKETTREELNRRFSTHGKIQDINLIFK---PTNIFAFIKYETEEAAAAALESENHAIFLNKTMH 108
	tmp = line.strip().split()
	return tmp[1], tmp[-1]

def parsePosteriori(line):
	tmp = line.strip().split()
	r = []
	for i in tmp[0]:
		p = castPosterior(i)
		if p == -1:
			continue
		r.append(p)
	return r

def castPosterior(v):
	if v == "*":
		return 10
	elif v == ".":
		return -1
	return int(v)

def parseOut(f):
	ifp = open(f)
	lines = ifp.readlines()
	alscores = []
	domains = []
	length = -1
	l = 0
	while l < len(lines):

		if "Scores for complete sequences" in lines[l]:
			if "[No hits" in lines[l+5]:
				return None, None
			else:
				tmp = lines[l+4].strip().split()
				#print tmp
				bitscore = float(tmp[1])
				evalue = float(tmp[3])
				alscores.append(( bitscore, evalue))
		if "Domain annotation for each sequence" in lines[l]:
			while l < len(lines):
				if "== domain" in lines[l]:
					start, end = parseBoundaries(lines[l+3])
					domains.append((int(start), int(end), parsePosteriori(lines[l+4])))
					l+=4
				l+=1
				if "Internal pipeline statistics summary:" in lines[l]:
					break
		if "residues searched)" in lines[l]:
			tmp = lines[l].strip().split()
			#print tmp
			length = int(tmp[3][1:])

		l += 1
	return domains, length

def getFeatsFromHmmer(v,l):

	if v==None:
		return None
	r = [0]*l
	for i in v:
		start = i[0]
		end = i[1]
		j = start-1
		while j < end:
			a=i[2].pop(0)
			r[j] = a
			j+=1
	return r

def main():
	a, l =  parseOut("output")

	#print a, l
	#raw_input()
	b = getFeatsFromHmmer(a,l)
	#print b
	c=hmmer_wrapper()
	c.fit_hmmer()
	print (c.predict({'a':'AAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','B':'VYVGNLGNNGNKTELERAFGYYGPLRSVWVARNPPGFAFVEFEDPRDAADAVRELDGRTLCGCRVR'}))
import os

class hmmer_wrapper:
	def __init__(self,root=''):

		from b2bTools.singleSeq.PSPer.Constants import hmmbuild_bin, hmmscan_bin

		self.ali_file=root+'rrm_align.pfam'
		self.hmmbuild_bin=hmmbuild_bin
		self.hmmscan_bin=hmmscan_bin
		self.root=root
	def fit_hmmer(self):
		#print self.hmmbuild_bin+' '+'phase_trans.hmm'+' '+self.ali_file +' > /dev/null'
		os.system(self.hmmbuild_bin+' '+self.root+'phase_trans.hmm'+' '+self.ali_file +' > /dev/null')
	def predict(self,seqs):
		resu={}
		for i in seqs.keys():
			f=open(self.root+'tmp.fasta','w')
			f.write('>tmp\n'+str(seqs[i])+'\n')
			f.close()
			os.system(self.hmmscan_bin+' -o '+self.root+'out_hmmer.tmp '+self.root+'phase_trans.hmm '+ self.root+'tmp.fasta')
			#print self.hmmscan_bin+' -o '+self.root+'out_hmmer.tmp '+self.root+'phase_trans.hmm '+ self.root+'tmp.fasta'
			a, l =  parseOut(self.root+'out_hmmer.tmp')
			b = getFeatsFromHmmer(a,l)
			os.system('rm '+self.root+'out_hmmer.tmp')
			os.system('rm '+self.root+'tmp.fasta')
			if b==None:
				b=[0]*len(str(seqs[i]))
			resu[i]=b
		return resu



if __name__ == '__main__':
	a=hmmer_wrapper()
	print (a.predict({'a':'AAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','B':'VYVGNLGNNGNKTELERAFGYYGPLRSVWVARNPPGFAFVEFEDPRDAADAVRELDGRTLCGCRVR'}))
