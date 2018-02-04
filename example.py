#
# example.py
# Copyright 2018 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# Example of how to use pyudmx with a Thinpar 64 light
# http://venuelightingeffects.com/wp-content/uploads/manuals/Venue_Thinpar_64_Manual_HR.pdf
# 7 channel mode
# Channels 1-3 are RGB
# Channel 7 is the dimmer
#
# Requirements
# A virtual environment meeting the requirements defined in requirements.txt works best.
# Specifically the pyusb module must be installed.
#

from pyudmx import pyudmx
from time import sleep


def send_rgb(dev, red, green, blue, dimmer):
    """
    Send a set of RGB values to the light
    """
    cv = [0 for v in range(0, 512)]
    cv[0] = red
    cv[1] = green
    cv[2] = blue
    cv[6] = dimmer
    sent = dev.send_multi_value(1, cv)
    return sent


def main():
    """
    How to control a DMX light through an Anyma USB controller
    """

    # Channel value list for channels 1-512
    cv = [0 for v in range(0, 512)]
    
    # Create an instance of the DMX controller and open it    
    print "Opening DMX controller..."
    dev = pyudmx.uDMXDevice()
    # This will automagically find a single Anyma-type USB DMX controller
    dev.open()
    # For informational purpose, display what we know about the DMX controller
    print dev.Device
    
    # Send messages to the light changing it to red, then green, then blue
    # This is the "hard way" to do it, but illustrates how it's done

    print "Setting to red..."
    cv[0] = 255 # red
    cv[6] = 128 # dimmer to half value
    sent = dev.send_multi_value(1, cv)
    print "Set to red"
    sleep(3.0)

    print "Setting to green..."
    cv[0] = 0 # red
    cv[1] = 255 # green
    cv[6] = 128 # dimmer to half value
    sent = dev.send_multi_value(1, cv)
    print "Set to green"
    sleep(3.0)

    print "Setting to blue..."
    cv[0] = 0 # red
    cv[1] = 0 # green
    cv[2] = 255 # blue
    cv[6] = 128 # dimmer to half value
    sent = dev.send_multi_value(1, cv)
    print "Set to blue"
    sleep(3.0)
    
    # Here's an easier way to do it

    print "And, again the easier way"
    send_rgb(dev, 255, 0, 0, 128)
    sleep(3.0)
    send_rgb(dev, 0, 255, 0, 128)
    sleep(3.0)
    send_rgb(dev, 0, 0, 255, 128)
    sleep(3.0)

    print "Reset all channels and close.."
    # Turns the light off
    cv = [0 for v in range(0, 512)]
    dev.send_multi_value(1, cv)
    dev.close()

if __name__ == "__main__":
    main()
    print "Done"
