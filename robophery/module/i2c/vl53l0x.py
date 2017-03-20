import struct
import time
from robophery.module.i2c.base import I2cModule

class Vl53L0XModule(I2cModule):
    """
    Module for VL53L0X light to distance sensor.
    """
    DEVICE_NAME = 'i2c-vl53l0x'
    # VL53L0X default address
    DEVICE_ADDR = 0x29

    VL53L0X_REG_IDENTIFICATION_MODEL_ID         = 0x00c0
    VL53L0X_REG_IDENTIFICATION_REVISION_ID      = 0x00c2
    VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD   = 0x0050
    VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x0070
    VL53L0X_REG_SYSRANGE_START                  = 0x000

    VL53L0X_REG_RESULT_INTERRUPT_STATUS         = 0x0013
    VL53L0X_REG_RESULT_RANGE_STATUS             = 0x0014


    def __init__(self, *args, **kwargs):
        self._addr = kwargs.get('addr', self.DEVICE_ADDR)
        super(Vl53L0XModule, self).__init__(*args, **kwargs)

        val1 = self.readU8(VL53L0X_REG_IDENTIFICATION_REVISION_ID)
        self._revision_id = hex(val1)
        val1 = self.readU8(VL53L0X_REG_IDENTIFICATION_MODEL_ID)
        self._device_id = hex(val1)
        val1 = self.readU8(VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD)
        val1 = self.readU8(VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD)


    def bswap(self, val):
        return struct.unpack('<H', struct.pack('>H', val))[0]


    def mread_word_data(self, adr, reg):
        return bswap(bus.read_word_data(adr, reg))


    def mwrite_word_data(self, adr, reg, data):
        return bus.write_word_data(adr, reg, bswap(data))


    def _makeuint16(self, lsb, msb):
        return ((msb & 0xFF) << 8)  | (lsb & 0xFF)


    def _decode_vcsel_period(self, vcsel_period_reg):
        """
        Converts the encoded VCSEL period register value into the real
        period in PLL clocks
        """
        vcsel_period_pclks = (vcsel_period_reg + 1) << 1;
        return vcsel_period_pclks;


    def read_distance(self):
        #        Status = VL53L0X_WrByte(Dev, VL53L0X_REG_SYSRANGE_START, 0x01);
        val1 = self.write8(VL53L0X_REG_SYSRANGE_START, 0x01)

#        Status = VL53L0X_RdByte(Dev, VL53L0X_REG_RESULT_RANGE_STATUS,
#            &SysRangeStatusRegister);
#        if (Status == VL53L0X_ERROR_NONE) {
#            if (SysRangeStatusRegister & 0x01)
#                *pMeasurementDataReady = 1;
#            else
#                *pMeasurementDataReady = 0;
#        }
        cnt = 0
        while (cnt < 100): # 1 second waiting time max
            self._msleep(10)
            val = self.readU8(VL53L0X_REG_RESULT_RANGE_STATUS)
            if (val & 0x01):
                break
            cnt += 1

#        if (val & 0x01):
#            print "ready"
#        else:
#            print "not ready"

        #Status = VL53L0X_ReadMulti(Dev, 0x14, localBuffer, 12);
        data = self.readList(0x14, 12)
        ambient_count = self._makeuint16(data[7], data[6])
        signal_count = self._makeuint16(data[9], data[8])
        #tmpuint16 = VL53L0X_MAKEUINT16(localBuffer[11], localBuffer[10]);
        distance = self._makeuint16(data[11], data[10])

        range_status_internal = ((data[0] & 0x78) >> 3)


    def read_data(self):
        """
        Get sensor reading.
        """
        read_time_start = time.time()
        distance = self.read_distance()
        read_time_stop = time.time()
        read_time_delta = read_time_stop - read_time_start
        data = [
            (self._name, 'distance', distance, read_time_delta),
        ]
        self._log_data(data)
        return data


    def meta_data(self):
        """
        Get the readings meta-data.
        """
        return {
            'distance': {
                'type': 'gauge', 
                'unit': 'm',
                'precision': 0.01,
                'range_low': 0.03,
                'range_high': 4,
                'sensor': self.DEVICE_NAME
            },
        }
