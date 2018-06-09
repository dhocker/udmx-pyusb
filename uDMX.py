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
import os
import sys

# The active configuration
loaded_conf = None
config = {}

# Global options
verbose = False

def load_conf(cfg_path):
    """
    Try to load the given conf file.
    """
    global config
    try:
        cfg = open(cfg_path, 'r')
    except Exception as ex:
        if verbose:
            print("Unable to open {0}".format(cfg_path))
            print(str(ex))
        return False
      
    # Read the entire contents of the conf file
    cfg_json = cfg.read()
    cfg.close()
    #print(cfg_json)
    
    # Try to parse the conf file into a Python structure
    try:
        config = json.loads(cfg_json)
    except Exception as ex:
        print("Unable to parse configuration file as JSON")
        print(str(ex))
        return False

    # This config was successfully loaded
    return True

# Try to load the conf file from one of these well known places.
# If there isn't one, we give up.
places = []
places.append(os.path.join(os.getcwd(), "uDMX.conf"))
if os.name == "nt":
    places.append(os.path.join(os.environ["USERPROFILE"], "uDMX.conf"))
else:
    places.append(os.path.join(os.environ["HOME"], "uDMX.conf"))
    places.append("/etc/uDMX.conf")

for cfg_path in places:
    if load_conf(cfg_path):
        loaded_conf = cfg_path
        break

if loaded_conf is None:
    print("Unable to find a uDMX.conf file")
    exit(0)

# print("Configuration:", config)
    
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
    # involves digging into udev. Permissions and a better solution are discussed in
    # the Readme.md file.

    # This appears to be the recommended way to activate the venv specified in the conf file.
    import platform

    # If a virtualenv is defined in the config file, use it.
    if "venv" in config:
        activate_this = os.path.join(config["venv"], "bin/activate_this.py")
        # On the raspberry pi 2 this is pretty expensive
        # On Python 2 is's execfile. One Python 3 it's exec.
        if sys.version_info[0] < 3:
            execfile(activate_this, dict(__file__=activate_this))
        else:
            exec(open(activate_this).read())

        import usb  # This is pyusb

        # print("usb imported from virtualenv.")
    else:
        print("Unable to import usb (the PyUSB module).")
        print("Install PyUSB or specify a virtualenv with PyUSB via the /etc/uDMX.conf file.")
        exit(0)

from pyudmx import pyudmx

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
        # print(ex)
        return False
    return True


def load_rc_file():
    """
    Load the contents of the resource file ~/.uDMXrc
    """
    # If an rc file is named in the config, use it.
    # Otherwise, fall back to looking in the HOME directory.
    # The fall back won't work under RPi because HOME will be root.
    if "uDMXrc" in config:
        rcfile = config["uDMXrc"]
    else:
        if os.name == "nt":
            # Windows
            rcfile = os.path.join(os.environ["USERPROFILE"], ".uDMXrc")
        else:
            # Mostly *nix type systems
            rcfile = os.path.join(os.environ["HOME"], ".uDMXrc")
    try:
        cf = open(rcfile, 'r')
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
                        print(line)
                        print("Invalid channel value")
                else:
                    print(line)
                    print("Invalid channel statement")
            # A DMX value or values
            elif tokens[0] in ['value', 'values']:
                # value alias value
                if len(tokens) >= 3:
                    if are_valid_values(tokens[2:]):
                        add_values(tokens[1], tokens[2:])
                    else:
                        print(line)
                        print("Invalid value(s)")
                else:
                    print(line)
                    print("Invalid value statement")
            # Something we don't recognize
            else:
                print(line)
                print(tokens[0], "is not a recognized resource file statement")
        cf.close()
    except:
        print("Unable to open resource file", rcfile)


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
    print(cv_dict)

def send_dmx_message(message_tokens):
    """
    Send the DMX message defined by the command line arguments (message tokens).
    The first argument/token is the DMX channel.
    The remaining argument(s).token(s) are DMX values.
    """

    # Open the uDMX USB device
    dev = pyudmx.uDMXDevice()
    if not dev.open():
        print("Unable to find and open uDMX interface")
        return False

    # Translate the tokens into integers.
    # trans_tokens[0] will be the one-based channel number (1-512) as an integer.
    # The remaining tokens will be zero-based values (0-255) as integers.
    trans_tokens = translate_message_tokens(message_tokens)

    if len(trans_tokens) == 2:
        # Single value message
        if verbose:
            print("Sending single value message channel:", trans_tokens[0], "value:", trans_tokens[1])
        n = dev.send_single_value(trans_tokens[0], trans_tokens[1])
        if verbose:
            print("Sent", n, "value")
    else:
        # Multi-value message
        if verbose:
            print("Sending multi-value message channel:", trans_tokens[0], "values:", trans_tokens[1:])
        n = dev.send_multi_value(trans_tokens[0], trans_tokens[1:])
        if verbose:
            print("Sent", n, "values")

    # This may not be absolutely necessary, but it is safe.
    # It's the closest thing to a close() method.
    dev.close()

    # Returns True if something was sent
    return n > 0
    
#
# Main program
#
import argparse

if __name__ == "__main__":
    print("uDMX.py - uDMX utility program - version 0.96")

    # Set up command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", nargs=1, 
        help="DMX channel number (1-512) or channel name")
    parser.add_argument("value", nargs="+", 
        help="One or more DMX channel values (0-255) or value names")
    parser.add_argument("-v", "--verbose", 
        help="Produce verbose output", action="store_true")
    args = parser.parse_args()

    verbose = args.verbose

    # Filter out requests for help and insufficient command line arguments
    #if len(sys.argv) < 2 or (len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h")):
    #    help()
    #    exit(0)

    # Load the .uDMXrc file
    load_rc_file()
    # dump_dict()

    # Send the message through the uDMX interface
    msg_tokens = []
    msg_tokens.extend(args.channel)
    msg_tokens.extend(args.value)
    if verbose:
        print("Message tokens:", msg_tokens)
    if send_dmx_message(msg_tokens):
        print("Message sent")
    else:
        print("Message failed")
