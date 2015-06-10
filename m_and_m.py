# -*- coding: utf-8 -*-
#!/usr/bin/env python

from thinkbayes import Suite

class M_and_M(Suite):

	mix94 = dict(brown = 30,
				yellow = 20,
				red = 20,
				green = 10,
				orange = 10,
				tan = 10)
	mix96 = dict(blue = 24,
				green = 20,
				orange = 16,
				yellow = 14,
				red = 13,
				brown = 13)

	hypoA = dict(bag1 = mix94, bag2 = mix96)
	hypoB = dict(bag1 = mix96, bag2 = mix94)
	hypotheses = dict(A = hypoA, B = hypoB)

	def Likelihood(self, data, hypo):
		bag, color = data
		mix = self.hypotheses[hypo][bag]
		like = mix[color]
		return like

suite = M_and_M('AB')

suite.Update(('bag1', 'yellow'))
suite.Update(('bag2', 'green'))
suite.Print()
