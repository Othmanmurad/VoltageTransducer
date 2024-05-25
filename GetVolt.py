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
voltage_range = 500  # Voltage transducer range (500V for VACT500-42L)
resistor_value = 250  # Current-to-voltage conversion resistor value (in ohms)

def read_voltage():
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]

    # Convert digital value to voltage
    voltage = (digital_value / 1023.0) * vref

    # Scale voltage to the transducer's range
    scaled_voltage = (voltage / (20 - 4)) * voltage_range

    return scaled_voltage

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
