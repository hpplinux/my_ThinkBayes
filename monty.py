#!/usr/bin/env python
# -*- coding: utf-8 -*-

from thinkbayes import Pmf

class Monty(Pmf):

	def __init__(self, hypos):
		Pmf.__init__(self)
		for hypo in  hypos:
			self.Set(hypo, 1)
		self.Normalize()

	def Update(self, data):
		for hypo in self.Values():
			like = self.Likelihood(data, hypo)
			self.Mult(hypo, like)
		self.Normalize()

	def Likelihood(self, data, hypo):
		if hypo==data:
			return 0
		elif hypo == 'A':
			return 0.5
		else:
			return 1


hypos = 'ABC'

pmf = Monty(hypos)
pmf.Update('B')

for hypo, prob in pmf.Items():
	print hypo, prob
