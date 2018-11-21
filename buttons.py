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

left_button = 35 #11
mid_button = 37 #13
both_buttons = (left_button,mid_button)

#switching_cam = False

def left_button_pressed(channel):
  #global switching_cam
  print("left button pressed")
  if GPIO.input(left_button) == GPIO.LOW:
    # Toggle display between camera control and temperature display
    set_switching_cam(not switching_cam())
    if switching_cam():
      print("switching_cam TRUE")
      # Wait while temperature display is updating
      while lcd_is_locked():
        time.sleep(0.3)
      # Prevent temperature display from overwriting status display.
      lock_lcd()
      # Display pycam status.
      disp_status()
    else:
      print("switching_cam FALSE")
      # Display current time/temp
      show_temp()
      # Unlock display for further temperature updates
      unlock_lcd()
    # debounce
    print("debounce sleep 0.3")
    time.sleep(0.3)

def pycam_running():
  tmp = os.popen("ps -Af").read()
  return True if tmp.count('pycam.py') > 0 else False

def disp_status():
  if time.strftime("%d%m") == "3011":
    lcd_init()
    send_string("HAPPY BIRTHDAY", LINE_1)
    send_string("HOLLY! %s"%("GREEN" if pycam_running() else "RED"), LINE_2)
  elif time.strftime("%d%m") == "2307":
    lcd_init()
    send_string("HAPPY BIRTHDAY", LINE_1)
    send_string("LUCY! %s"%("GREEN" if pycam_running() else "RED"), LINE_2)
  elif time.strftime("%d%m") == "3107":
    lcd_init()
    send_string("HAPPY BIRTHDAY", LINE_1)
    send_string("EWAN! %s"%("GREEN" if pycam_running() else "RED"), LINE_2)
  else:
    send_string("Status: %s"%("GREEN" if pycam_running() else "RED"), LINE_2)

def mid_button_pressed(channel):
  if switching_cam() and GPIO.input(mid_button) == GPIO.LOW:
    send_string("Status: ...", LINE_2)
    try:
      # Toggle pycam state..
      subprocess.check_call(["sudo","/etc/init.d/pycam", "stop" if pycam_running() else "start"])
      # Prevent temperature display from overwriting status display.
      lock_lcd()
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
