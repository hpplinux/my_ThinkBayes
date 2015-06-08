from thinkbayes import Pmf

pmf = Pmf()
for x in range(1, 6 + 1):
	pmf.Set(x, 1/6.0)

pmf.Print()
