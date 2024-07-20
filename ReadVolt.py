
import time
import spidev
import RPi.GPIO as GPIO

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

    # Convert average ADC value to voltage across the resistor
    resistor_voltage = (avg_adc_value / 1023.0) * vref

    # Scale the resistor voltage to 0-10V range
    # 1V corresponds to 4mA, 5V corresponds to 20mA
    scaled_voltage = (resistor_voltage - 1) * (10 / 4)

    # Ensure scaled voltage is within 0-10V range
    scaled_voltage = max(0, min(scaled_voltage, 10))

    # Calculate current from resistor voltage
    current = (resistor_voltage / resistor_value) * 1000  # Convert to mA

    # Calculate measured voltage based on current
    measured_voltage = ((current - 4) / 16) * 500  # 4-20mA maps to 0-500V

    return avg_adc_value, resistor_voltage, current, measured_voltage, scaled_voltage

# Print CSV header
print("Timestamp,ADC Value,Resistor Voltage (V),Current (mA),Measured Voltage (V),Scaled Voltage (0-10V)")

try:
    while True:
        avg_adc_value, resistor_voltage, current, measured_voltage, scaled_voltage = read_voltage()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Print the readings in CSV format
        print(f"{timestamp},{avg_adc_value:.2f},{resistor_voltage:.4f},{current:.4f},{measured_voltage:.2f},{scaled_voltage:.4f}")

        time.sleep(30)  # Delay between readings (in seconds)

except KeyboardInterrupt:
    print("Measurement stopped by the user.")

finally:
    # Close the SPI connection
    spi.close()
    GPIO.cleanup()
