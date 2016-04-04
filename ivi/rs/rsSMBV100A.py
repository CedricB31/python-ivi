from .rsBaseSM import *


class rsSMBV100A(rsBaseSM):
    "Agilent E4433B ESG-D IVI RF signal generator driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'ESG-D4000B')

        super(rsSMBV100A, self).__init__(*args, **kwargs)

        self._frequency_low = 9e3
        self._frequency_high = 3200e6
