from machine import UART, Pin
import time
import ustruct

# Setup UART for RS485 communication
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), parity=None, stop=1)

# RS485 control pin
rs485_ctrl = Pin(3, Pin.OUT)
rs485_ctrl.value(1)  # Set to high to enable transmitting


# Function to calculate CRC16
def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


# Function to read register
def read_register(device_addr, start_addr, num_regs):
    request = ustruct.pack(">BBHH", device_addr, 0x03, start_addr, num_regs)
    crc = crc16(request)
    request += ustruct.pack("<H", crc)

    rs485_ctrl.value(1)
    uart.write(request)
    rs485_ctrl.value(0)

    time.sleep(0.1)

    response = uart.read(5 + 2 * num_regs)
    if response:
        resp_crc = ustruct.unpack("<H", response[-2:])[0]
        if crc16(response[:-2]) == resp_crc:
            return response
    return None


# Function to parse response
def parse_response(response, num_regs):
    data = []
    for i in range(num_regs):
        reg_value = ustruct.unpack(">H", response[3 + 2 * i : 5 + 2 * i])[0]
        data.append(reg_value)
    return data


# Device address
device_address = 0x01

# Register addresses
registers = {
    "ph": 0x0006,
    "moisture": 0x0012,
    "temperature": 0x0013,
    "conductivity": 0x0015,
    "nitrogen": 0x001E,
    "phosphorus": 0x001F,
    "potassium": 0x0020,
}

while True:
    for key, reg in registers.items():
        response = read_register(device_address, reg, 1)
        if response:
            data = parse_response(response, 1)
            raw_value = data[0]
            if key == "temperature":
                value = (
                    raw_value / 10.0
                    if raw_value < 0x8000
                    else (raw_value - 0x10000) / 10.0
                )
            elif key in ["moisture", "ph"]:
                value = raw_value / 10.0
            else:
                value = raw_value

            print(f"{key}: {value} (Raw: {raw_value})")
        else:
            print(f"Failed to read {key}")

    print("")
    time.sleep(1)
