import aioble
import bluetooth
import time
import random
import struct
from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin

# RTU Host/Master setup
rtu_pins = (Pin(4), Pin(5))  # (TX, RX)
uart_id = 1

register_definitions = {
    "PH": {"register": 0x0006, "len": 1},
    "Moisture": {"register": 0x0012, "len": 1},
    "Temperature": {"register": 0x0013, "len": 1},
    "Conductivity": {"register": 0x0015, "len": 1},
    "Nitrogen": {"register": 0x001E, "len": 1},
    "Phosphorus": {"register": 0x001F, "len": 1},
    "Potassium": {"register": 0x0020, "len": 1},
}

host = ModbusRTUMaster(pins=rtu_pins, uart_id=uart_id)

# BLE setup
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHARACTERISTIC_UUID = bluetooth.UUID("abcdef12-3456-7890-abcd-ef1234567890")

service = aioble.Service(SERVICE_UUID)
characteristic = aioble.Characteristic(
    service, CHARACTERISTIC_UUID, read=True, notify=True
)
aioble.register_services(service)


async def send_sensor_data():
    while True:
        try:
            for name, reg in register_definitions.items():
                data = struct.pack("f", random.uniform(0, 255))
                characteristic.write(data, send_update=True)
                await asyncio.sleep(1000)
        except Exception as e:
            print(f"Error: {e}")


async def ble_task():
    while True:
        async with await aioble.advertise(
            250000, name="SensorDevice", services=[SERVICE_UUID]
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)


async def main():
    t1 = asyncio.create_task(send_sensor_data())
    t2 = asyncio.create_task(ble_task())
    await asyncio.gather(t1, t2)


import asyncio

asyncio.run(main())
