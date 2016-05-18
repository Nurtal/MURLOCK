


'''
A few code lines
for the Murlock Project
'''

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
 
 
fromaddr = "murlock.raspberypi@gmail.com"
toaddr = "fingolfinfingril@yahoo.fr"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Step one"
 
body = "GRMBMBLBLBLBLBLBMMMMLLL"
msg.attach(MIMEText(body, 'plain'))
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "IamNotStupidEnoughToWriteMyPasswordThere")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()


