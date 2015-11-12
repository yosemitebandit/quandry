"""Camera testing with the beaglebone black and adafruit JPEG camera.

Code from bradsmc.blogspot.com/2013/05/adafruit-ttl-serial-jpeg-camera.html
and the adafruit tutorials.
"""

import serial
import time

import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO


# Initialize serial port, switch and LED.
UART.setup("UART1")
GPIO.setup("P8_10", GPIO.OUT)
GPIO.setup("P8_12", GPIO.IN)


def take_photo():
  """Takes a photo with the TTL camera and writes image to disk."""
  # Initialize camera.
  ser = serial.Serial("/dev/ttyO1", baudrate=38400)
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
  # Write image to file.
  ser.write(
    b'\x56\x00\x32\x0C\x00\x0A\x00\x00\x00\x00\x00\x00%c%c\x00\x0A' % (
      msb, lsb))
  time.sleep(10)
  filename = 'out.jpg'
  resp = ser.read(size=5)
  if b'\x76\x00\x32\x00\x00' in resp:
    with open("/tmp/" + filename, 'wb') as f:
      while ser.inWaiting() > 0:
        data = ser.read()
        f.write('%c' % data)
    print "Image written to /tmp/%s" % (filename)


if __name__ == '__main__':
  # Read the switch and, if it's pressed, turn off the LED and take a photo.
  old_switch_state = 0
  while True:
    GPIO.output('P8_10', GPIO.HIGH)
    new_switch_state = GPIO.input('P8_12')
    if new_switch_state == 1 and old_switch_state == 0:
      GPIO.output('P8_10', GPIO.LOW)
      take_photo()
    old_switch_state = new_switch_state
    time.sleep(0.1)
