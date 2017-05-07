#!/usr/bin/python
import io
import time
import os
try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

data = 16
clock = 18
clkwait = 0.0001
lcd_lock_file_path = '/var/ram/lcd_locked'
switching_cam_file_path = '/var/ram/switching_cam'

MODE_CHR = True
MODE_CMD = False

LCD_WIDTH = 16
LINE_1 = 0x80 # LCD RAM Address
LINE_2 = 0xC0 # LCD RAM Address

def lcd_is_locked():
  return os.path.exists(lcd_lock_file_path)

def lock_lcd():
  if not lcd_is_locked():
    f = open(lcd_lock_file_path,'w')
    f.close()

def unlock_lcd():
  if lcd_is_locked():
    os.remove(lcd_lock_file_path)

def switching_cam():
  return os.path.exists(switching_cam_file_path)

def set_switching_cam(set_on):
  if set_on:
    if not switching_cam():
      f = open(switching_cam_file_path,'w')
      f.close()
  elif switching_cam():
    os.remove(switching_cam_file_path)

def setdata(value):
  GPIO.output(data, GPIO.HIGH if value else GPIO.LOW)
  
def tick():
  GPIO.output(clock,GPIO.HIGH)
  time.sleep(clkwait)
  GPIO.output(clock,GPIO.LOW)
  time.sleep(clkwait)

def clockdata(value):
  setdata(value)
  tick()
  
def send_hi_nibble(value, mode):
  # mode = True for char, False for command
  
  # First, clock 8 zero bits into the shift register...
  setdata(0)
  for i in range(8):
    tick()
  # Now set high bit for E
  clockdata(1)
  # Now set RS signal
  clockdata(mode)
  # Shift in top 4 bits
  mask = 0x80
  for i in range(4):
    clockdata(value & mask)
    mask >>= 1
  # Shift all into place with a zero data value to ensure no E pulse
  clockdata(0)
  # Now toggle data line to generate E pulse
  setdata(1)
  time.sleep(clkwait)
  setdata(0)
  
def send_byte(value, mode):
  # mode = True for char, False for command
  send_hi_nibble(value, mode)
  send_hi_nibble(value << 4, mode)

def lcd_init():
  send_byte(0x33,MODE_CMD) # 110011 Initialise
  send_byte(0x32,MODE_CMD) # 110010 Initialise
  send_byte(0x06,MODE_CMD) # 000110 Cursor move direction
  send_byte(0x0C,MODE_CMD) # 001100 Display On, Cursor Off, Blink Off
  send_byte(0x28,MODE_CMD) # 101000 Data length, number of lines, font size
  send_byte(0x01,MODE_CMD) # 000001 Clear display

def send_string(message,line):
  # Send string to display
  # line = LINE_1 or LINE_2
  message = message.ljust(LCD_WIDTH," ")  
  #print "send_string(" , message, ")"
  # Specify line to update
  send_byte(line, MODE_CMD)
  # Send string
  for i in range(LCD_WIDTH):
    send_byte(ord(message[i]), MODE_CHR)
