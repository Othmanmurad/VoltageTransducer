import time
import datetime
import spidev
from tabulate import tabulate

# SPI bus and device configuration
spi_bus = 0
spi_device = 0

# Create an SPI object
spi = spidev.SpiDev()

# Open the SPI bus and device
spi.open(spi_bus, spi_device)

# SPI mode and maximum clock speed
spi.mode = 0
spi.max_speed_hz = 1000000

# MCP3008 configuration
adc_channel = 0  # Analog input channel (0 to 7)
vref = 5.0  # Reference voltage (in volts)

# VACT500-42L configuration
voltage_range = 500  # VACT500-42L input voltage range (in volts)
resistor_value = 250  # Current-to-voltage conversion resistor value (in ohms)

def read_adc():
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]
    return digital_value

def read_voltage():
    # Read multiple ADC values and calculate the average
    adc_values = []
    for _ in range(10):
        adc_values.append(read_adc())
        time.sleep(0.01)  # Small delay between readings

    avg_adc_value = sum(adc_values) / len(adc_values)

    # Convert average ADC value to voltage
    voltage = (avg_adc_value / 1023.0) * vref

    # Scale the voltage to the transducer's range
    scaled_voltage = (voltage / (5.0 - 1.0)) * voltage_range

    # Handle negative scaled values
    if scaled_voltage < 0:
        scaled_voltage = 0

    return avg_adc_value, voltage, scaled_voltage

# Create a table to store the readings
table_data = []
headers = ["Timestamp", "Average ADC Value", "Voltage (V)", "Scaled Voltage (V)"]

try:
    # Continuously read the voltage and add the values to the table
    while True:
        avg_adc_value, voltage, scaled_voltage = read_voltage()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the readings to the table
        table_data.append([timestamp, avg_adc_value, voltage, scaled_voltage])

        # Print the table
        print(tabulate(table_data, headers, tablefmt="grid"))

        time.sleep(1)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the SPI connection
    spi.close()
