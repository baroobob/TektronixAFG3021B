# Copyright 2009 Jim Bridgewater

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# 11/03/09 Jim Bridgewater
# Adapted this from code written for the Keithley 2400. 

#################################################################
# The user functions defined in this module are:
#################################################################
# open_serial_port(serial_port = "COM4"):
# set_amplitude(voltage):
# set_offset(voltage):
# set_frequency(frequency):
# enable_output():
# disable_output():
# close_serial_port():

#################################################################
# Import libraries
#################################################################
import sys, time, serial
from errors import Error

#################################################################
# Global Declarations
#################################################################
Debug = 0  # set to 1 to enable printing of error codes
READING_AVAILABLE = 1 << 6

#################################################################
# Function definitions
#################################################################

# This function opens the virtual serial port created by the Prologix
# USB/GPIB interface and sets up the parameters required to communicate
# with the Tektronix AFG3021B.
def open_serial_port(serial_port = "COM5"):
  global ser
  try:
    # open serial port, 9600 baud, 8 data bits, no parity, 1 stop bit,
    # 5 second time out, no software flow control, RTS/CTS flow control
    # these settings were copied from hyperterminal
    ser = serial.Serial(serial_port,9600,8,'N',1,5,0,1)
    ser.write("++rst\r\n")      # reset Prologix
    time.sleep(7)                # Prologix reset requires several seconds
    ser.write("++mode 1\r\n")    # put Prologix in controller mode
    ser.write("++auto 0\r\n")    # turn off Prologix Read-After-Write mode
    ser.write("++addr 11\r\n")  # set GPIB address to the AFG3021B
    ser.write("*RST\r\n")        # Reset instrument
    ser.write("*IDN?\r\n")      # ask instrument to identify itself
    ser.write("++read 10\r\n")
    reading = ser.readline()    # make sure instrument is turned on 
    if not "TEKTRONIX,AFG3021B" in reading:
      raise Error("ERROR: The Tektronix AFG3021B is not responding, make "\
      "sure it is turned on.")
  except serial.SerialException:
    raise Error("ERROR: Unable to open the USB communication link to the "\
    "Tektronix AFG3021B, make sure it is plugged in.")
    


# This function sets the peak to peak amplitude of the function 
# generator's output.
def set_amplitude(amplitude):
  write("VOLTAGE:OFFSET?")      # read present offset voltage
  write("++read 10")
  offset = float(ser.readline())
  if (amplitude < 10e-3):
    print 'Warning: The minimum peak to peak amplitude for the AFG3021B '\
    'is 10 mV.'
    amplitude = 10e-3
  if (abs(amplitude/2) + abs(offset) > 5):
    print 'Warning: The offset plus peak amplitude for the AFG3021B '\
    'cannot exceed +/-5 V.'
    amplitude = 2*(5 - abs(offset))
  write("VOLTAGE:AMPLITUDE " + str(amplitude))


# This function sets the offset voltage of the function generator's output.
def set_offset(offset):
  write("VOLTAGE:AMPLITUDE?")      # read present amplitude
  write("++read 10")
  amplitude = float(ser.readline())
  if (abs(amplitude/2) + abs(offset) > 5):
    print 'Warning: The offset plus peak amplitude for the AFG3021B '\
    'cannot exceed +/-5 V.'
    if (offset > 0):
      offset = 5 - amplitude/2
    else:
      offset = amplitude/2 - 5
  write("VOLTAGE:OFFSET " + str(offset))


## This function sets the frequency of the function generator's output.
def set_frequency(frequency):
  if (frequency < 1e-6):
    print 'Warning: The minimum sinusoidal frequency for the AFG3021B '\
    'is 1 uHz.'
    frequency = 1e-6
  if (frequency > 25e6):
    print 'Warning: The maximum sinusoidal frequency for the AFG3021B '\
    'is 25 MHz.'
    frequency = 25e6
  write("FREQUENCY " + str(frequency))


# This function enables the function generator's output.
def enable_output():
  write("OUTP ON")


# This function disables the function generator's output.
def disable_output():
  write("OUTP OFF")


# This function writes command codes to the instrument. 
def write(command_code):
  ser.write(command_code + "\r\n")    # write command code


# This function closes the virtual serial port created by the Prologix
# USB/GPIB interface.
def close_serial_port():
  try:
    ser.close()
  except:
    pass


