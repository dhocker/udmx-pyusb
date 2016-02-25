# uDMX.py - Anyma (and clones) uDMX interface utility
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
# This utility is based on the C++ uDMX utility written by Markus Baertschi.
# See https://github.com/markusb/uDMX-linux.git for more on this good work.
# In particular, this program reads the same format rc file: ~/.uDMXrc
# It responds to the same commands and inputs.
#
# This program is limited to controlling one uDMX, namely the first one
# it finds with the correct vendor ID and product ID.
#

import json

# The active configuration
loaded_conf = None
config = {}

def load_conf(cfg_path):
    """
    Try to load the given conf file.
    """
    global config
    try:
        cfg = open(cfg_path, 'r')
    except Exception as ex:
        #print "Unable to open {0}".format(cfg_path)
        #print str(ex)
        return False
      
    # Read the entire contents of the conf file
    cfg_json = cfg.read()
    cfg.close()
    #print cfg_json
    
    # Try to parse the conf file into a Python structure
    try:
        config = json.loads(cfg_json)
    except Exception as ex:
        print "Unable to parse configuration file as JSON"
        print str(ex)
        return False

    # This config was sucessfully loaded
    return True

# Try to load the conf file from one of these well known places.
# If there isn't one, we give up.
for cfg_path in ["/etc/uDMX.conf", "/home/pi/uDMX.conf", "/home/pi/rpi/uDMX-pyusb/uDMX.conf"]:
    if load_conf(cfg_path):
        loaded_conf = cfg_path
        break

if loaded_conf is None:
    print "Unable to find a uDMX.conf file"
    exit(0)

# print "Configuration:", config
    
# Find the pyusb module and import it
try:
    import usb  # this is pyusb
except:
    # Assumption: You are running with a virtualenv.
    # If pyusb is not available we assume we might be running sudo on a raspberry pi.
    # In order to directly access a USB port on a raspberry pi, you must be running sudo.
    # An alternative is the chmod the permissions on the USB device. For example, if the
    # device is /dev/bus/usb/001/005, then run the command
    #   sudo chmod +w /dev/bus/usb/001/005
    # Unfortunately, this change will be lost across a reboot. A more permanent solution
    # involves digging into udev which is way outside the scope of this project.

    # This appears to be the recommended way to activate the venv specified in the conf file.
    import platform

    # If a virtualenv is defined in the config file, use it.
    if "venv" in config:
        activate_this = config["venv"] + "/bin/activate_this.py"
        # On the raspberry pi 2 this is pretty expensive
        execfile(activate_this, dict(__file__=activate_this))

        import usb  # This is pyusb

        # print "usb imported from virtualenv."
    else:
        print "Unable to import usb (the PyUSB module)."
        print "Install PyUSB or specify a virtualenv with PyUSB via the /etc/uDMX.conf file."
        exit(0)

import os

# channel/value dictionary
channels_key = "channels"
values_key = "values"
cv_dict = {}
cv_dict[channels_key] = {}
cv_dict[values_key] = {}


def add_channel(name, value):
    """
    Adds to the channel/value dictionary an alias channel name with channel number.
    """
    cv_dict[channels_key][name] = int(value)


def add_values(name, values):
    """
    Adds an alias with list of values to the channel/value dictionary.
    """
    int_values = map(int, values)
    cv_dict[values_key][name] = int_values


def is_valid_channel(channel):
    """
    Determines if a channel number is a valid DMX channel (1-512).
    """
    try:
        c = int(channel)
        return (c >= 1) and (c <= 512)
    except:
        return False


def are_valid_values(values):
    """
    Determines if a list of values are valid DMX values (0-255).
    """
    try:
        int_values = map(int, values)
        for v in int_values:
            if (v >= 0) and (v <= 255):
                continue
            else:
                return False
    except Exception as ex:
        # print ex
        return False
    return True


def load_rc_file():
    """
    Load the contents of the configuration file ~/.uDMXrc
    """
    # If an rc file is named in the config, use it.
    # Otherwise, fall back to looking in the HOME directory.
    # The fall back  won't work under RPi because HOME will be root.
    if "uDMXrc" in config:
        rcfile = config["uDMXrc"]
    else:
        rcfile = os.environ["HOME"] + "/.uDMXrc"
    cf = open(rcfile, 'r')
    if cf:
        for line in cf:
            tokens = line.split()

            # Blank line
            if len(tokens) == 0:
                continue

            # A comment
            if tokens[0] == '#':
                continue
            # A channel alias
            elif tokens[0] == 'channel':
                # channel alias value
                if len(tokens) >= 3:
                    if is_valid_channel(tokens[2]):
                        add_channel(tokens[1], tokens[2])
                    else:
                        print line
                        print "Invalid channel value"
                else:
                    print line
                    print "Invalid channel statement"
            # A DMX value or values
            elif tokens[0] in ['value', 'values']:
                # value alias value
                if len(tokens) >= 3:
                    if are_valid_values(tokens[2:]):
                        add_values(tokens[1], tokens[2:])
                    else:
                        print line
                        print "Invalid value(s)"
                else:
                    print line
                    print "Invalid value statement"
            # Something we don't recognize
            else:
                print line
                print tokens[0], "is not a recognized configuration file statement"
        cf.close()
    else:
        print "Configuration file ~/.uDMXrc was not found"


