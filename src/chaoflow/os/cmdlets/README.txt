Introduction
============

The purpose of chaoflow.os.cmdlets is to make execution of cmdlines easy, pain-
and noise-free.

	>>> from chaoflow.os.cmdlets import Cmdlet
	>>> ls = Cmdlet('ls')
	>>> ls('-a1')	
	['.', '..']
