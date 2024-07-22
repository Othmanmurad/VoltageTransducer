import time
import spidev
import RPi.GPIO as GPIO
import csv
from datetime import datetime

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

# Time delay between each cycle in seconds
delay = 5

# MCP3008 configuration
adc_channel = 0  # Analog input channel (0 to 7)
vref = 3.3  # Reference voltage (in volts) - typically 3.3V for Raspberry Pi

# VACT500-42L configuration
voltage_range = 500  # VACT500-42L input voltage range (in volts)
current_min = 4  # Minimum current (mA)
current_max = 20  # Maximum current (mA)

# Current measurement configuration
resistor_value = 250  # Precision resistor value (in ohms)

def read_adc(channel):
    # Perform SPI transaction to read MCP3008 value
    adc_value = spi.xfer2([1, (8 + channel) << 4, 0])
    digital_value = ((adc_value[1] & 3) << 8) + adc_value[2]
    return digital_value

def read_voltage():
    # Read multiple ADC values and calculate the average
    adc_values = []
    for _ in range(10):
        adc_values.append(read_adc(adc_channel))
        time.sleep(0.01)  # Small delay between readings
    avg_adc_value = sum(adc_values) / len(adc_values)

    # Convert average ADC value to voltage across the resistor which represents
    # the output DC voltage of the voltage transducer
    Output_voltage = (avg_adc_value / 1023.0) * vref

    # Scale the resistor voltage to 0-10V range
    # 1V corresponds to 4mA, 5V corresponds to 20mA
    scaled_voltage = (Output_voltage - 1) * (10 / 4)

    # Ensure scaled voltage is within 0-10V range
    scaled_voltage = max(0, min(scaled_voltage, 10))

    # Calculate current from resistor voltage
    current = (Output_voltage / resistor_value) * 1000  # Convert to mA

    # Calculate measured voltage based on current
    Input_voltage = ((current - 4) / 16) * 500  # 4-20mA maps to 0-500V

    return avg_adc_value, Output_voltage, current, Input_voltage, scaled_voltage

# Open CSV file for writing
csv_filename = "VTlog.csv"
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)

# Write CSV header
csv_writer.writerow(["Timestamp", "ADC Value", "Output Voltage (V)", "Current (mA)", "Input Voltage (V)", "Scaled Voltage (0-10V)"])

print(f"Logging data to {csv_filename}")
print("Press Ctrl+C to stop logging")

try:
    while True:
        avg_adc_value, Output_voltage, current, Input_voltage, scaled_voltage = read_voltage()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision

        # Write the readings to CSV file
        csv_writer.writerow([timestamp, f"{avg_adc_value:.2f}", f"{Output_voltage:.4f}", 
                             f"{current:.4f}", f"{Input_voltage:.2f}", f"{scaled_voltage:.4f}"])
        csv_file.flush()  # Ensure data is written to the file

        # Also print to console
        print(f"{timestamp},{avg_adc_value:.2f},{Output_voltage:.4f},{current:.4f},{Input_voltage:.2f},{scaled_voltage:.4f}")

        time.sleep(delay)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the CSV file
    csv_file.close()
    # Close the SPI connection
    spi.close()
    GPIO.cleanup()

print(f"Data saved to {csv_filename}")
