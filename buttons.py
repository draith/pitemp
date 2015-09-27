#!/usr/bin/python

# SCRIPT TO ALLOW CONTROL VIA TWO BUTTONS (connected to pins 11 and 13).
import os
import time
import subprocess
from lcd_display import *
from display_temp_lcd import show_temp

try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

left_button = 11
mid_button = 13
both_buttons = (left_button,mid_button)

switching_cam = False

def left_button_pressed(channel):
  global switching_cam
  
  if GPIO.input(left_button) == GPIO.LOW:
    # Toggle display between camera control and temperature display
    switching_cam = not switching_cam
    if switching_cam:
      # Prevent temperature display from overwriting status display.
      lock_lcd()
      # Display pycam status.
      disp_status()
    else:
      # Display current time/temp
      show_temp()
      # Unlock display for further temperature updates
      unlock_lcd()
    # debounce
    time.sleep(0.3)

def pycam_running():
  tmp = os.popen("ps -Af").read()
  return True if tmp.count('pycam.py') > 0 else False

def disp_status():
  send_string("Status: %s"%("ON" if pycam_running() else "OFF"), LINE_2)

def mid_button_pressed(channel):
  if switching_cam and GPIO.input(mid_button) == GPIO.LOW:
    send_string("Status: ...", LINE_2)
    try:
      # Toggle pycam state..
      subprocess.check_call(["sudo","/etc/init.d/pycam", "stop" if pycam_running() else "start"])
      disp_status()
    except:
      send_string("Status: EXCEPTION", LINE_2)
      
    
# Set up GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(both_buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup((data,clock), GPIO.OUT, initial=GPIO.LOW)

GPIO.add_event_detect(left_button, GPIO.FALLING, bouncetime=200)
GPIO.add_event_detect(mid_button, GPIO.FALLING, bouncetime=200)
GPIO.add_event_callback(left_button, left_button_pressed)
GPIO.add_event_callback(mid_button, mid_button_pressed)

while True:
  time.sleep(999)
