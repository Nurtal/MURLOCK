


'''
A few code lines
for the Murlock Project
'''
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import requests
from lxml import html

import random

def sendMailWrapper(fromaddr, toaddr, subject, content, passwd): 
 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject
 
	msg.attach(MIMEText(content, 'plain'))
 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, passwd)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	
	return




def collectCodeFromSOF(url):
	"""
	=> Scan a web page looking for html code
	balise.
	=> Return Balise content in a string array
	
	----------------
	Optimize for StackOverFlow (SOF) : IN PROGRESS

	"""

	page = requests.get(url)
	tree = html.fromstring(page.content)
	code = tree.xpath('//code/text()')

	return code


def scanStackOverFlow(keywords):

	"""
	This function generate random url,
	scan the page subject and compare it to
	the input keywords

	Return the url of selected pages

	[TODO]
	=> parse page title
	=> compare keywords
	=> work on return value
	"""

	# Url Generation
	prefix = "http://stackoverflow.com/questions/"
	for number in range(1, 99999):
		generatedUrl = prefix + str(number) + "/"
		print generatedUrl


	return 0



"""
Test Space
"""


#stuff = collectCodeFromSOF('http://stackoverflow.com/questions/846257/how-can-i-remove-the-last-seven-characters-of-a-hash-value-in-perl')
#print stuff
"""
# Example
page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
tree = html.fromstring(page.content)
#This will create a list of buyers:
buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
prices = tree.xpath('//span[@class="item-price"]/text()')
#print 'Buyers: ', buyers
#print 'Prices: ', prices
"""


#page = requests.get('http://stackoverflow.com/questions/846257/how-can-i-remove-the-last-seven-characters-of-a-hash-value-in-perl')
#tree = html.fromstring(page.content)
#code = tree.xpath('//code/text()')
#print code;






