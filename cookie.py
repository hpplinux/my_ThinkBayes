#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from thinkbayes import Pmf

pmf1 = Pmf()
for x in range(1, 6 + 1):
	pmf1.Set(x, 1/6.0)

pmf1.Print()

print ("曲奇饼问题")
pmf2 = Pmf()
pmf2.Set('Bowl1', 0.5)
pmf2.Set('Bowl2', 0.5)

pmf2.Mult('Bowl1', 0.75)
pmf2.Mult('Bowl2', 0.5)

pmf2.Normalize()
print pmf2.Probs(pmf2.Values())