def translate_message_tokens(message_tokens):
    """
    Translates alias references to their defined values.
    The first token is a channel alias.
    The remaining tokens are value aliases.
    """
    trans_tokens = []
    if message_tokens[0] in cv_dict[channels_key]:
        trans_tokens.append(cv_dict[channels_key][message_tokens[0]])
    else:
        trans_tokens.append(int(message_tokens[0]))

    for token in message_tokens[1:]:
        if token in cv_dict[values_key]:
            trans_tokens.extend(cv_dict[values_key][token])
        else:
            trans_tokens.append(int(token))

    return trans_tokens


def dump_dict():
    """
    Diagnostic dump of channel/value dictionary.
    """
    print cv_dict


def find_udmx_device():
    """
    Find the uDMX USB device using its vendor and product ID
    """
    # This is the vendor ID and product ID for the Anyma uDMX clone interface.
    vid = 0x16c0
    pid = 0x05dc

    # Find the uDMX interface
    dev = usb.core.find(idVendor=vid, idProduct=pid)

    if dev is None:
        print "uDMX device was not found"

    # print dev.bus, dev.address

    return dev

def send_control_message(dev, cmd, value_or_length=1, channel=1, data_or_length=1):
    """
    Execute a control transfer.
    dev - Device object that defines the target device (uDMX interface).
    cmd - 1 for single value transfer, 2 for multi-value transfer
    value_or_length - for single value transfer, the value. For multi-value transfer,
        the length of the data bytearray.
    channel - the base DMX channel number, 1-512. Note that this will be adjusted
        to 0-511 when sent to the uDMX.
    data_or_length - for a single value transfer it should be 1.
        For a multi-value transfer, a bytearray containing the values. 
    """

    # All data tranfers use this request type. This is more for
    # the PyUSB package than for the uDMX as the uDMX does not 
    # use it..
    bmRequestType = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE | usb.util.CTRL_OUT 

    n = dev.ctrl_transfer(bmRequestType, cmd, wValue=value_or_length, wIndex=channel - 1,
        data_or_wLength=data_or_length)
    
    # For a single value transfer the return value is the data_or_length value.
    # For a multi-value transfer the return value is the number of values transfer
    # which should be the number of values in the data_or_length bytearray.
    return n

"""
    NOTE: 
    This code implements two functions for transmitting DMX messages. One function 
    transmits a single channel/value pair while the second transmits a 
    multi-channel/values set. In reality only the second function is needed as it
    is a superset of the the first function. The single channel/value function
    is included here for completeness. The function is used, but is not strictly
    necessary.
"""

def send_single_value(dev, channel, value):
    """
    usb request for SetSingleChannel:
        Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
        Request:        1
        Value:          value to set [0 .. 255]
        Index:          channel index to set [0 .. 511], not the human known value of 1-512
        Length:         ignored, but returned as the number of byte values transfered
    """
    SetSingleChannel = 1
    n = send_control_message(dev, SetSingleChannel, value_or_length=value, channel=channel, data_or_length=1)
    return n

def send_multi_value(dev, channel, values):
    """
    usb request for SetMultiChannel:
        Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
        Request:        2
        Value:          number of channels to set [1 .. 512-wIndex]
        Index:          index of first channel to set [0 .. 511]
        Data:           iterable object containing values (we use a bytearray)
    """
    SetMultiChannel = 2
    n = send_control_message(dev, SetMultiChannel, value_or_length=len(values), 
        channel=channel, data_or_length=values)
    return n

def send_dmx_message(message_tokens):
    """
    Send the DMX message defined by the command line arguments (message tokens).
    The first argument/token is the DMX channel.
    The remaining argument(s).token(s) are DMX values.
    """

    # Find the uDMX USB device
    dev = find_udmx_device()
    if dev is None:
        return

    # Translate the tokens into integers.
    # trans_tokens[0] will be the zero-based channel number (0-511) as an integer.
    # The remaining tokens will be zero-based values (0-255) as integers.
    trans_tokens = translate_message_tokens(message_tokens)

    if len(trans_tokens) == 2:
        # Single value message
        print "Sending single value message channel:", trans_tokens[0], "value:", trans_tokens[1]
        n = send_single_value(dev, trans_tokens[0], trans_tokens[1])
        print "Sent", n, "value"
    else:
        # Multi-value message
        print "Sending multi-value message channel:", trans_tokens[0], "values:", trans_tokens[1:]
        bytes = bytearray(trans_tokens[1:])
        n = send_multi_value(dev, trans_tokens[0], bytes)
        print "Sent", n, "values"

    # This may not be absolutely necessary, but it is safe.
    # It's the closest thing to a close() method.
    usb.util.dispose_resources(dev)

def help():
    print ""
    print "Usage:"
    print ""
    #print "python uDMX.py [--help | -h]"
    #print "or"
    print "uDMX [--help | -h]"
    print "    Produces help information"
    print ""
    #print "python uDMX.py channel value [value ... value]"
    #print "or"
    print "uDMX channel value [value ... value]"
    print "    Sends DMX message"
    print "    channel is a number (1-512) or a channel name (defined in ~/.uDMXrc)"
    print "    value is a number (0-255) or a value name (defined in ~/.uDMXrc)"
    print ""

#
# Main program
#
import sys

if __name__ == "__main__":
    print "uDMX.py - uDMX utility program - version 0.9"

    # Filter out requests for help and insufficient command line arguments
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h")):
        help()
        exit(0)

    # Load the .uDMXrc file
    load_rc_file()
    # dump_dict()

    # Send the message through the uDMX interface
    send_dmx_message(sys.argv[1:])
