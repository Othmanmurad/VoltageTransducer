import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
voltage_channel = AnalogIn(mcp, MCP.P0)

CALIBRATION_FACTOR = 1.99  # Adjust this based on your previous calibration
EXPECTED_MAINS_VOLTAGE = 120  # Expected RMS mains voltage
SAMPLES = 100  # Number of samples to take for each measurement

def read_voltage():
    samples = [voltage_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    sensor_voltage = (avg_raw / 65535) * 3.3 * CALIBRATION_FACTOR
    return avg_raw, sensor_voltage

def calculate_mains_voltage(sensor_rms_voltage):
    mains_calibration_factor = EXPECTED_MAINS_VOLTAGE / sensor_rms_voltage
    mains_voltage = sensor_rms_voltage * mains_calibration_factor
    return mains_voltage, mains_calibration_factor

# Print header
print("Raw ADC, Sensor Peak Voltage, Sensor RMS Voltage, Mains Peak Voltage, Mains RMS Voltage, Calibration Factor")

while True:
    raw_value, sensor_voltage = read_voltage()
    rms_sensor_voltage = sensor_voltage / np.sqrt(2)
    
    mains_rms_voltage, current_calibration_factor = calculate_mains_voltage(rms_sensor_voltage)
    mains_peak_voltage = mains_rms_voltage * np.sqrt(2)
    
    # Print values in comma-separated format
    print(f"{raw_value:.0f}, {sensor_voltage:.3f}, {rms_sensor_voltage:.3f}, {mains_peak_voltage:.1f}, {mains_rms_voltage:.1f}, {current_calibration_factor:.2f}")
    
    time.sleep(1)
