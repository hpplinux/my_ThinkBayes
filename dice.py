# -*- coding: utf-8 -*-
#!/usr/bin/env python

from thinkbayes import Suite

class Dice(Suite):
	def Likelihood(self, data, hypo):
		if hypo < data:
			return 0
		else:
			return 1.0/hypo



suite = Dice([4, 6, 8, 12, 20])
suite.Update(6)
suite.Print()
