import pytest
import unittest

from actone import A, act

class ActOneTests(unittest.TestCase):

	def test_identity(self):
		for i in ['hello', 42, (5, 6, 7, 8), sum]:
			assert act(A, i) is i

	def test_unary(self):
		for i in range(-10, 10):
			assert act(-A, i) == -i

	def test_binary_left(self):
		for i in range(-10, 10):
			assert act(A * 42, i) == i * 42

	def test_binary_right(self):
		for i in range(-10, 10):
			assert act(42 * A, i) == 42 * i

	def test_list_index(self):
		for i in range(100):
			assert act(A[i], range(100)) == i

	def test_dict_index(self):
		test_dict = dict(zip('abcdef','ghijkl'))
		for key, value in test_dict.items():
			assert act(A[key], test_dict) == value

	def test_slice(self):
		for i in range(10):
			seq = range(i, i + 10)
			assert act(A[1:-1:2], seq) == seq[1:-1:2]

	def test_attribute(self):
		class C(object):
			pass

		for i in range(10):
			C.a = i
			assert act(A.a, C) == i

	def test_call(self):
		for i in range(10):
			seq = range(i)
			assert act(A(seq), sum) == sum(seq)

	def test_on_self(self):
		assert act(A, A) is A

	def test_compose_one_level(self):
		ab = act(A['b'], A['a'])
		print act(ab, {'a': {'b': 42}}), 42

	def test_compose_two_levels(self):
		obj = {'a': {'b': {'c': {'d': 'nyaa'}}}}
		ab = A['a']['b']
		cd = A['c']['d']
		abcd = act(cd, ab)
		assert act(abcd, obj) == 'nyaa'