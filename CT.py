import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# Set up MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

# Set up the current channel
current_channel = AnalogIn(mcp, MCP.P1)

# Constants
SAMPLES = 1000
VCC = 5.0
ADC_MAX = 65535
SENSOR_ZERO_VOLTAGE = 2.5  # We'll calibrate this
SENSOR_SENSITIVITY = 0.0417  # V/A

def read_voltage():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    return (avg_raw / ADC_MAX) * VCC

def calibrate_zero():
    print("Ensuring no current is flowing, then press Enter to calibrate zero point...")
    input()
    global SENSOR_ZERO_VOLTAGE
    SENSOR_ZERO_VOLTAGE = read_voltage()
    print(f"Zero point calibrated to {SENSOR_ZERO_VOLTAGE:.4f}V")

def voltage_to_current(voltage):
    return (voltage - SENSOR_ZERO_VOLTAGE) / SENSOR_SENSITIVITY

# Calibrate zero point
calibrate_zero()

# Print header
print("Raw ADC, Sensor Voltage, RMS Current")

while True:
    raw_adc = current_channel.value
    adc_voltage = read_voltage()
    
    # Calculate current
    rms_current = voltage_to_current(adc_voltage)
    
    # Print values in comma-separated format
    print(f"{raw_adc:.0f}, {adc_voltage:.4f}, {rms_current:.4f}")
    
    time.sleep(1)
