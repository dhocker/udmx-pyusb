#
# Copyright (C) 2016  Dave Hocker (email: AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE file).  If not, see <http://www.gnu.org/licenses/>.
#

"""
This code was written expressly to learn about the Anyma uDMX interface and
how to work with it using Python and pyusb on a raspberry pi (RPi).
Much of the learning started with the C++ based uDMX utility written
by Markus Baertschi (https://github.com/markusb/uDMX-linux). Many thanks
to Markus for this work.

After gaining enough knowledge on how to use pyusb, my next step will be
to write a Python version of the uDMX utility (which I will push to my github
accuont). Hopefully, the combination of tryusb.py and uDMX.py will provide 
a good base for others wanting to work with an inexpensive DMX interface on an RPi.

Side Note: You can find a number of clone uDMX interfaces on eBay. The one
used for this exercise was purchased from tomtop_auction
http://www.ebay.com/usr/tomtop_auction?_trksid=p2047675.l2559
This is not an endoresement or recommendation. It is just information in
case you are looking for a uDMX type of interface.
"""

# Requires a venv with pyusb installed. See requirements.txt.

# If you apply the udev rule, the uDMX will be accessible as the pi user.
# If youdo not apply the udev rule, you must be running sudo.
# This appears to be the recommended way to activate the venv
# when running under sudo. However, it hard wires the venv to this script.
# At a minimum we need a runtime test so the work around is only executed
# when running on an RPi.
# the rest of this research code assumes the udev rule has been applied.
# import platform
# Here we make a gross assumption that an arm cpu is an RPi.
# if platform.machine().startswith("arm"):
#	activate_this = "/home/pi/Virtualenvs/pyusb/bin/activate_this.py"
#	execfile(activate_this, dict(__file__=activate_this))

import usb  # This is pyusb
import time

# DEVICE ID 16c0:05dc
# USB id's for uDMX (aka Anyma uDMX)
# The attached DMX device was a Venue ThinPar64.

# This is the vendor ID and product ID for the Anyma uDMX clone interface.
vid = 0x16c0
pid = 0x05dc

# Find the uDMX interface by vendor and product ID
dev = usb.core.find(idVendor=vid, idProduct=pid)
# This would find the uDMX by bus number and address (aka port)
# dev = usb.core.find(bus=1, address=4)
#
# You could find the uDMX by using the SYMLINK that the udev rule sets up.
# links = glob.glob("/dev/uDMXusb*")
# os.path.realpath(links[0]) # returns something like /dev/bus/usb/001/004
# You can use a regex to pull out the bus (001) and address (004).

if dev is None:
    print("uDMX device was not found")
    exit(0)

#
# It looks like the only way to determine what methods and
# properties are available on a given pyusb object requires looking
# at the source code on github: https://github.com/walac/pyusb/tree/master/usb
#

print("**********uDMX Device")
print("type:", type(dev))
print(dev)

print("**********MANUFACTURER")
print(dev.manufacturer)
if dev.manufacturer != "www.anyma.ch":
    print("Error - expected www.anyma.ch, actual " + dev.manufacturer)

print("**********PRODUCT")
print(dev.product)

dev.set_configuration()
cfg = dev.get_active_configuration()
print("**********CONFIGURATION")
print("type:", type(cfg))
print(cfg)

intf = cfg[0, 0]
print("**********INTERFACE")
print("type:", type(intf))
print(intf)

ep = usb.util.find_descriptor(intf,
                              # match the first OUT endpoint
                              custom_match= \
                                  lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_OUT)
print("**********ENDPOINT")
if ep:
    print(ep)
else:
    print("This device.configuration.interface does not have an OUT endpoint")

status = usb.control.get_status(dev)
print("**********STATUS")
print("Status:", status)

