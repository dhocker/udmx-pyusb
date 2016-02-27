# pyuDMX.py - Anyma (and clones) uDMX interface module
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

import usb

class uDMXDevice:
    def __init__(self):
        self._dev = None

    def open(self, vendor_id=0x16c0, product_id=0x5dc):
        # Find the uDMX interface
        self._dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        return self._dev is not None

    def close(self):
        # This may not be absolutely necessary, but it is safe.
        # It's the closest thing to a close() method.
        if self._dev is not None:
            usb.util.dispose_resources(self._dev)

    def _send_control_message(self, cmd, value_or_length=1, channel=1, data_or_length=1):
        """
        Execute a control transfer.
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

        n = self._dev.ctrl_transfer(bmRequestType, cmd, wValue=value_or_length, wIndex=channel - 1,
            data_or_wLength=data_or_length)

        # For a single value transfer the return value is the data_or_length value.
        # For a multi-value transfer the return value is the number of values transfer
        # which should be the number of values in the data_or_length bytearray.
        return n

    def send_single_value(self, channel, value):
        """
        usb request for SetSingleChannel:
            Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
            Request:        1
            Value:          value to set [0 .. 255]
            Index:          channel index to set [0 .. 511], not the human known value of 1-512
            Length:         ignored, but returned as the number of byte values transfered
        """
        SetSingleChannel = 1
        n = self._send_control_message(SetSingleChannel, value_or_length=value, channel=channel, data_or_length=1)
        return n

    def send_multi_value(self, channel, values):
        """
        usb request for SetMultiChannel:
            Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
            Request:        2
            Value:          number of channels to set [1 .. 512-wIndex]
            Index:          index of first channel to set [0 .. 511]
            Data:           iterable object containing values (we use a bytearray)
        """
        SetMultiChannel = 2
        n = self._send_control_message(SetMultiChannel, value_or_length=len(values),
            channel=channel, data_or_length=values)
        return n
