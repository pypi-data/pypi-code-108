from typing import List, Optional, Union
import pytest
from userinput import UserInput
import numpy as np
import abserdes
from conftest import Dictionary

@pytest.mark.dictionary
def test_dictionary_serialization(
			tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.dictionary = {
		'a' : 1, 
		'b' : 2, 
		'c' : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert ( 
		deserialized_dictionary.dictionary 
		== dictionary.dictionary
	)

@pytest.mark.dictionary
def test_tuple_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.tuple_key_dictionary = {
		(1, 2, 3) : 1, 
		(4, 5, 6) : 2, 
		(7, 8, 9) : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert ( 
		deserialized_dictionary.tuple_key_dictionary 
		== dictionary.tuple_key_dictionary
	)

@pytest.mark.dictionary
def test_int_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.int_key_dictionary = {
		1 : 1, 
		4 : 2, 
		7 : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert ( 
		deserialized_dictionary.int_key_dictionary 
		== dictionary.int_key_dictionary
	)

@pytest.mark.dictionary
def test_float128_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.float128_key_dictionary = {
		np.float128(1.23) : 1, 
		np.float128(4.56) : 2, 
		np.float128(7.89) : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.float128_key_dictionary 
		== dictionary.float128_key_dictionary
	)

@pytest.mark.dictionary
def test_nested_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.nested_dictionary = {
		'a' : {'a' : 1}, 
		'b' : {'b' : 2}, 
		'c' : {'c' : 3}
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.nested_dictionary 
		== dictionary.nested_dictionary
	)

@pytest.mark.dictionary
def test_float_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.float_key_dictionary = {
		1.23 : 1, 
		4.56 : 2, 
		7.89 : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.float_key_dictionary 
		== dictionary.float_key_dictionary
	)

@pytest.mark.dictionary
def test_int_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.int_key_dictionary = {
		1 : 1, 
		4 : 2, 
		7 : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.int_key_dictionary 
		== dictionary.int_key_dictionary
	)

@pytest.mark.dictionary
def test_float64_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.float64_key_dictionary = {
		np.float64(1.23) : 1, 
		np.float64(4.56) : 2, 
		np.float64(7.89) : 3
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.float64_key_dictionary 
		== dictionary.float64_key_dictionary
	)

@pytest.mark.dictionary
def test_nested_tuple_key_dictionary_serialization(
        tmp_test_files_dir
):
	dictionary = Dictionary()
	dictionary.nested_tuple_key_dictionary = {
		(1, 2, 3) : {6.6658 : {(9.332, np.float128(5.223)) : 'abc'}}, 
		(4, np.float64(5.2), 6) : {
			np.float64(10.6658) : {
				(9.332, np.float128(5.223)) : 'a81981bc'
			}
		}, 
		(4, 5, 6) : {
			np.float64(10.6658) : {
				(9.332, np.float128(5.223)) : 'a81981bc'
			}
		}, 
	}
	dictionary.serialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	deserialized_dictionary = Dictionary()
	deserialized_dictionary.deserialize(str(
		tmp_test_files_dir /
		"dictionary.xml"
	))
	assert (
		deserialized_dictionary.nested_tuple_key_dictionary == 
		dictionary.nested_tuple_key_dictionary
	)












