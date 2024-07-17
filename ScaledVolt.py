import time
import spidev
import RPi.GPIO as GPIO
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
vref = 3.3  # Reference voltage (in volts)

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

    # Convert average ADC value to voltage across the resistor
    resistor_voltage = (avg_adc_value / 1023.0) * vref

    # Calculate current from resistor voltage
    current = (resistor_voltage / resistor_value) * 1000  # Convert to mA

    # Calculate measured voltage based on current
    # Clamping the current between 4mA and 20mA to avoid negative voltages
    clamped_current = max(current_min, min(current, current_max))
    measured_voltage = ((clamped_current - current_min) / (current_max - current_min)) * voltage_range

    # Scale the resistor voltage to 0-10V range
    # 1V corresponds to 4mA, 5V corresponds to 20mA
    scaled_voltage = (resistor_voltage - 1) * (10 / 4)
    scaled_voltage = max(0, min(scaled_voltage, 10))

    return avg_adc_value, resistor_voltage, current, measured_voltage, scaled_voltage

# Create a table to store the readings
table_data = []
headers = ["Timestamp", "ADC Value", "Resistor Voltage (V)", "Current (mA)", "Measured Voltage (V)", "Scaled Voltage (0-10V)"]

try:
    while True:
        avg_adc_value, resistor_voltage, current, measured_voltage, scaled_voltage = read_voltage()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Add the readings to the table
        table_data.append([
            timestamp,
            f"{avg_adc_value:.2f}",
            f"{resistor_voltage:.4f}",
            f"{current:.4f}",
            f"{measured_voltage:.2f}",
            f"{scaled_voltage:.4f}"
        ])

        # Print the table
        print(tabulate(table_data[-10:], headers, tablefmt="grid"))  # Show last 10 readings
        print(f"Current range: {current_min}-{current_max} mA")
        print(f"Voltage range: 0-{voltage_range} V")
        print(f"Scaled voltage range: 0-10 V")
        
        # Check if current is within the expected range
        if current_min <= current <= current_max:
            print("Current is within the expected range.")
        else:
            print(f"Warning: Current ({current:.4f} mA) is outside the expected range!")
        
        print("\n")  # Add a blank line for readability

        time.sleep(1)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the SPI connection
    spi.close()
    GPIO.cleanup()
