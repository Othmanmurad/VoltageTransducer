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
voltage_adc_channel = 0  # Analog input channel for voltage measurement (0 to 7)
current_adc_channel = 1  # Analog input channel for current measurement (0 to 7)
vref = 5.0  # Reference voltage (in volts)

# VACT500-42L configuration
voltage_range = 500  # VACT500-42L input voltage range (in volts)
current_range = 16  # VACT500-42L output current range (in mA)
resistor_value = 250  # Current-to-voltage conversion resistor value (in ohms)

def read_adc(adc_channel):
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]
    return digital_value

def read_voltage_and_current():
    # Read multiple ADC values for voltage and current and calculate the average
    voltage_adc_values = []
    current_adc_values = []
    for _ in range(10):
        voltage_adc_values.append(read_adc(voltage_adc_channel))
        current_adc_values.append(read_adc(current_adc_channel))
        time.sleep(0.01)  # Small delay between readings

    avg_voltage_adc = sum(voltage_adc_values) / len(voltage_adc_values)
    avg_current_adc = sum(current_adc_values) / len(current_adc_values)

    # Convert average ADC values to voltage
    voltage = (avg_voltage_adc / 1023.0) * vref
    current_voltage = (avg_current_adc / 1023.0) * vref

    # Scale the voltage to the transducer's range
    scaled_voltage = (voltage / (5.0 - 1.0)) * voltage_range

    # Convert the current voltage to current (in mA)
    current = ((current_voltage - 1.0) / (5.0 - 1.0)) * current_range

    # Handle negative values
    if scaled_voltage < 0:
        scaled_voltage = 0
    if current < 0:
        current = 0

    return avg_voltage_adc, avg_current_adc, voltage, current, scaled_voltage

# Create a table to store the readings
table_data = []
headers = ["Timestamp", "Voltage ADC", "Current ADC", "Voltage (V)", "Current (mA)", "Scaled Voltage (V)"]

try:
    # Continuously read the voltage and current and add the values to the table
    while True:
        avg_voltage_adc, avg_current_adc, voltage, current, scaled_voltage = read_voltage_and_current()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the readings to the table
        table_data.append([timestamp, avg_voltage_adc, avg_current_adc, voltage, current, scaled_voltage])

        # Print the table
        print(tabulate(table_data, headers, tablefmt="grid"))

        time.sleep(1)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the SPI connection
    spi.close()
