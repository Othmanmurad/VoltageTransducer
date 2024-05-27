import time
import spidev
import csv

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
input_voltage = 240  # Input voltage (in volts)
input_voltage_range = 500  # VACT500-42L input voltage range (in volts)
output_current_range = 16  # VACT500-42L output current range (in mA)
min_output_current = 4  # VACT500-42L minimum output current (in mA)
resistor_value = 250  # Current-to-voltage conversion resistor value (in ohms)

def read_voltage():
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]

    # Convert digital value to voltage
    voltage = (digital_value / 1023.0) * vref

    # Calculate the output current based on the input voltage
    output_current = (input_voltage / input_voltage_range) * output_current_range + min_output_current

    # Calculate the voltage across the resistor
    resistor_voltage = output_current * resistor_value / 1000  # Convert mA to A

    # Scale the resistor voltage to the expected output voltage
    expected_voltage = (resistor_voltage / (vref - (min_output_current * resistor_value / 1000))) * input_voltage_range

    return expected_voltage

# CSV file configuration
csv_file = 'voltage_data.csv'
csv_headers = ['Timestamp', 'Voltage (V)']

try:
    # Open the CSV file in write mode
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

        while True:
            voltage = read_voltage()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            # Write voltage data to the CSV file
            writer.writerow([timestamp, voltage])

            print("Voltage: {:.2f} V".format(voltage))
            time.sleep(1)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    # Close the SPI connection
    spi.close()
