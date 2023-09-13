import os

import random

import time

from datetime import  datetime as dt
st = "Hello,my name is elon"

if "elon" in st:
	print("Found")
else:
	print("No")

me = "kim@gmail.com"
me2 = me.replace("." , "")

if  os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
	print("yeah")
else:
	print("oh no")


stc = "My name is James"

st2 = stc.split()

print(st2)


x = random.randint(2,5)

print(x)


def timez():
	now = dt.now()
	now3 = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")

	time.sleep(196)
	now2 = dt.now()
	nextz =  now2.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
	print("Now" + str(now3))
	print("date " + str(now3)[14:16])
	print("Time " + str(now3)[23:28])

	cr = str(now3)[23:28]
	first_min = cr[3:5]
	first_hour = cr[0:2]

	
	

	cr2 = str(nextz)[23:28]
	second_min = cr2[3:5]
	second_hour = cr2[0:2]

	dif = int(second_min) - int(first_min)
	hours = int(first_hour) - int(second_hour)
	if dif < 0:
		dif = dif + 60
		hours = int(first_hour) - 1
	
	return dif
	


timez()


import logging
from logging.handlers import RotatingFileHandler


# Set the log level (you can adjust this as needed)
app.logger.setLevel(logging.INFO)

# Create a log file and set up logging to that file
log_file = "your_app.log"
handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
handler.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the app's logger
app.logger.addHandler(handler)


import smtplib

# SMTP server configuration
smtp_server = 'your_smtp_server.com'  # Replace with your SMTP server's hostname or IP address
smtp_port = 587  # This is the default port for secure SMTP (TLS)
smtp_username = 'your_username'
smtp_password = 'your_password'

# Create an SMTP connection
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Enable TLS encryption for secure connection
    server.login(smtp_username, smtp_password)

    # Compose your email
    subject = 'Your Subject Here'
    body = 'Your email body here'
    from_email = 'your_email@example.com'
    to_email = 'recipient@example.com'
    message = f'Subject: {subject}\n\n{body}'

    # Send the email
    server.sendmail(from_email, to_email, message)
    print('Email sent successfully')

except Exception as e:
    print(f'An error occurred: {str(e)}')

finally:
    server.quit()  # Close the SMTP connection


