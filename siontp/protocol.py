###############################################################################
# The MIT License (MIT)
#
# Copyright (C) 2009-2015 Charles-Francois Natali <cf.natali@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
"""Python NTP library.

Implementation of client-side NTP (RFC-1305), and useful NTP-related
functions.
"""


import struct
import time
import datetime


_LSB16 = 2 ** 16
_LSB32 = 2 ** 32
_SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[:3])
_NTP_EPOCH = datetime.date(1900, 1, 1)
DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600


class NTPException(Exception):
    pass


# TODO: move to dataclasses when python 3.6 will be dropped
class Packet:

    _FORMAT = struct.Struct("!B B B b 3I 4Q")

    def __init__(self, *, leap=0, version=2, mode=3, stratum=0,
                 poll_interval=0, precision=0, root_delay=0, root_dispersion=0,
                 reference_clock_id=0, reference_timestamp=0,
                 originate_timestamp=0, receive_timestamp=0,
                 transmit_timestamp=0, destination_timestamp=0):
        self.leap = leap
        self.version = version
        self.mode = mode
        self.stratum = stratum
        self.poll_interval = poll_interval
        self.precision = precision
        self.root_delay = root_delay
        self.root_dispersion = root_dispersion
        self.reference_clock_id = reference_clock_id
        self.reference_timestamp = reference_timestamp
        self.originate_timestamp = originate_timestamp
        self.receive_timestamp = receive_timestamp
        self.transmit_timestamp = transmit_timestamp
        self.destination_timestamp = destination_timestamp

    def to_bytes(self):
        try:
            return self._FORMAT.pack(
                self.leap << 6 | self.version << 3 | self.mode,
                self.stratum,
                self.poll_interval,
                self.precision,
                int(self.root_delay * _LSB16),
                int(self.root_dispersion * _LSB16),
                self.reference_clock_id,
                int((self.reference_timestamp + DELTA) * _LSB32),
                int((self.originate_timestamp + DELTA) * _LSB32),
                int((self.receive_timestamp + DELTA) * _LSB32),
                int((self.transmit_timestamp + DELTA) * _LSB32),
            )
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")

    @classmethod
    def from_bytes(cls, data):
        try:
            raw = cls._FORMAT.unpack(data[:cls._FORMAT.size])
        except struct.error:
            raise NTPException("Invalid NTP packet.")
        return cls(
            leap=raw[0] >> 6 & 0x3,
            version=raw[0] >> 3 & 0x7,
            mode=raw[0] & 0x7,
            stratum=raw[1],
            poll_interval=raw[2],
            precision=raw[3],
            root_delay=raw[4] / _LSB16,
            root_dispersion=raw[5] / _LSB16,
            reference_clock_id=raw[6],
            reference_timestamp=raw[7] / _LSB32 - DELTA,
            originate_timestamp=raw[8] / _LSB32 - DELTA,
            receive_timestamp=raw[9] / _LSB32 - DELTA,
            transmit_timestamp=raw[10] / _LSB32 - DELTA,
        )

    @property
    def offset(self):
        return ((self.receive_timestamp - self.originate_timestamp) +
                (self.transmit_timestamp - self.destination_timestamp)) / 2

    @property
    def delay(self):
        return ((self.destination_timestamp - self.originate_timestamp) -
                (self.transmit_timestamp - self.receive_timestamp))

    @property
    def remote_datetime(self):
        return datetime.datetime.fromtimestamp(self.receive_timestamp)
