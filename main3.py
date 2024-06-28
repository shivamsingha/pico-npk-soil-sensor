from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import machine
import time
# RTU Host/Master setup

I2C_MODE = 0x01
UART_MODE = 0x02
DEV_ADDRESS = 0x22

DEVICE_VID = 0x3343
DEVICE_ADDRESS = 0x22

HPA = 0x01
KPA = 0x02
TEMP_C = 0x03
TEMP_F = 0x04


class DFRobotEnvironmentalSensor:
    def __init__(self, bus):
        self.i2c = machine.I2C(bus, scl=machine.Pin(27), sda=machine.Pin(26))

    def _detect_device_address(self):
        try:
            self.i2c.readfrom_mem(DEV_ADDRESS, 0x04, 2)
            return DEV_ADDRESS
        except OSError:
            return None

    def begin(self):
        return self._detect_device_address() == DEV_ADDRESS

    def get_temperature(self):
        return (int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x14, 2), 'big')* 175.00) / 1024.00 / 64.00 -45

    def get_humidity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x16, 2), 'big')/ 1024 * 100 / 64

    def get_ultraviolet_version(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x05, 2), 'big')

    def get_ultraviolet_intensity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x10, 2), 'big')

    def get_luminous_intensity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x12, 2), 'big')

    def get_atmosphere_pressure(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')/10

    def get_elevation(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')


rtu_pins = (Pin(4), Pin(5))  # (TX, RX)
uart_id = 1


def my_coil_get_cb(reg_type, address, val):
    print(
        "Custom callback, called on getting {} at {}, currently: {}".format(
            reg_type, address, val
        )
    )


register_definitions = {
    "PH": {  # custom name of a holding register
        "register": 0x0006,  # register address of the holding register
        "len": 1,  # amount of registers to request aka quantity
        "on_get_cb": my_coil_get_cb,
    },
    "Moisture": {
        "register": 0x0012,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
    "Temperature": {
        "register": 0x0013,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
    "Conductivity": {
        "register": 0x0015,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
    "Nitrogen": {
        "register": 0x001E,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
    "Phosphorus": {
        "register": 0x001F,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
    "Potassium": {
        "register": 0x0020,
        "len": 1,
        "on_get_cb": my_coil_get_cb,
    },
}


host = ModbusRTUMaster(
    pins=rtu_pins,  # given as tuple (TX, RX)
    # baudrate=9600,        # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id,  # optional, default 1, see port specific documentation
)
sensor = DFRobotEnvironmentalSensor(1)

while True:
    time.sleep(1)
    data = [sensor.get_temperature(), sensor.get_humidity(), sensor.get_ultraviolet_version(),
                    sensor.get_ultraviolet_intensity(), sensor.get_luminous_intensity(),
                    sensor.get_atmosphere_pressure(), sensor.get_elevation()]

    print(data, end='\n\n')
    try:
        for x, y in register_definitions.items():
            print(x, host.read_holding_registers(0x01, y["register"], 1), end='\n\n')
    except KeyboardInterrupt:
        print("KeyboardInterrupt, stopping TCP client...")
        break
    except Exception as e:
        print("Exception during execution: {}".format(e))
