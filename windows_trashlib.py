'''
A few code lines
for the Murlock Project

=> Designed for windows
=> python 3.4

Nothing Seems to Work

'''

import random


def scanStackOverFlow(keywords):

	"""
	This function generate random url,
	scan the page subject and compare it to
	the input keywords

	[TODO]
	=> adapt to linux python 2.7
	=> parse page title
	=> compare keywords
	=> work on return value
	"""


	prefix = "http://stackoverflow.com/questions/"
	for number in range(1, 99999):
		generatedUrl = prefix + str(number) + "/"
		print generatedUrl

	return 0

scanStackOverFlow("test")