import time
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

# Current measurement configuration
resistor_value = 250  # Precision resistor value (in ohms)
current_min = 4  # Minimum current (mA)
current_max = 20  # Maximum current (mA)

def read_adc():
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]
    return digital_value

def read_current():
    # Read multiple ADC values and calculate the average
    adc_values = []
    for _ in range(10):
        adc_values.append(read_adc())
        time.sleep(0.01)  # Small delay between readings

    avg_adc_value = sum(adc_values) / len(adc_values)

    # Convert average ADC value to voltage
    voltage = (avg_adc_value / 1023.0) * vref

    # Calculate current from voltage using Ohm's law
    current = (voltage / resistor_value) * 1000  # Convert to mA

    return avg_adc_value, voltage, current

# Create a table to store the readings
table_data = []
headers = ["Timestamp", "ADC Value", "Voltage (V)", "Current (mA)"]

try:
    # Continuously read the current and add the values to the table
    while True:
        avg_adc_value, voltage, current = read_current()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Add the readings to the table
        table_data.append([timestamp, f"{avg_adc_value:.2f}", f"{voltage:.4f}", f"{current:.4f}"])

        # Print the table
        print(tabulate(table_data, headers, tablefmt="grid"))
        print(f"Current range: {current_min}-{current_max} mA")
        
        # Check if current is within the expected range
        if current_min <= current <= current_max:
            print("Current is within the expected range.")
        else:
            print("Warning: Current is outside the expected range!")
        
        print("\n")  # Add a blank line for readability

        time.sleep(1)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the SPI connection
    spi.close()
