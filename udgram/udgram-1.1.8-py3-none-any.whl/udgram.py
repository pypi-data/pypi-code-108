"""Compute probabilities in N-grams model for upostag in ud format

bigram(tag, given_tag, conllu_file, tags_to_consider, ) : function for bigrams with specify tag in UD
trigram(tag, given_tags, conllu_file, tags_to_consider, remove_of_the_sentences)	: function for trigrams with specify tag in UD
ngram(n, tag, given_tags, conllu_file, tags_to_consider, remove_of_the_sentences)	: general funciont for ngram with specify tag in UD

bigram_matriz(tag, conllu_file, tags_to_consider, remove_of_the_sentences)	: matriz with bigram probabilities
ngram_matriz(n, tag, conllu_file, tags_to_consider, remove_of_the_sentences)	: matriz with ngram probabilities
"""


import sys
from itertools import product
#from ngrams_functions import bigram, trigram, ngram


################
import sys
from io import open
from conllu import parse_incr
from conllu.models import TokenList

###### Functions: bigram, trigram and ngram ######
def bigram(tag: str, given_tag: list, conllu_file: str, tags_to_consider: list, remove_of_the_sentence=[]) -> dict:
	'''
	Returns the probabilities of each tag given an initial tag
		
		Parameters:
			tag (str)	: An tag to use
			given_tag (list)	: List of given tags (in this case one)
			conllu_file (str)	: A file path for a conllu in format UD
			tags_to_consider (list)	: Tags to consider in model
			remove_of_the_sentence (list)	: Remove of senteces
		
		Returns:
			result (dict)	: A dictionary with probabilities for all tag
	'''
	
	# read file path in utf-8
	data_file = open(conllu_file, "r", encoding="utf-8")
	
	# initialize valiables
	result = { }
	total = 0
	
	# parser the conllu file and extract informations
	for sentence in parse_incr(data_file):
		sentence_clean = TokenList()	# for control

		for token in sentence:
			if not token[tag] in remove_of_the_sentence:
				sentence_clean.append(token)
	
		for token in sentence_clean:
			if (token[tag] == given_tag[0] and token["id"] < len(sentence_clean)):
				total += 1
				
				next_token = sentence_clean[token["id"]]
				
				if next_token[tag] in result.keys():
					result[next_token[tag]] += 1
				else:
					result[next_token[tag]] = 1

	# Remove tags from data
	all_tags = list(result.keys())

	for i in all_tags:
		if not i in tags_to_consider:
			total -= result[i]
			result.pop(i)
				
	
	# format results for probabilities
	for i in result.keys():
		result[i] = round(result[i]/total, 4)
		
	return result


def trigram(tag: str, given_tags: list, conllu_file: str, tags_to_consider: list, remove_of_the_sentences=[]) -> dict:
	'''
	Returns the probabilities of each tag given two initial tag
		
		Parameters:
			tag (str)	: An tag to use
			given_tag (list)	: List of given tags (in this case two)
			conllu_file (str)	: A file path for a conllu in format UD
			tags_to_consider (list)	: Tags to consider in model
			remove_of_the_sentence (list)	: Remove of senteces
		
		Returns:
			result (dict)	: A dictionary with probabilities for all tag
	'''

	# read file path in utf-8
	data_file = open(conllu_file, "r", encoding="utf-8")
	
	# initialize valiables
	result = { }
	total = 0

	for sentence in parse_incr(data_file):
		sentence_clean = TokenList()	# for control
		last_tags = [None, None]

		for token in sentence:
			if not token[tag] in remove_of_the_sentences:
				sentence_clean.append(token)
		
		for token in sentence_clean:
			last_tags = [last_tags[1], token[tag]]

			if (last_tags == given_tags and token["id"] < len(sentence_clean)):
				total += 1
				
				next_token = sentence_clean[token["id"]]

				if next_token[tag] in result.keys():
					result[next_token[tag]] += 1
				else:
					result[next_token[tag]] = 1

	# Remove tags from data
	all_tags = list(result.keys())

	for i in all_tags:
		if not i in tags_to_consider:
			total -= result[i]
			result.pop(i)		
	
	# format results for probabilities
	for i in result.keys():
		result[i] = round(result[i]/total, 4)
		
	return result


