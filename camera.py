"""Camera testing with the beaglebone black and Adafruit JPEG camera.

Code from bradsmc.blogspot.com/2013/05/adafruit-ttl-serial-jpeg-camera.html

Usage:
  camera.py [--outdir=/home/test]

Options:
  --outdir: where to save output files (defaults to /tmp)
"""

import os
import serial
import time

import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO
from docopt import docopt


# Initialize serial port, switch and LED.
UART.setup("UART1")
ser = serial.Serial("/dev/ttyO1", baudrate=38400)
GPIO.setup("P8_10", GPIO.OUT)
GPIO.setup("P8_12", GPIO.IN)


def take_photo():
  """Takes a photo with the TTL camera."""
  print 'Taking photo..'
  # Initialize camera.
  ser.write(b'\x56\x00\x26\x00')
  resp = ""
  time.sleep(1)
  while ser.inWaiting() > 0:
    data = ser.read()
    resp += data
    if "Init end\r\n" in resp:
      print "Ready"
      break
  # Set image size to 640 x 480.
  ser.write(b'\x56\x00\x54\x01\x00')
  resp = ""
  time.sleep(1)
  while ser.inWaiting() > 0:
    data = ser.read()
    resp += data
    if b'\x76\x00\x54\x00\x00' in resp:
      print "Size set"
      break
  # Take picture.
  ser.write(b'\x56\x00\x36\x01\x00')
  resp = ""
  time.sleep(2)
  while ser.inWaiting() > 0:
    data = ser.read()
    resp += data
    if b'\x76\x00\x36\x00\x00' in resp:
      print "Picture taken"
      break


def save_photo(outdir='/tmp'):
  """Writes image to file.  We'll use integer filenames and won't overwrite.

  kwargs:
    outdir: where to save the output file.
  """
  # Get JPG size.
  ser.write(b'\x56\x00\x34\x01\x00')
  resp = ""
  time.sleep(1)
  while ser.inWaiting() > 0:
    data = ser.read()
    resp += data
    if b'\x76\x00\x34\x00\x04\x00\x00' in resp:
      msb = ser.read()
      lsb = ser.read()
      print "Image file size: %d bytes" % (ord(msb) << 8 | ord(lsb))
  ser.write(
    b'\x56\x00\x32\x0C\x00\x0A\x00\x00\x00\x00\x00\x00%c%c\x00\x0A' % (
      msb, lsb))
  time.sleep(10)
  # Create outdir if it doesn't exist.
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  # Find any existing image files in the outdir.
  files = [f for f in os.listdir(outdir) if '.jpg' in f]
  numbers = [int(f.strip('.jpg')) for f in files]
  numbers = sorted(numbers)
  if not numbers:
    filename = '0.jpg'
  else:
    filename = '%s.jpg' % (numbers[-1] + 1)
  filepath = os.path.join(outdir, filename)
  resp = ser.read(size=5)
  if b'\x76\x00\x32\x00\x00' in resp:
    with open(filepath, 'wb') as f:
      while ser.inWaiting() > 0:
        data = ser.read()
        f.write('%c' % data)
    print "Image written to %s" % filepath


if __name__ == '__main__':
  args = docopt(__doc__)
  # If the switch is pressed, turn off the LED and take a photo.
  old_switch_state = 0
  while True:
    GPIO.output('P8_10', GPIO.HIGH)
    new_switch_state = GPIO.input('P8_12')
    if new_switch_state == 1 and old_switch_state == 0:
      GPIO.output('P8_10', GPIO.LOW)
      take_photo()
      if not args['--outdir']:
        save_photo()
      else:
        save_photo(outdir=args['--outdir'])
    old_switch_state = new_switch_state
