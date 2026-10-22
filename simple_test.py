
import time
import serial

import adafruit_gps

# On a PC the GPS shows up as a USB serial port, not board.RX/TX pins.
# Check `ls /dev/ttyUSB* /dev/ttyACM*` after plugging it in.
uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart, debug=False)

# Switch the GPS to 115200 baud, then switch the PC side to match.
# 9600 baud is too slow for 10 Hz (needs ~15,000 bits/s).
# If the GPS is already at 115200 (e.g. kept by a backup battery), it ignores
# this command, and the switch below still leaves both sides matching.
gps.send_command(b'PMTK251,115200')
time.sleep(1)
uart.baudrate = 115200
uart.reset_input_buffer()  # Drop bytes garbled during the switch.

# Only RMC + GGA sentences.
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# New fix every 100 ms (10 Hz).
gps.send_command(b'PMTK220,100')

PRINT_INTERVAL = 0.1  # Seconds; matches the 10 Hz update rate.

last_print = time.monotonic()
while True:

    gps.update()

    current = time.monotonic()
    if current - last_print >= PRINT_INTERVAL:
        last_print = current
        if not gps.has_fix:
            print('Waiting for fix...')
            continue
        print('=' * 40)  # Print a separator line.
        print('Latitude: {0:.6f} degrees'.format(gps.latitude))
        print('Longitude: {0:.6f} degrees'.format(gps.longitude))