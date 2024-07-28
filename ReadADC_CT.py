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
CT_BURDEN_RESISTOR = 220
CT_TURNS = 2000
EXPECTED_RMS_CURRENT = 0.48  # The expected RMS current from your ammeter

def read_current():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    voltage = (avg_raw / 65535) * VCC
    return avg_raw, voltage

# Calibration
def calibrate():
    _, voltage = read_current()
    sensor_current = voltage / CT_BURDEN_RESISTOR
    sensor_rms_current = sensor_current / np.sqrt(2)
    return EXPECTED_RMS_CURRENT / sensor_rms_current

CT_CALIBRATION_FACTOR = calibrate()

# Print header
print("Raw ADC, Sensor Peak Current, Sensor RMS Current, Mains Peak Current, Mains RMS Current, Calibration Factor")

while True:
    raw_value, voltage = read_current()
    
    # Calculate sensor current
    sensor_peak_current = (voltage / CT_BURDEN_RESISTOR) * CT_TURNS
    sensor_rms_current = sensor_peak_current / np.sqrt(2)
    
    # Apply calibration factor to get mains current
    mains_peak_current = sensor_peak_current * CT_CALIBRATION_FACTOR
    mains_rms_current = mains_peak_current / np.sqrt(2)
    
    # Print values in comma-separated format
    print(f"{raw_value:.0f}, {sensor_peak_current:.3f}, {sensor_rms_current:.3f}, {mains_peak_current:.3f}, {mains_rms_current:.3f}, {CT_CALIBRATION_FACTOR:.4f}")
    
    time.sleep(1)
