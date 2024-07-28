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
SAMPLES = 100  # Number of samples to take for each measurement
VCC = 3.3  # Supply voltage to MCP3008
CT_BURDEN_RESISTOR = 220  # Burden resistor value in ohms
CT_TURNS = 2000  # Number of turns in the current transformer

# You may need to adjust this based on your specific current transformer
CT_CALIBRATION_FACTOR = 1.0  

def read_current():
    samples = [current_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    voltage = (avg_raw / 65535) * VCC
    
    # Convert voltage to current
    primary_current = (voltage / CT_BURDEN_RESISTOR) * CT_TURNS * CT_CALIBRATION_FACTOR
    return avg_raw, voltage, primary_current

# Print header
print("Raw ADC, Sensor Voltage, RMS Current")

while True:
    raw_value, sensor_voltage, primary_current = read_current()
    rms_current = primary_current / np.sqrt(2)
    
    # Print values in comma-separated format
    print(f"{raw_value:.0f}, {sensor_voltage:.3f}, {rms_current:.3f}")
    
    time.sleep(1)
