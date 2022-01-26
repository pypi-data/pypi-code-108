"""Compute probabilities in N-grams model for upostag in ud format

bigram(tag, given_tag, conllu_file, tags_to_consider, ) : function for bigrams with specify tag in UD
trigram(tag, given_tags, conllu_file, tags_to_consider, remove_of_the_sentences)	: function for trigrams with specify tag in UD
ngram(n, tag, given_tags, conllu_file, tags_to_consider, remove_of_the_sentences)	: general funciont for ngram with specify tag in UD

bigram_matriz(tag, conllu_file, tags_to_consider, remove_of_the_sentences)	: matriz with bigram probabilities
ngram_matriz(n, tag, conllu_file, tags_to_consider, remove_of_the_sentences)	: matriz with ngram probabilities
"""


from itertools import product
import sys
from ngrams_functions import bigram, trigram, ngram


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



if __name__ == '__main__':
	sys.modules[__name__] = ngram_matriz, bigram_matriz
	#print(ngram(3, 'upos', ['NOUN', 'CCONJ'], 'test/test.conllu', ['NOUN', 'ADJ', 'CCONJ', 'VERB'], ['PUNCT', '_']))	# test
	#print(ngram_matriz(2, 'upos', 'test/test.conllu', ['NOUN', 'CCONJ', 'VERB', 'DET', 'ADP', 'AUX'], ['_'])) # test
