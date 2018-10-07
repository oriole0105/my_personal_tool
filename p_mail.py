#!/usr/local/bin/python3.4
# Import smtplib for the actual sending function
#import smtplib

# Import the email modules we'll need
#from email.message import EmailMessage

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys
import getopt



sender = 'oriole0105work1@gmail.com'
passwd = ''
receivers = 'oriole0105.qfs6r@sync.omnigroup.com'

msg = MIMEMultipart()
part = MIMEText(sys.argv[2])
msg.attach(part)

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] =  sys.argv[1]
msg['From'] = sender
msg['To'] = receivers

# Send the message via our own SMTP server.
s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.login(sender, passwd)
s.sendmail(msg['From'], receivers , msg.as_string())

#s.send_message(msg)
s.quit()
