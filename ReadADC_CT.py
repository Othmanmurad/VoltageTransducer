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
mcp = MCP.MCP3008(spi, cs)  # Corrected this line

# Set up the current channel
current_channel = AnalogIn(mcp, MCP.P1)

# Constants
SAMPLES = 100
VCC = 3.3
ADC_MAX = 65535
CALIBRATION_FACTOR = 0.2535  # Use the value we found

def read_current():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    adc_voltage = (avg_raw / ADC_MAX) * VCC
    return avg_raw, adc_voltage

# Print header
print("Raw ADC, Sensor Peak Current, Sensor RMS Current, Mains Peak Current, Mains RMS Current")

while True:
    raw_adc, adc_voltage = read_current()
    
    # Calculate currents
    mains_rms_current = adc_voltage * CALIBRATION_FACTOR
    mains_peak_current = mains_rms_current * np.sqrt(2)
    
    # Calculate sensor currents (assuming linear relationship)
    sensor_rms_current = adc_voltage
    sensor_peak_current = sensor_rms_current * np.sqrt(2)
    
    # Print values in comma-separated format
    print(f"{raw_adc:.0f}, {sensor_peak_current:.4f}, {sensor_rms_current:.4f}, {mains_peak_current:.4f}, {mains_rms_current:.4f}")
    
    time.sleep(1)
