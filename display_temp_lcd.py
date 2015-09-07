#!/usr/bin/python
import io
import time
execfile("lcd_display.py")

f = open('/sys/bus/w1/devices/28-000007099503/w1_slave','r')
file_content = f.read()
f.close()
pos = file_content.rfind('t=')
if (pos > 0):
  val = int(file_content[pos+2:])/float(1000)
  timestr = time.strftime("%H:%M")
  
  # Set up GPIO pins
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup((data,clock), GPIO.OUT, initial=GPIO.LOW)
  # Initialise display
  lcd_init()
  send_string("{0}    {1:.1f}\xdfC".format(timestr, val), LINE_1)
  GPIO.cleanup((data,clock))
 