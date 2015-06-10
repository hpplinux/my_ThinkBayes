#!/usr/bin/python
# -*- coding: utf-8 -*-
import bisect  #bisect用于操作排序的数组
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

	def MaximumLikelihood(self):
		prob, val = max((prob, val) for val, prob in self.Items())
		return val

	def Mean(self):
		mu = 0.0
		for x, p in self.d.iteritems():
			mu += p * x
		return mu
	
	def MakeCdf(self, name=None):
		return MakeCdfFromPmf(self, name=name)


def Percentile(pmf, percentage):
	p = percentage / 100.0
	total = 0
	for val, prob in pmf.Items():
		total += prob
		if total >= p:
			return val

def CredibleInterval(pmf, percentage=90):
	cdf = pmf.MakeCdf()
	prob = (1 - percentage / 100.0) / 2
	interval = cdf.Value(prob), cdf.Value(1-prob)
	return interval

def MakeCdfFromPmf(pmf, name=None):
	if name == None:
		name = pmf.name
	return MakeCdfFromItems(pmf.Items(), name)

def MakeCdfFromItems(items, name=''):
	runsum = 0
	xs = []
	cs = []

	for value, count in sorted(items):
		runsum += count
		xs.append(value)
		cs.append(runsum)
	
	total = float(runsum)
	ps = [c/total for c in cs]

	cdf = Cdf(xs, ps, name)
	return cdf



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



class Cdf(object):
	"""
	Attributes:
		xs: sequence of values
		ps: sequence of probabilities
		name: string used as a graph label.
	"""

	def __init__(self, xs=None, ps=None, name=''):
		self.xs = [] if xs is None else xs
		self.ps = [] if ps is None else ps
		self.name = name

	def Copy(self, name=None):
		if name is None:
			name = self.name
		return Cdf(list(self.xs), list(self.ps), name)

	def MakePmf(self, name=None):
		return MakePmfFromCdf(slef, name=name)

	def Values(self):
		return self.xs

	def Items(self):
		return zip(self.xs, self.ps)
	
	def Append(self, x, p):
		self.xs.append(x)
		self.ps.append(p)

	def Shift(self, term):
		"""Adds a term to the xs.
		term: how much to add
		"""
		new = self.Copy()
		new.xs = [x + term for x in self.xs]
		return new

	def Scale(self, factor):
		new = self.Copy()
		new.xs = [x * factor for x in self.xs]
		return new

	def Prob(slef, x):
		if x < self.xs[0]:
			return 0.0
		index = bisect.bisect(self.xs, x)
		#查找该数值将会插入的位置并返回，而不会插入。
		p = self.ps[index - 1]
		return p

	def Value(self, p):
		if p<0 or p>1:
			raise ValueError('Probability p must be in range [0, 1]')

		if p == 0:
			return self.xs[0]
		if p == 1:
			return self.xs[-1]
		index = bisect.bisect(self.ps, p)
		if p == self.xs[index - 1]:
			return self.xs[index - 1]
		else:
			return self.xs[index]

	def Percentile(self, p):
		return self.Value(p/100.0)

	def Ramdom(self):
		return self.Value(random.random())

	def Sample(self,n):
		return [self.Random() for i in range(n)]

	def Mean(self):
		old_p = 0.0
		total = 0.0
		for x, new_p in zip(self.xs, self.ps):
			p = new_p - old_p
			total += p * x
			old_p = new_p
		return total







def MakePmfFromCdf(cdf, name):
	if name is None:
		name = cdf.name
	pmf = Pmf(name=name)

	prev = 0.0
	for val, prob in cdf.Items():
		pmf.Inrc(val, prob - prev)
		prev = prob
	
	return pmf
