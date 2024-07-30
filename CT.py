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
SENSOR_ZERO_VOLTAGE = 2.5  # From datasheet
SENSOR_SENSITIVITY = 0.0417  # V/A from datasheet

def read_voltage():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    return (avg_raw / ADC_MAX) * VCC

def voltage_to_current(voltage):
    return (voltage - SENSOR_ZERO_VOLTAGE) / SENSOR_SENSITIVITY

def adjust_calibration():
    print("Enter the current reading from your clamp meter (or 0 to skip):")
    clamp_reading = float(input())
    if clamp_reading == 0:
        return
    
    voltage = read_voltage()
    calculated_current = voltage_to_current(voltage)
    
    global SENSOR_SENSITIVITY
    SENSOR_SENSITIVITY = (voltage - SENSOR_ZERO_VOLTAGE) / clamp_reading
    print(f"Sensitivity adjusted to {SENSOR_SENSITIVITY:.6f} V/A")

# Print header
print("Raw ADC, Sensor Voltage, Calculated Current")

while True:
    raw_adc = current_channel.value
    adc_voltage = read_voltage()
    
    # Calculate current
    calculated_current = voltage_to_current(adc_voltage)
    
    # Print values in comma-separated format
    print(f"{raw_adc:.0f}, {adc_voltage:.4f}, {calculated_current:.4f}")
    
    time.sleep(1)
    
    # Every 10 readings, offer to adjust calibration
    if raw_adc % 10 == 0:
        print("Would you like to adjust calibration? (y/n)")
        if input().lower() == 'y':
            adjust_calibration()
