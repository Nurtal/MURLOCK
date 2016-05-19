


'''
A few code lines
for the Murlock Project
'''
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import requests
from lxml import html

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



page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
tree = html.fromstring(page.content)
#This will create a list of buyers:
buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
prices = tree.xpath('//span[@class="item-price"]/text()')
print 'Buyers: ', buyers
print 'Prices: ', prices

