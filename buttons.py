#!/usr/bin/python

# SCRIPT TO ALLOW CONTROL VIA TWO BUTTONS (connected to pins 11 and 13).
import os
import time

try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

left_count = 0
mid_count = 0
left_button = 11
mid_button = 13
both_buttons = (left_button,mid_button)

def left_button_pressed(channel):
  global left_count
  if GPIO.input(left_button) == GPIO.LOW:
    left_count += 1
    print('Left button pressed %s times'%left_count)

def mid_button_pressed(channel):
  global mid_count
  if GPIO.input(mid_button) == GPIO.LOW:
    mid_count += 1
    print('Left button pressed %s times'%mid_count)

  # Set up GPIO pin
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(both_buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(left_button, GPIO.FALLING, bouncetime=200)
GPIO.add_event_detect(mid_button, GPIO.FALLING, bouncetime=200)
GPIO.add_event_callback(left_button, left_button_pressed)
GPIO.add_event_callback(mid_button, mid_button_pressed)

while True:
  time.sleep(999)
