import sys

# ruff: noqa: E402
sys.path.append("")

from micropython import const

import asyncio
import aioble
import bluetooth

import random
import struct
from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

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

# Register GATT server.
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
aioble.register_services(temp_service)
host = ModbusRTUMaster(
    pins=rtu_pins,  # given as tuple (TX, RX)
    # baudrate=9600,        # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id,  # optional, default 1, see port specific documentation
)

# Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 10))


# This would be periodically polling a hardware sensor.
async def sensor_task():
    while True:
        temp_characteristic.write(_encode_temperature(host.read_holding_registers(0x01, register_definitions["Temperature"]["register"], 1)[0]))
        await asyncio.sleep_ms(1000)


# Serially wait for connections. Don't advertise while a central is
# connected.
async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="mpy-temp",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)


# Run both tasks.
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)


asyncio.run(main())
