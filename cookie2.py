#!/usr/bin/env python
# -*- coding: utf-8 -*-

from thinkbayes import Pmf

class Cookie(Pmf):

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

	mixes = {'Bowl1':dict(vanilla=0.75, chocolate=0.25),			'Bowl2':dict(vanilla=0.5, chocolate=0.5)}

	"""
	Likelihood实际上就是一个条件概率，
	根据hypo选出哪一个碗，再根据data选出哪一种cookie，
	即：先选出一个碗之后，从此碗中选出某种cookie的概率。
	"""
	def Likelihood(self, data, hypo):
		mix = self.mixes[hypo]
		like = mix[data]
		return like




hypos = ['Bowl1', 'Bowl2']
pmf = Cookie(hypos)
pmf.Update('vanilla')  #拿到一个香草曲奇，求是从哪个碗拿的概率

print("若拿到一个vanilla cookie，则是从Bowl1和Bowl2拿的概率如下：")
for hypo, prob in pmf.Items():
	print hypo, prob
