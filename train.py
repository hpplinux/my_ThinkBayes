# -*- coding: utf-8 -*-
#!/usr/bin/env python

from thinkbayes import Suite
from thinkbayes import Pmf
import matplotlib.pyplot as plt
import numpy as np

class Dice(Suite):
	def Likelihood(self, data, hypo):
		if hypo < data:
			return 0
		else:
			return 1.0/hypo

class Train(Dice):
	def __init__(self, hypo, alpha = 1.0):
		Pmf.__init__(self)
		for hypo in hypos:
			self.Set(hypo, hypo**(-alpha))
		self.Normalize()

hypos = range(1,1001)
suite = Train(hypos)
arr =  np.array(suite.Items())
plt.plot(arr[:,0],arr[:,1])
plt.xticks(range(0,1000,100))
plt.show()
