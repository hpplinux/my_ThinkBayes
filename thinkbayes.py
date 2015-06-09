import bisect
import copy
import logging
import math
import numpy
import random


class _DictWrapper(object):
	"""An object that contains a dictionary."""
	
	def __init__(self, values=None, name=''):
		self.name = name
		self.d = {}
		# flag whether the distribution is under a log transform
		self.log = False

		if values is None:
			return

		init_methods = [
				self.InitPmf,
				self.InitMapping,
				self.InitSequence,
				self.InitFailure
				]

		for method in init_methods:
			try:
				method(values)
				break
			except AttributeError:
				continue

		if len(self) > 0:
			self.Normalize()

	def InitSequence(self, values):
		for value in values:
			self.Set(value, 1)

	def InitMapping(self, values):
		for value, prob in values.iteritems():
			self.Set(value, prob)

	def InitPmf(self, values):
		for value, prob in values.Items():
			self.Set(value, prob)

	def InitFailure(self, values):
		raise ValueError('None of the initialization methods worked.')

	def __len__(self):
		return len(self.d)

	def __iter__(self):
		return iter(self.d)

	def iterkeys(self):
		return iter(self.d)

	def __contains__(self, value):
		return value in self.d

	def Copy(self, name=None):
		new = copy.copy(self)
		new.d = copy.copy(self.d)
		new.name = name if name is not None else self.name
		return new

	def Scale(self, factor):
		new = self.Copy()
		new.d.clear()

		for val, prob in self.Items():
			new.Set(val * factor, prob)
		return new

	def Log(self, m=None):
		if self.log:
			raise ValueError("Pmf/Hist already under a log transform")
		self.log = True

		if m is None:
			m = self.MaxLike()

		for x, p in self.d.iteritems():
			if p:
				self.Set(x, math.log(p/m))
			else:
				self.Remove(x)

	def Exp(self, m=None):
		if not self.log:
			raise ValueError("Pmf/Hist not under a log transform")
		self.log = False

		if m is None:
			m = self.MaxLike()

		for x, p in self.d.iteritems():
			self.Set(x, math.exp(p - m))

	def GetDict(self):
		return self.d

	def SetDict(self, d):
		self.d = d

	def Values(self):
		return self.d.keys()
	
	def Items(self):
		return self.d.items()

	def Render(self):
		return zip(*sorted(self.Items()))

	def Print(self):
		for val, prob in sorted(self.d.iteritems()):
			print val, prob

	def Set(self, x, y=0):
		self.d[x] = y

	def Incr(self, x, term=1):
		self.d[x] = self.d.get(x,0) + term

	def Mult(self, x, factor):
		self.d[x] = self.d.get(x, 0) * factor
	
	def Remove(self, x):
		del self.d[x]

	def Total(self):
		total = sum(self.d.itervalues())
		return total

	def MaxLike(self):
		return max(self.d.itervalues())


class Pmf(_DictWrapper):

	def Prob(self, x, default=0):
		return self.d.get(x, default)

	def Probs(self, xs):
		return [self.Prob(x) for x in xs]

	def Normalize(self, fraction=1.0):
		if self.log:
			raise ValueError("Pmf is under a log transform")
		total = self.Total()
		if total == 0.0:
			raise ValueError("total probability is zero.")
			logging.warning('Normalize: total probability is zero.')
			return total

		factor = float(fraction) / total
		for x in self.d:
			self.d[x] *= factor

		return total



class Suite(Pmf):
	
	def Update(self, data):
		for hypo in self.Values():
			like = self.Likelihood(data, hypo)
			self.Mult(hypo, like)
		return self.Normalize()

	def UpdateSet(self, dataset):
		for data in dataset:
			for hypo in self.Values():
				like = self.Likelihood(data, hypo)
				self.Mult(hypo, like)
		return self.Normalize()

	def Likelihood(self, data, hypo):
		raise UnimplementMethodException()

	def Print(self):
		for hypo, prob in sorted(self.Items()):
			print hypo, prob
