# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tnorms.base import BaseTNorm

from typing import Optional


class AdditiveLinearGenerator(BaseTNorm):
	def __init__(self, vec_size: int = 1) -> None:
		super().__init__()

		self.vec_size = vec_size
		function = torch.randn(vec_size)
		self.function =  nn.Parameter(function)
		# self.relu = torch.nn.ReLU()


	def __call__(self,
				 a: Tensor,
				 b: Tensor) -> Tensor:
		t_norm: Optional[Tensor] = None

		monotonic_function = torch.exp(self.function)

		gen_a = monotonic_function * (1 - a)
		gen_b = monotonic_function * (1 - b)

		t_norm = gen_a + gen_b
		t_norm = torch.minimum(monotonic_function, t_norm)
		t_norm = (monotonic_function - t_norm) / monotonic_function

		return t_norm


class AdditiveGenerator(BaseTNorm):
	def __init__(self, vec_size: int = 1) -> None:
		super().__init__()

		self.vec_size = vec_size
		function = torch.empty(vec_size,vec_size)
		torch.nn.init.xavier_uniform_(function)
		self.function =  nn.Parameter(function)
		self.relu = torch.nn.ReLU()


	def __call__(self,
				 a: Tensor,
				 b: Tensor) -> Tensor:
		t_norm: Optional[Tensor] = None


		# This Kinda becomes an enforced positive attention/ranking across the sorted candidate scores
		# As we learn what weighted linear combination the candidates yields
		monotonic_function = torch.exp(self.function)

		gen_a = monotonic_function @ (1 - a)
		gen_b = monotonic_function @ (1 - b)

		t_norm = gen_a + gen_b
		t_norm = torch.minimum(monotonic_function @ torch.ones(self.vec_size), t_norm)
		t_norm = (torch.inverse(monotonic_function) @ (-t_norm)) + 1
		t_norm = self.relu(t_norm)

		return t_norm


class AdditiveOrthogonalGenerator(BaseTNorm):
	def __init__(self, vec_size: int = 1) -> None:
		super().__init__()

		self.vec_size = vec_size
		self._lambda = 100
		function = torch.empty(vec_size,vec_size)
		torch.nn.init.xavier_uniform_(function)
		self.function =  nn.Parameter(function)

		# self.relu = torch.nn.ReLU()


	def __call__(self,
				 a: Tensor,
				 b: Tensor) -> Tensor:
		t_norm: Optional[Tensor] = None


		monotonic_function = torch.exp(self.function)

		regularizer = self._lambda* torch.pow(torch.norm(( monotonic_function @ monotonic_function.T) - torch.eye(self.vec_size) ,  p='fro'), 2)

		gen_a = monotonic_function @ (1 - a)
		gen_b = monotonic_function @ (1 - b)

		t_norm = gen_a + gen_b

		t_norm = torch.minimum(monotonic_function @ torch.ones(self.vec_size), t_norm)
		t_norm = (monotonic_function.T @ (-t_norm)) + 1

		return t_norm, regularizer


class AdditiveLearnableInverseGenerator(BaseTNorm):
	def __init__(self, vec_size: int = 1) -> None:
		super().__init__()

		self.vec_size = vec_size

		function = torch.empty(vec_size,vec_size)
		torch.nn.init.xavier_uniform_(function)
		self.function =  nn.Parameter(function)

		function_inverse = torch.empty(vec_size,vec_size)
		torch.nn.init.xavier_uniform_(function_inverse)
		self.function_inverse =  nn.Parameter(self.function)
		# self.relu = torch.nn.ReLU()


	def __call__(self,
				 a: Tensor,
				 b: Tensor) -> Tensor:
		t_norm: Optional[Tensor] = None

		monotonic_function = torch.exp(self.function)
		monotonic_function_inverse = torch.exp(self.function_inverse)

		gen_a = monotonic_function @ (1 - a)
		gen_b = monotonic_function @ (1 - b)

		t_norm = gen_a + gen_b

		t_norm = torch.minimum(monotonic_function @ torch.ones(self.vec_size), t_norm)
		t_norm = (monotonic_function_inverse @ (-t_norm)) + 1

		return t_norm

class AdditivePolynomialGenerator(BaseTNorm):
	def __init__(self, vec_size: int = 1, default_p: int = 0.1) -> None:
		super().__init__()

		self.vec_size = vec_size
		self.power =  nn.Parameter(torch.tensor(default_p))
		function = torch.randn(vec_size)
		self.function =  nn.Parameter(function)
		self.relu = torch.nn.ReLU()


	def __call__(self,
				 a: Tensor,
				 b: Tensor) -> Tensor:
		t_norm: Optional[Tensor] = None

		monotonic_function = torch.exp(1 + self.function)
		power = 1 + torch.exp(self.power)

		gen_a = monotonic_function * (1 - a ** power)
		gen_b = monotonic_function * (1 - b ** power)

		t_norm = gen_a + gen_b

		t_norm = torch.minimum(monotonic_function,t_norm)
		t_norm = ((monotonic_function - t_norm) ** (1 / power)) * (1 / (monotonic_function)) ** (1/power)

		return t_norm


# (1-a)/x^p

# class AdditiveLinearGenerator(BaseTNorm):
# 	def __init__(self, vec_size: int = 1) -> None:
# 		super().__init__()
#
# 		self.vec_size = vec_size
# 		self._lambda = 100
# 		self.function = torch.exp(torch.randn(vec_size,vec_size))
# 		self.function =  nn.Parameter(self.function)
# 		# self.relu = torch.nn.ReLU()
#
#
# 	def __call__(self,
# 				 a: Tensor,
# 				 b: Tensor) -> Tensor:
# 		t_norm: Optional[Tensor] = None
#
# 		regularizer = torch.pow(torch.norm((self.function @ self.function.T) - torch.eye(self.vec_size) ,  p='fro'), 2)
# 		# t_norm = ((1.0 / (-self.function@(a-1) + -self.function@(b-1))) @ self.function.T) + self._lambda * regularizer
# 		gen_a = self.function @ (1 - a)
# 		gen_b = self.function @ (1 - b)
#
# 		t_norm = gen_a + gen_b
# 		t_norm = (-t_norm @ self.function.T) + 1
#
# 		return t_norm, regularizer
# #
#
# class AdditiveNonLinearGenerator(BaseTNorm):
# 	def __init__(self, vec_size: int = 1) -> None:
# 		self.vec_size = vec_size
# 		self._lambda = 100
# 		self.function = torch.normal(vec_size,vec_size)
# 		self.function =  nn.Parameter(self.function)
# 		# self.relu = torch.nn.ReLU()
# 		super().__init__()
#
#
# 	def __call__(self,
# 				 a: Tensor,
# 				 b: Tensor) -> Tensor:
# 		t_norm: Optional[Tensor] = None
#
# 		regularizer = torch.pow(torch.norm((self.function @ self.function.T) - torch.eye(self.vec_size) ,  p='fro'), 2)
#
# 		gen_a = torch.exp(self.function@a) * (1 - a)
# 		gen_b = torch.exp(self.function@b) * (1 - b)
#
# 		t_norm = gen_a+gen_b
# 		t_norm = torch.exp(self.function@(-t_norm)) * (1.0 / (1 - t_norm))
# 		return t_norm