cmd_SetSingleChannel = 1
"""
usb request for cmd_SetSingleChannel:
	bmRequestType:	ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
	bRequest:		cmd_SetSingleChannel
	wValue:			value of channel to set [0 .. 255]
	wIndex:			channel index to set [0 .. 511]
	wLength:		ignored
"""
cmd_SetChannelRange = 2
"""
usb request for cmd_SetChannelRange:
	bmRequestType:	ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
	bRequest:		cmd_SetChannelRange
	wValue:			number of channels to set [1 .. 512-wIndex]
	wIndex:			index of first channel to set [0 .. 511]
	wLength:		length of data, must be >= wValue
"""

# From pyusb (usb.core)
# class Device
#    def ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0,
#            data_or_wLength = None, timeout = None):
"""
		Do a control transfer on the endpoint 0.
        This method is used to issue a control transfer over the endpoint 0
        (endpoint 0 is required to always be a control endpoint).
        The parameters bmRequestType, bRequest, wValue and wIndex are the same
        of the USB Standard Control Request format.
        Control requests may or may not have a data payload to write/read.
        In cases which it has, the direction bit of the bmRequestType
        field is used to infer the desired request direction. For
        host to device requests (OUT), data_or_wLength parameter is
        the data payload to send, and it must be a sequence type convertible
        to an array object. In this case, the return value is the number
        of bytes written in the data payload. For device to host requests
        (IN), data_or_wLength is either the wLength parameter of the control
        request specifying the number of bytes to read in data payload, and
        the return value is an array object with data read, or an array
        object which the data will be read to, and the return value is the
        number of bytes read.
"""

# All data tranfers use this request type. This is more for
# the PyUSB package than for the uDMX.
bmRequestType = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE | usb.util.CTRL_OUT

# Single channel value transfer
# Interface for setting a single channel data value
# wValue - the value, 0-255, to be set.
# wIndex - channel number, 0-511, being set. In DMX terms this corresponds to channel 1-512.
# data_or_wLength - not used for this case. However, on success this will be the return value.

# Set RGB mode (Venue ThinPar64 is in 7-channel mode)
channel = 6  # mode channel
channel_value = 255  # on all the way
n = dev.ctrl_transfer(bmRequestType, cmd_SetSingleChannel, wValue=channel_value, wIndex=channel, data_or_wLength=1)
print("Sent:", n)

# Bring dimmer to 100%
channel = 7  # dimmer channel
channel_value = 255  # on all the way
n = dev.ctrl_transfer(bmRequestType, cmd_SetSingleChannel, wValue=channel_value, wIndex=channel, data_or_wLength=1)
print("Sent:", n)

# Turn light on
channel = 2  # blue channel
channel_value = 255  # on all the way
n = dev.ctrl_transfer(bmRequestType, cmd_SetSingleChannel, wValue=channel_value, wIndex=channel, data_or_wLength=1)
print("Sent:", n)

print("Sleeping...")
time.sleep(3.000)

# Turn light off
channel_value = 0
n = dev.ctrl_transfer(bmRequestType, cmd_SetSingleChannel, wValue=channel_value, wIndex=channel, data_or_wLength=1)
print("Sent:", n)

print("Sleeping...")
time.sleep(2.000)

# Interface for setting multiple channels at one time
# wValue - number of channels/bytes to be set. e.g. len(bytearray)
# wIndex - starting channel number, 0-511.
# data_or_wLength - sequence type of data, e.g. a bytearray

channel_values = bytearray([255, 255, 255])  # RGB all on
channel = 0  # Red channel
# Turn on red, green and blue lights
n = dev.ctrl_transfer(bmRequestType, cmd_SetChannelRange, wValue=len(channel_values), \
                      wIndex=channel, data_or_wLength=channel_values)
print("Sent:", n)

print("Sleeping...")
time.sleep(3.000)

channel_values = bytearray([0, 0, 0])  # all off
# Turn off red, green and blue
n = dev.ctrl_transfer(bmRequestType, cmd_SetChannelRange, wValue=len(channel_values), \
                      wIndex=channel, data_or_wLength=channel_values)
print("Sent:", n)
