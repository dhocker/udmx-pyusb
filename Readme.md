# Programming the Anyma uDMX interface (and clones) Using Python
Copyright © 2016 by Dave Hocker (AtHomeX10@gmail.com)

## Overview

The purpose of this repo is to share what I have learned about programming the
Anyma uDMX interface using Python and PyUSB on the Raspberry Pi (RPi). Th Anyma uDMX
interface is relatively inexpensive and there are a large number of clones available 
from sites like eBay. However, there seems to be a dearth of information available for
programming this interface under Linux.

Many thanks go out to Markus Baertschi and the work he did on the uDMX-linux utility
(see https://github.com/markusb/uDMX-linux). His C++ based uDMX utility served as the basis
for the majority of my learnng exercise. 
My next project will be a Python version of the uDMX utility.

## License

The work presented here is licensed under the GNU General Public License v3 as published by the 
Free Software Foundation, Inc.. See the LICENSE file for the full text of the license.

## Source Code

The full source is maintained on [GitHub](https://www.github.com/dhocker/repo-tbd).

## Build Environment

This work is written in Python 2.7.
A suitable development environment would use virtualenv and virtualenvwrapper to create a working virtual environment.
The requirements.txt file can be used with pip to create the required virtual environment with all dependencies.

## Programs

### tryusb.py
This was my first learning tool. It does the following:

  * Locates the uDMX interface
  * Prints some information about the interface
  * Sends some basic commands to a Venue ThinPar64 demonstrating how to manipulate the light via DMX.

It also helped me resolve some issues with permissions on the RPi. To run this app:

sudo python tryusb.py

### uDMX.py
TBW