def ngram(n: int, tag: str, given_tags: list, conllu_file: str, tags_to_consider: list, remove_of_the_sentences=[]) -> dict:
	'''
	Returns the probabilities of each tag given n-1 initial tag
		
		Parameters:
			n (int)	: Positive interger for n-gram
			tag (str)	: An tag to use
			given_tag (list)	: List of n-1 given tags
			conllu_file (str)	: A file path for a conllu in format UD
			tags_to_consider (list)	: Tags to consider in model
			remove_of_the_sentence (list)	: Remove of senteces
		
		Returns:
			result (dict)	: A dictionary with probabilities for all tag
	'''
    
	# read file path in utf-8
	data_file = open(conllu_file, "r", encoding="utf-8")

	# initialize valiables
	result = { }
	total = 0

	for sentence in parse_incr(data_file):
		sentence_clean = TokenList()	# for control
		last_tags = [None for i in range(0, n - 1)]

		for token in sentence:
			if not token[tag] in remove_of_the_sentences:
				sentence_clean.append(token)
		
		for token in sentence_clean:
			last_tags = [last_tags[i] for i in range(1, n - 1)] + [token[tag]]

			if (last_tags == given_tags and token["id"] < len(sentence_clean)):
				total += 1
				
				next_token = sentence_clean[token["id"]]

				if next_token[tag] in result.keys():
					result[next_token[tag]] += 1
				else:
					result[next_token[tag]] = 1

	# Remove tags from data
	all_tags = list(result.keys())

	for i in all_tags:
		if not i in tags_to_consider:
			total -= result[i]
			result.pop(i)				
	
	# format results for probabilities
	for i in result.keys():
		result[i] = round(result[i]/total, 4)
		
	return result

################


###### Matriz data ######

# bigram matriz
def bigram_matriz(tag: str, conllu_file: str, tags_to_consider: list, remove_of_the_sentences=[]) -> dict:
	'''
	Returns array (dict of dicts) with data given in the first dict and
	probabilities of each tag in the second with bigram model
		
		Parameters:
			tag (str)	: An tag to use
			conllu_file (str)	: A file path for a conllu in format UD
			tags_to_consider (list)	: Tags to consider in model
			remove_of_the_sentence (list)	: Remove of senteces
		
		Returns:
			result (dict)	: A dictionary with probabilities for all tag
	'''

	result = {}

	for tag in tags_to_consider:
		result[tag] = ngram(2, 'upos', [tag], conllu_file, tags_to_consider, remove_of_the_sentences)
	
	return result


def ngram_matriz(n: int, tag: str, conllu_file: str, tags_to_consider: list, remove_of_the_sentences=[]) -> dict:
	'''
	Returns array (dict of dicts) with data given in the first dict and
	probabilities of each tag in the second with ngram model
		
		Parameters:
			n (int)	: An interger for n-gram
			tag (str)	: An tag to use
			conllu_file (str)	: A file path for a conllu in format UD
			tags_to_consider (list)	: Tags to consider in model
			remove_of_the_sentence (list)	: Remove of senteces
		
		Returns:
			result (dict)	: A dictionary with probabilities for all tag
	'''

	result = {}
	given_data = []

	for i in product(tags_to_consider, repeat=(n - 1)):
		given_data.append(list(i))

	for given_tag in given_data:
		result[tuple(given_tag)] = ngram(n, tag, given_tag, conllu_file, tags_to_consider, remove_of_the_sentences)
	
	return result


###### Test ######

# print token
def token_print(token):
	print(str(token["id"]) + "	" + 
		  str(token["form"]) + "	" + 
		  str(token["lemma"]) + "	" + 
		  str(token["upos"]) + "	" + 
		  str(token["xpos"]) + "	" + 
		  str(token["feats"]) + "	" + 
		  str(token["head"]) + "	" + 
		  str(token["deprel"]) + "	" + 
		  str(token["deps"]) + "	" + 
		  str(token["misc"]))

def test(result: dict, correct: dict):
	pass



sys.modules[__name__] = ngram_matriz, bigram_matriz

if __name__ == '__main__':
	print(ngram_matriz(2, 'upos', '../universal_dependencies/UD_Tupinamba-TuDeT/tpn_tudet-ud-test.conllu', ['NOUN', 'CCONJ', 'VERB', 'DET', 'ADP', 'AUX'], ['PUNCT', '_']))
