#!/usr/bin/python

from lcd_display import *
try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


# Set up GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup((data,clock), GPIO.OUT, initial=GPIO.LOW)

while True:
  line1 = raw_input('Line 1: ')
  if (line1 == ''):
    break
  line2 = raw_input('Line 2: ')
  lcd_init()
  send_string(line1, LINE_1)
  send_string(line2, LINE_2)
