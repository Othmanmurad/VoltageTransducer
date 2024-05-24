# Initialize Analog to Digital Converter (ADC) - MCP3008

# Import library for MCP3008 
import Adafruit_MCP3008

# MCP3008 Serial Peripheral Interface (SPI) Configuration
# Serial Clock
CLK  = 23

# Serial Data Our
DOUT = 21

# Serial Data In
DIN = 19

# Chip Select
CS   = 25

MCP = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


