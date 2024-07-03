import time
import board
import busio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# Create the mcp object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

# Voltage transducer specifications
V_IN_MAX = 500  # Maximum input voltage of VACT500-42L
V_OUT_MAX = 10  # Maximum output voltage of VACT500-42L

# ADC specifications
ADC_MAX = 1023  # Maximum value of 10-bit ADC

def read_voltage():
    # Read the ADC value
    adc_value = chan.value

    # Convert ADC value to voltage
    measured_voltage = (adc_value / ADC_MAX) * V_OUT_MAX

    # Scale the measured voltage to the actual input voltage
    actual_voltage = (measured_voltage / V_OUT_MAX) * V_IN_MAX

    return actual_voltage

def main():
    try:
        while True:
            voltage = read_voltage()
            print(f"Measured voltage: {voltage:.2f} V")
            time.sleep(1)  # Wait for 1 second before next reading
    except KeyboardInterrupt:
        print("Measurement stopped by user")

if __name__ == "__main__":
    main()
