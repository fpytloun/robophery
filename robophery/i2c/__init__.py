
#import smbus
from robophery.core import Module

#Type of I2C interface to manage system device
I2C_SMBUS_INTERFACE = 1
I2C_ADAFRUIT_I2C_INTERFACE = 2

class I2cModule(Module):

    #def set_device(self, address, bus, interface=I2C_SMBUS_INTERFACE):
    #    """
    #    Set up I2C device.
    #    """
    #    # Create I2C device.
    #    if interface is I2C_ADAFRUIT_I2C_INTERFACE:
    #        import Adafruit_GPIO.I2C as I2C
    #        #i2c = I2C
    #        self.bus = I2C.get_i2c_device(address, bus)
    #    elif (interface is I2C_SMBUS_INTERFACE):
    #        import smbus
    #        self.bus = smbus.SMBus(bus)

    def set_bus(self, bus, interface=I2C_SMBUS_INTERFACE):
        """
        Set bus for reading.
        """
        if interface is I2C_ADAFRUIT_I2C_INTERFACE:
            #Adafruit interface has bus implemented in different object
            self.bus = 0;
        elif (interface is I2C_SMBUS_INTERFACE):
            import smbus
            self.bus = smbus.SMBus(bus)

    def set_addr(self, addr):
        """
        Set address for reading.
        """
        self.addr = addr
