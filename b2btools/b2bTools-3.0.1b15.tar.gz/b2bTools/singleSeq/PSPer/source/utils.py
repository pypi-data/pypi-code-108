#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  learnBackgrounds.py
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
import math, os, gc
import matplotlib.pyplot as plt
import numpy as np


def readFASTA(seqFile, MIN_LENGTH = 20, MAX_LENGTH=1500):
	ifp = open(seqFile, "r")
	sl = {}
	i = 0
	line = ifp.readline()
	discarded = 0

	while len(line) != 0:
		tmp = []
		if line[0] == '>':
			#sl.append([line.strip().replace("|","").replace(">","")[:5]+"_",""])	#only for spx

			tmp = [line.strip().split(" ")[-3][3:],""] #attenzione
			line = ifp.readline()
			while len(line) > 0 and line[0] != '>':
				tmp[1] = tmp[1] + line.strip()
				line = ifp.readline()
			#print len(tmp[1])
			#raw_input()
			i = i + 1
			if len(tmp[1]) > MAX_LENGTH or len(tmp[1]) < MIN_LENGTH:
				#print "discard"
				discarded += 1
				continue
			else:
				sl[tmp[0]] = tmp[1]
		else:
			raise Exception("Syntax error in the fasta file "+seqFile+"!")
	print ("Found %d sequences, added %d discarded %d" % (i, len(sl), discarded))
	return sl

listAA = [  "A",  "C",  "D",  "E",  "F",  "G",  "H",  "I",  "K",  "L",  "M",  "N",  "P",  "Q",  "R",  "S",  "T",  "V",  "W",  "Y"  ]

def buildVectorsRSA(seqs, WS):
	X = []
	for u in seqs.items():
		i = 0
		#assert len(tmprsa) == len(seq)
		targetSeq = u[1]
		#print targetSeq
		while i < len(str(targetSeq)):
			fragment = seq2vecSklearn(targetSeq, WS, i)
			X.append(fragment)
			#print fragment
			#raw_input()
			i += 1
	#raw_input()
	return X

def seq2vecSklearn(seq, sw, pos):
	vec=[]
	startpos=pos-(sw/2)
	if startpos < 0 :
		vec= ["0"] * int((-startpos))
		startpos=0
	endpos=pos+(sw/2)+1

	vec += str(seq)[int(startpos):int(min(len(str(seq)),endpos))]
	if endpos > len(str(seq)):
		endpos = endpos - len(str(seq))
		vec += ["0"]* int(endpos)
	#assert len(vec) == sw
	return vec

def buildSmoothVect(seq, WS):
	targetSeq = seq
	X = []
	#print targetSeq
	i = 0
	while i < len(targetSeq):
		fragment = smoothVect1(targetSeq, WS, i)
		X.append(np.mean(fragment))
		i += 1
	#raw_input()
	return X

def smoothVect1(seq,sw, pos):
	vec=[]
	startpos=pos-(sw/2)
	if startpos < 0 :
		vec= [0] * (-startpos)
		startpos=0
	endpos=pos+(sw/2)+1

	vec += seq[startpos:min(len(seq),endpos)]
	if endpos > len(seq):
		endpos = endpos - len(seq)
		vec += [0]* endpos
	#assert len(vec) == sw
	return vec

def leggifasta(database):
		f=open(database)
		uniprot=f.readlines()
		f.close()
		dizio={}
		for i in uniprot:
			i=i.strip()
			if '>' in i:
				if "|" in i:
					uniprotid=i.strip('>\n').split('|')[1]
				else:
					uniprotid = i.strip(">\n")
				dizio[uniprotid]=''
			else:
				dizio[uniprotid]=dizio[uniprotid]+i.strip('\n').upper()
		return dizio

def seqs_features(seqs, WS=10):
	diz={}
	for id in seqs.keys():
		seq=seqs[id]
		lcomp = []
		r = []
		g = []
		y = []
		fragments = buildVectorsRSA({"pippo":seq}, WS)
		for c, f in enumerate(fragments):
			c = len(set(fragments[c]))
			lcomp.append(c)
			#r.append(f.count("R"))
			r.append(f.count("R"))
			y.append(f.count("Y"))
		diz[id]=( lcomp, r, y)
	return diz

def main():
	print (seqs_features({'ddd':'AAAAAAAAAAAAAAAAAAACCCCCCCCCCCCCCTTTTTTTTTTTTTRRRRRRRRRRRRRRRRRRRGGGGGGGGGGGGGGGGG'}))

def getLKcomp(distro, frag):
	c = len(set(frag))
	return distro[c]

def getLKfreqMultivar(distro, frag):
	h = getHash(frag)
	r = 0
	try:
		return distro[h]
	except:
		return np.nan

def getHash(f):
	l = []
	for i in listAA:
		l.append(f.count(i))
	return hash(str(l))

def getLKfreq(distro, frag):
	r = 1
	for aa in frag:
		if aa not in listAA:
			continue
		r *= distro[aa]
	return r

if __name__ == '__main__':
	print (main())
