import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
voltage_channel = AnalogIn(mcp, MCP.P0)

while True:
    raw_value = voltage_channel.value
    voltage = (raw_value / 65535) * 3.3  # Convert to voltage
    print(f"Raw ADC: {raw_value}, Voltage: {voltage:.3f}V")
    time.sleep(1)
