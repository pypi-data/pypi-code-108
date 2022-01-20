import bifs
import os
import numpy as np

def test_simple():
	b = bifs.BIFS()
	b.load_image_file("tests/images/lena512.bmp")
	b.BIFS_MAP()
	assert (b.prior_object().var() == b.prior_object().sd()**2).all()

def test_reset():
	b = bifs.BIFS()
	b.load_image_file("tests/images/lena512.bmp")
	b.BIFS_MAP()

	b2 = bifs.BIFS()
	b2.load_image_file("tests/images/lena512.bmp")
	b2.BIFS_MAP()
	b2.set_prior_func_type("Linear Decay")
	b2.BIFS_MAP()

	assert b.bas == b2.bas
	assert (b.prior_object().mean() != b2.prior_object().mean()).any()
	assert b.prior_object().name() != b2.prior_object().name()

def test_reset2():
	b = bifs.BIFS()
	b.load_image_file("tests/images/lena512.bmp")
	b.BIFS_MAP()

	b2 = bifs.BIFS()
	b2.set_prior_func_type("Linear Decay")
	b2.load_image_file("tests/images/lena512.bmp")
	b2.BIFS_MAP()


	assert b.bas == b2.bas
	assert (b.prior_object().mean() != b2.prior_object().mean()).any()
	assert b.prior_object().name() != b2.prior_object().name()

def test_inverse():
	b = bifs.BIFS()
	b.set_prior_func_type("Banded Inverse Power Decay")
	b.load_image_file("tests/images/lena512.bmp")
	b.BIFS_MAP()

