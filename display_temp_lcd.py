#!/usr/bin/python
import io
import time
import os.path
import sys
from lcd_display import *

maxfilepath = '/var/ram/maxtemp.txt'
minfilepath = '/var/ram/mintemp.txt'

def show_temp():
  f = open('/sys/bus/w1/devices/28-011620e000ee/w1_slave','r')
  file_content = f.read()
  f.close()
  pos = file_content.rfind('t=')
  if (pos <= 0):
    return
  val = int(file_content[pos+2:])/float(1000)
  datestr = time.strftime("%a %H:%M")
  timestr = time.strftime("%H:%M")
  # Get Max and Min temperature for today
  if (timestr != "00:00" and os.path.exists(maxfilepath)):
    maxfile = open(maxfilepath,'r')
    maxtemp = float(maxfile.read())
    maxfile.close()
    minfile = open(minfilepath,'r')
    mintemp = float(minfile.read())
    minfile.close()
  else:
    # start of day or no recorded max/min:
    # ensure we record current temperature as max and min
    maxtemp = val-1
    mintemp = val+1
 
  # update recorded max/min as needed
  if (val > maxtemp):
    maxtemp = val
    maxfile = open(maxfilepath,'w')
    maxfile.write(str(maxtemp))
    maxfile.close()
  if (val < mintemp):
    mintemp = val
    minfile = open(minfilepath,'w')
    minfile.write(str(mintemp))
    minfile.close()
    
  # Set up GPIO pins
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup((data,clock), GPIO.OUT, initial=GPIO.LOW)
  # Initialise display
  lcd_init()
  # Display day, time, current temperature. (\xdf is the degree symbol)
  if (val <= -10):
    send_string("{0}{1:.1f}\xdfC".format(datestr, val), LINE_1)
  else:
    send_string("{0} {1:.1f}\xdfC".format(datestr, val), LINE_1)
  # Display max/min (only min before noon)
  if (timestr >= "12:00"):
    send_string("Hi {0:.1f} Lo {1:.1f}".format(maxtemp,mintemp), LINE_2)
  else:
    send_string("    Lo {1:.1f}".format(maxtemp,mintemp), LINE_2)
#  GPIO.cleanup((data,clock)) # occasionally messes up the display..
 

if __name__ == "__main__":
  # Don't do anything this time if the LCD is locked by buttons.py
  # - just unlock so next run will display
  if lcd_is_locked():
    unlock_lcd()
  else:
    lock_lcd()
    show_temp()
    set_switching_cam(False)
    unlock_lcd()
