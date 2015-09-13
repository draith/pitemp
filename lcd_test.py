#!/usr/bin/python
import io
import time
try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

data = 16
clock = 18
clkwait = 1 # 0.001

MODE_CHR = True
MODE_CMD = False

LCD_WIDTH = 16
LINE_1 = 0x80 # LCD RAM Address
LINE_2 = 0xC0 # LCD RAM Address

def main():
  # Set up GPIO pins
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup((data,clock), GPIO.OUT, initial=GPIO.LOW)
  # Initialise display
  # lcd_init()
  val = None
  while True:
    try:
      ip = input("data:")
      if (ip == 'q'):
        break
      val = ip
    except SyntaxError:
      print 'repeat'
    if (val != None):
      print 'clockdata', val
      clockdata(val)
    # print 'high'
    # GPIO.output(clock,GPIO.HIGH)
    # GPIO.output(data,GPIO.HIGH)
    # time.sleep(1)
    # print 'low'
    # GPIO.output(clock,GPIO.LOW)
    # GPIO.output(data,GPIO.LOW)
    # time.sleep(1)
    # send_string("Raspberry Pi", LINE_1)
    # send_string("16x2 LCD Test", LINE_2)
    # time.sleep(3)
    # send_string("0123456789ABCDEF", LINE_1)
    # send_string("abcdefghijklmnop", LINE_2)
    # time.sleep(3)
    

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

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    # send_byte(0x01, MODE_CMD)
    # send_string("Goodbye!", LINE_1)
    GPIO.cleanup((data,clock))
