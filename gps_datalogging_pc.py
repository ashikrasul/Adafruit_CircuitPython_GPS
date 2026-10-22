# GPS datalogging on a PC over a USB serial port.
# Based on examples/gps_datalogging.py, with these changes:
#   - Uses pyserial (/dev/ttyUSB0) instead of board/busio, and drops the
#     SD card code, which is only for microcontrollers.
#   - Switches the GPS to 115200 baud and 10 Hz, same as simple_test.py.
# Each raw NMEA sentence is appended to LOG_FILE.
import time

import serial

import adafruit_gps

# Path to the file to log GPS data.  By default this will be appended to
# which means new lines are added at the end and all old data is kept.
LOG_FILE = "gps.txt"

# Mode 'ab' means append, adding new lines to the end of the file.
# Use 'wb' instead to erase the file and start clean each time.
LOG_MODE = "ab"

# On a PC the GPS shows up as a USB serial port.
# Check `ls /dev/ttyUSB* /dev/ttyACM*` after plugging it in.
# The GPS starts at its default 9600 baud.
uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart)

# Switch the GPS to 115200 baud, then switch the PC side to match.
# 9600 baud is too slow for 10 Hz (needs ~15,000 bits/s).
# If the GPS is already at 115200 (e.g. kept by a backup battery), it ignores
# this command, and the switch below still leaves both sides matching.
gps.send_command(b"PMTK251,115200")
time.sleep(1)
uart.baudrate = 115200
uart.reset_input_buffer()  # Drop bytes garbled during the switch.

# Only RMC + GGA sentences.
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

# New fix every 100 ms (10 Hz).
gps.send_command(b"PMTK220,100")

# Main loop just reads data from the GPS module and writes it back out to
# the output file while also printing it.
with open(LOG_FILE, LOG_MODE) as outfile:
    while True:
        sentence = gps.readline()
        if not sentence:
            continue
        print(str(sentence, "ascii", errors="replace").strip())
        outfile.write(sentence)
        outfile.flush()
