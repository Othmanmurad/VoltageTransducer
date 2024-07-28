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
CT_CALIBRATION_FACTOR = 1.5  # Adjust this based on your calibration
                             # Ammeter reading / Current RMS = Calb.Factor

def read_current():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    voltage = (avg_raw / 65535) * VCC
    
    # Convert voltage to current
    sensor_current = (voltage / CT_BURDEN_RESISTOR) * CT_TURNS
    return avg_raw, sensor_current

# Print header
print("Raw ADC, Sensor Peak Current, Sensor RMS Current, Mains Peak Current, Mains RMS Current")

while True:
    raw_value, sensor_current = read_current()
    
    # Calculate peak and RMS values
    sensor_peak_current = sensor_current
    sensor_rms_current = sensor_peak_current / np.sqrt(2)
    
    # Apply calibration factor to get mains current
    mains_peak_current = sensor_peak_current * CT_CALIBRATION_FACTOR
    mains_rms_current = mains_peak_current / np.sqrt(2)
    
    # Print values in comma-separated format
    print(f"{raw_value:.0f}, {sensor_peak_current:.3f}, {sensor_rms_current:.3f}, {mains_peak_current:.3f}, {mains_rms_current:.3f}")
    
    time.sleep(1)
