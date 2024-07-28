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
MAINS_CALIBRATION_FACTOR = 120 / 2.35  # Adjust this based on your voltage transformer ratio
SAMPLES = 100  # Number of samples to take for each measurement

def read_voltage():
    samples = [voltage_channel.value for _ in range(SAMPLES)]
    avg_raw = np.mean(samples)
    sensor_voltage = (avg_raw / 65535) * 3.3 * CALIBRATION_FACTOR
    mains_voltage = sensor_voltage * MAINS_CALIBRATION_FACTOR
    return avg_raw, sensor_voltage, mains_voltage

while True:
    raw_value, sensor_voltage, mains_voltage = read_voltage()
    rms_sensor_voltage = sensor_voltage / np.sqrt(2)
    rms_mains_voltage = mains_voltage / np.sqrt(2)
    
    print(f"Raw ADC: {raw_value:.0f}")
    print(f"Sensor Peak Voltage: {sensor_voltage:.3f}V, Sensor RMS Voltage: {rms_sensor_voltage:.3f}V")
    print(f"Mains Peak Voltage: {mains_voltage:.1f}V, Mains RMS Voltage: {rms_mains_voltage:.1f}V")
    print("--------------------")
    time.sleep(1)
