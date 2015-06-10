# -*- coding: utf-8 -*-
#!/usr/bin/env python

from thinkbayes import Suite
import thinkbayes

class Euro(Suite):

	def Likelihood(self, data, hypo):
		x = hypo
		if data == 'H':
			return x/100.0
		else:
			return 1 - x/100.0


suite = Euro(range(0,101))
dataset = 'H'*140 + 'T'*110

#for data in dataset:
#	suite.Update(data)
suite.UpdateSet(dataset)

#suite.Print()
print suite.MaximumLikelihood()
print 'Mean', suite.Mean()
print 'Median', thinkbayes.Percentile(suite, 50)
print 'CI', thinkbayes.CredibleInterval(suite, 90)
