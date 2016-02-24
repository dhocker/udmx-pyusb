#
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
# In particular, this program reads the same format configuration file: ~/.uDMXrc
# It responds to the same commands.
#

#
# Command syntax
#
# python uDMX.py [--help | -h] 
#	Produces help information
#
# python uDMX.py channel value [value ... value] 
#	Sends DMX message
#	channel is a number (1-512) or a channe name (defined in ~/.uDMXrc)
#	value is a number (0-255) or a value name (defined in ~/.uDMXrc)
#

try:
	import usb # this is pyusb
except:
	# If pyusb is not available we assume we might be running sudo on a raspberry pi.
	# In order to directly access a USB port on a raspberry pi, you must be running sudo.
	# This appears to be the recommended way to activate the venv
	# when running under sudo. However, it hard wires the venv to this script.
	# At a minimum we need a runtime test so the work around is only executed
	# when running on an RPi.
	import platform
	# Here we make a gross assumption that an arm cpu is an RPi.
	if platform.machine().startswith("arm"):
		activate_this = "/home/pi/Virtualenvs/pyusb/bin/activate_this.py"
		execfile(activate_this, dict(__file__=activate_this))

		import usb # This is pyusb
		print "usb imported from virtualenv."
	else:
		print "Unable to import usb (the PyUSB module)."
		print "Install PyUSB and try again."
		exit(0)

import os

# channel/value dictionary
channels_key = "channels"
values_key = "values"
cv_dict = {}
cv_dict[channels_key]= {}
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

	return dev

def send_dmx_message(message_tokens):
	dev = find_udmx_device()
	if dev is None:
		return

	trans_tokens = translate_message_tokens(message_tokens)

	if len(trans_tokens) == 2:
		# Single value message
		print "Single value message channel:", trans_tokens[0], "value:", trans_tokens[1]
	else:
		# Multi-value message
		print "Multi-value message channel:", trans_tokens[0], "values:", trans_tokens[1:]

	return

#
# Main program
#
import sys
if __name__ == "__main__":
	print "uDMX.py - uDMX utility program"

	# Filter out requests for help
	if len(sys.argv) == 1 or (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
		print "Help - TBD"
		exit(0)

	# Load the .uDMXrc file
	load_rc_file()
	# dump_dict()

	# Send the message through the uDMX interface
	send_dmx_message(sys.argv[1:])	
