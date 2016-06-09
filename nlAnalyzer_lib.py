"""
This file contains
function for the natural
Language analayser

use nltk

=> may have to install corpora
	-> import nltk
	-> nltk.download()
	-> d all-corpora

"""

import nltk



"""
TEST SPACE
"""

text = "DATA/test/test.txt"
data = open(text, "r")
words = []
for line in data:
	line = line.replace("\n", "")
	lineInArray = line.split(" ")
	for word in lineInArray:
		if len(word) > 1:
			words.append(word)




machin = nltk.Text(words)
#print machin[24:62]

machin.collocations()






