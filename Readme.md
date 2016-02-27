# Programming the Anyma uDMX interface (and clones) Using Python and PyUSB
Copyright © 2016 by Dave Hocker (AtHomeX10@gmail.com)

## Overview

The purpose of this repo is to share what I have learned about programming the
Anyma uDMX interface using Python and PyUSB on the Raspberry Pi (RPi). Th Anyma uDMX
interface is relatively inexpensive and there are a large number of clones available 
from sites like eBay. However, there seems to be a dearth of information available for
programming this interface under Linux (Raspbian Jessie in this case).

Many thanks go out to Markus Baertschi and the work he did on the uDMX-linux utility
(see https://github.com/markusb/uDMX-linux). His C++ based uDMX utility served as the basis
for the majority of my learning exercise. 

## License

The work presented here is licensed under the GNU General Public License v3 as published by the 
Free Software Foundation, Inc.. See the LICENSE file for the full text of the license.

## Source Code

The full source is maintained on [GitHub](https://www.github.com/dhocker/uDMX-pyusb).

## Build Environment

This work is written in Python 2.7.
A suitable development environment would use virtualenv and virtualenvwrapper to create a working virtual environment.
The requirements.txt file can be used with pip to create the required virtual environment with all dependencies.

## Programs and Modules

### tryusb.py Program
This was my first learning tool. It does the following:

* Locates the uDMX interface.
* Prints some information about the interface.
* Sends some basic commands to a Venue ThinPar64 demonstrating how to manipulate the light via DMX.

It also helped me resolve some issues with permissions on the RPi. To run this app:

    python tryusb.py

### uDMX.py Program
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

uDMX.py uses the pyuDMX.py module.

### pyuDMX.py Module
The pyuDMX.py module provides a simple, easy to use module for takling to the uDMX interface. Essentially,
it is a uDMX specific adapter on top of the pyusb module. If you want to write a uDMX oriented application
consider starting with pyuDMX.py.

## Learning Notes
Here are some notes from this learning exercise.

### Finding the uDMX Interface
As there is no kernel driver for the uDMX, it does not show up under /dev like /dev/tty.

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
If you want to program the uDMX on a raspberry pi without always running sudo, you
must do something with the default permissions of the uDMX device. Here are the default permissions.

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
udev rule that sets the permissions to 666 when the device is plugged in. Here's the
rule.

    SUBSYSTEM=="usb", ATTR{idVendor}=="16c0", ATTR{idProduct}=="05dc", MODE="0666"

You can take this solution by editing the [98-uDMX-usb.rules](https://github.com/dhocker/uDMX-pyusb/blob/master/98-uDMX.rules) 
file and uncommenting
the line that contains this rule. Copy the edited file to /etc/udev/rules.d.

    sudo cp 98-uDMX-usb.rules /etc/udev/rules.d

To make sure the rule is used, pull the uDMX and replug it.

There is an obvious down side to this solution. It gives all users read/write access to the uDMX. We
can limit read/write access to members of the pi group by changing the rule to:

    SUBSYSTEM=="usb", ATTR{idVendor}=="16c0", ATTR{idProduct}=="05dc", GROUP="pi"

This rule leaves the permissions set to 664 while changing the ownership to root:pi.
Overall, this is probably more desirable. The root user owns the device, members of the 
pi group (which includes pi) have read/write access and all other users have read-only access.

    ~/rpi/uDMX-pyusb $ ll /dev/bus/usb/001/005
    crw-rw-r-- 1 root pi 189, 4 Feb 26 10:05 /dev/bus/usb/001/005

You can choose this rule by editing 98-uDMX-usb.rules file and uncommenting
the line that contains this rule.

For more on udev rules see [Writing udev rules](http://www.reactivated.net/writing_udev_rules.html).

## Reboot Issues
This is an observation. On a warm reboot, the uDMX interface is not always found. 
You might have to replug the device to get Raspbian to find it. Why this happens is unclear.

## Multiple uDMX Issues
It is possible to run multiple uDMX devices on one system, but it can be difficult. Most uDMX interfaces
and clones do not have unique serial numbers. This makes identification of each interface problematic.

Given the detailed USB information shown below, the following is available to identify
a uDMX.

* Vendor ID
* Product ID
* Manufacturer
* Product
* Serial
* Bus number
* Device number

Based on limited research it appears that only the Bus and Device numbers uniquely identify a
given uDMX interace. The other values are likely to be the same for all uDMX interfaces based on the 
Anyma design and firmware. Unfortunately, the Bus and Device number cannot be used reliably because simply moving 
a uDMX to another USB port will change one or both of those values.

If you want to use multiple uDMX interfaces, you need to plug them in one at a time and use the lsusb command
to determine the Bus and Device number for each one. And, after that you can't move them around.

Unless otherwise indicated, the programs in this repo will work with the first uDMX interface they find.

## Detailed USB Information
Here is a dump of innformation a uDMX clone. Most of the information in the dump seems to refer to
the firmware manufacturer not the hardware manufacturer. The firmware is open source.

    ~/rpi/uDMX-pyusb $ lsusb -v
    
    Bus 001 Device 005: ID 16c0:05dc Van Ooijen Technische Informatica shared ID for use with libusb
    Device Descriptor:
      bLength                18
      bDescriptorType         1
      bcdUSB               1.01
      bDeviceClass          255 Vendor Specific Class
      bDeviceSubClass         0 
      bDeviceProtocol         0 
      bMaxPacketSize0         8
      idVendor           0x16c0 Van Ooijen Technische Informatica
      idProduct          0x05dc shared ID for use with libusb
      bcdDevice            1.02
      iManufacturer           1 www.anyma.ch
      iProduct                2 uDMX
      iSerial                 3 ilLUTZminator001
      bNumConfigurations      1
      Configuration Descriptor:
        bLength                 9
        bDescriptorType         2
        wTotalLength           18
        bNumInterfaces          1
        bConfigurationValue     1
        iConfiguration          0 
        bmAttributes         0x80
          (Bus Powered)
        MaxPower              500mA
        Interface Descriptor:
          bLength                 9
          bDescriptorType         4
          bInterfaceNumber        0
          bAlternateSetting       0
          bNumEndpoints           0
          bInterfaceClass         0 (Defined at Interface level)
          bInterfaceSubClass      0 
          bInterfaceProtocol      0 
          iInterface              0 
    Device Status:     0x0000
      (Bus Powered)

## References
1. [uDMX - tiny bus powered USB-DMX interface - Anyma](http://www.anyma.ch/research/udmx/)
2. [illutzminator](http://www.illutzminator.de/udmx.html?&L=1)
3. [Markus Baertschi uDMX Utility](https://github.com/markusb/uDMX-linux)
4. [Writing udev rules](http://www.reactivated.net/writing_udev_rules.html)