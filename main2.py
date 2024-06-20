from machine import Pin, UART
import time

# Pin definitions
RE_PIN = 6
DE_PIN = 7

# RS485 commands
TEMP_CMD = bytearray([0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xCF])
MOIS_CMD = bytearray([0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F])
ECON_CMD = bytearray([0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xCE])
PH_CMD = bytearray([0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0B])
NITRO_CMD = bytearray([0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C])
PHOS_CMD = bytearray([0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC])
POTA_CMD = bytearray([0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0])

# Initialize UART
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))


def read_sensor(cmd):
    uart.write(cmd)
    time.sleep(0.2)  # Delay to allow response bytes to be received
    if uart.any():
        response = uart.read(7)
        return response
    return None


def get_value(cmd):
    uart.write(cmd)
    time.sleep(0.2)
    time.sleep(0.2)
    response = uart.read(7)
    if response:
        return response[3] << 8 | response[4]
    return None


def main():
    while True:
        # Moisture
        val1 = get_value(MOIS_CMD)
        if val1 is not None:
            soil_mois = val1 / 1.8
            print(f"Moisture: {soil_mois:.2f} %")

        # Temperature
        val2 = get_value(TEMP_CMD)
        if val2 is not None:
            soil_temp = val2 / 10.0
            print(f"Temperature: {soil_temp:.2f} C")

        # EC
        val3 = get_value(ECON_CMD)
        if val3 is not None:
            print(f"EC: {val3} us/cm")

        # pH
        val4 = get_value(PH_CMD)
        if val4 is not None:
            soil_ph = val4 / 25.0
            print(f"pH: {soil_ph:.2f}")

        # Nitrogen
        val5 = get_value(NITRO_CMD)
        if val5 is not None:
            print(f"Nitrogen: {val5} mg/kg")

        # Phosphorous
        val6 = get_value(PHOS_CMD)
        if val6 is not None:
            print(f"Phosphorous: {val6} mg/kg")

        # Potassium
        val7 = get_value(POTA_CMD)
        if val7 is not None:
            print(f"Potassium: {val7} mg/kg")

        print()
        time.sleep(3)


if __name__ == "__main__":
    main()
