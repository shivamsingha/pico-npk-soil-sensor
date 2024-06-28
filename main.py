from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import time
# RTU Host/Master setup


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
    # uart_id=uart_id,  # optional, default 1, see port specific documentation
)

while True:
    time.sleep(1)
    try:
        for x, y in register_definitions.items():
            print(x, host.read_holding_registers(0x01, y["register"], 1))
    except KeyboardInterrupt:
        print("KeyboardInterrupt, stopping TCP client...")
        break
    except Exception as e:
        print("Exception during execution: {}".format(e))
