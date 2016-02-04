# -*- coding: utf-8 -*-
import smtplib
import json
from email.mime.text import MIMEText

users = dict()
with open("data_user1.json", "r") as fi:
	users = json.loads(fi.read())
for user in users:
	print(user["fields"]["name"])
	content = str()
	content += 'Dear %s,\n\nThe system is open now\nhttp://140.112.107.147:8000/label/login\n\n' % user["fields"]["name"]
	content += 'Your account: %s\nYour password: %s\n\n' % (user["fields"]["account"], user["fields"]["pwd"])
	content += 'If there is any problem about the system or slide, feel free to contact me by e-mail\n\nThank you and Best Wishes,\nKen Chen' 
	gmail_user = 'sychen1990@gmail.com'
	gmail_pwd = 'OUou09087358'

	smtpserver = smtplib.SMTP("smtp.gmail.com",587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo()
	smtpserver.login(gmail_user, gmail_pwd)

	text_subtype = 'text'
	msg = MIMEText(content.encode('utf-8'), 'plain', 'UTF-8')
	msg['From']="sychen1990@gmail.com"
	msg['MIME-Version']="1.0"
	msg['Subject']="熱門及前瞻議題-使用者帳號與密碼"
	msg['Content-Type'] = "text; charset=utf-8"
	msg['Content-Transfer-Encoding'] = "quoted-printable"

	fromaddr = "sychen1990@gmail.com"
	toaddrs = ['sychen1990@gmail.com', user["fields"]["account"]]

	smtpserver.sendmail(fromaddr, toaddrs, str(msg))
	smtpserver.quit()