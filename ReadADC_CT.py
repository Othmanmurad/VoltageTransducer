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
SAMPLES = 100
VCC = 3.3
EXPECTED_RMS_CURRENT = 0.48  # The expected RMS current from your ammeter
ADC_MAX = 65535  # Maximum value of the ADC

def read_adc():
    samples = [current_channel.value for _ in range(SAMPLES)]
    return np.mean(samples)

# Print header
print("Raw ADC, ADC Voltage, Calculated Current, Calibration Factor")

# Initialize calibration factor
calibration_factor = 1.0

while True:
    raw_adc = read_adc()
    adc_voltage = (raw_adc / ADC_MAX) * VCC
    
    # Calculate current using the calibration factor
    calculated_current = adc_voltage * calibration_factor
    
    # Adjust calibration factor
    if abs(calculated_current - EXPECTED_RMS_CURRENT) > 0.01:  # If off by more than 0.01A
        calibration_factor = EXPECTED_RMS_CURRENT / adc_voltage
    
    # Print values in comma-separated format
    print(f"{raw_adc:.0f}, {adc_voltage:.4f}, {calculated_current:.4f}, {calibration_factor:.4f}")
    
    time.sleep(1)
