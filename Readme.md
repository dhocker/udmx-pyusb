# Programming the Anyma uDMX interface (and clones) Using Python
Copyright © 2016 by Dave Hocker (AtHomeX10@gmail.com)

## Overview

The purpose of this repo is to share what I have learned about programming the
Anyma uDMX interface using Python and PyUSB on the Raspberry Pi (RPi). Th Anyma uDMX
interface is relatively inexpensive and there are a large number of clones available 
from sites like eBay. However, there seems to be a dearth of information available for
programming this interface under Linux (Raspbian Jessie in this case).

Many thanks go out to Markus Baertschi and the work he did on the uDMX-linux utility
(see https://github.com/markusb/uDMX-linux). His C++ based uDMX utility served as the basis
for the majority of my learnng exercise. 
My next project will be a Python version of his C++ uDMX utility.

## License

The work presented here is licensed under the GNU General Public License v3 as published by the 
Free Software Foundation, Inc.. See the LICENSE file for the full text of the license.

## Source Code

The full source is maintained on [GitHub](https://www.github.com/dhocker/uDMX-pyusb).

## Build Environment

This work is written in Python 2.7.
A suitable development environment would use virtualenv and virtualenvwrapper to create a working virtual environment.
The requirements.txt file can be used with pip to create the required virtual environment with all dependencies.

## Programs

### tryusb.py
This was my first learning tool. It does the following:

  * Locates the uDMX interface.
  * Prints some information about the interface.
  * Sends some basic commands to a Venue ThinPar64 demonstrating how to manipulate the light via DMX.

It also helped me resolve some issues with permissions on the RPi. To run this app:

sudo python tryusb.py

### uDMX.py
This program functions pretty much like the C++ based uDMX utility from Markus Baertschi. To get help, try

    ./uDMX --help
    or
    python uDMX.py --help

For each invocation, this program does the following:

    * Loads the uDMX.conf file from /etc/uDMX.conf.
    * Activates the virtualenv defined in the conf file IF PyUSB is not found in the current environment.
    * Loads the .uDMXrc file defined in the conf file.
    * Locates the uDMX interface.
    * Sends the DMX message defined by the command line arguments.

## Notes
Here are some notes from this learning exercise.

### Finding the uDMX Interface
As there is no kernel driver for the uDMX, it does not show up under /dev.

You can locate it this way:

~/rpi/uDMX-pyusb $ lsusb
Bus 001 Device 005: ID 16c0:05dc Van Ooijen Technische Informatica shared ID for use with libusb
Bus 001 Device 004: ID 1a40:0201 Terminus Technology Inc. FE 2.1 7-port Hub
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. 
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

The uDMX is the first device at Bus 001, Device 005 with ID 16c0:05dc. The 16c0 is the vendor ID and
the 05dc is the product ID. The uDMX can be found at /dev/bus/usb/001/005.

## Permissions

~/rpi/uDMX-pyusb $ ls -al /dev/bus/usb/001/005
crw-rw-r-- 1 root root 189, 4 Feb 25 15:30 /dev/bus/usb/001/005

Notice the permissions for the device: 664. Only root and members of the 
root group have write permission. This is why sudo is required for the current user (usually pi).
You can fix this issue by changing the permissions on the uDMX to: 666.

sudo chmod 666 /dev/bus/usb/001/005

Now check the permissions.

~/rpi/uDMX-pyusb $ ls -al /dev/bus/usb/001/005
crw-rw-rw- 1 root root 189, 4 Feb 25 15:30 /dev/bus/usb/001/005

Unfortunately, this is only a temporary fix. On the next reboot the permissions will revert
back to their default 664. One way to permanently fix this problem is to write a 
udev rule that sets the permissions to 666 when then device is plugged in.

You can take this route by copying the 98-uDMX-usb.rules file to /etc/udev/rules.d.

sudo cp 98-uDMX-usb.rules /etc/udev/rules.d

To make sure the rule is used, pull the uDMX and replug it.

## Reboot Issues
This is an empiracle observation. On a warm reboot, the uDMX interface is not found. You have to replug
the device to get Raspbian to find it. Why this happens is unclear.
