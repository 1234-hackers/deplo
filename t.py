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

