import time
from gpiozero import MCP3008

# Create an analog input channel on pin 0
adc = MCP3008(channel=0)

# Voltage transducer specifications
V_IN_MAX = 500  # Maximum input voltage of VACT500-42L
V_OUT_MAX = 10  # Maximum output voltage of VACT500-42L

def read_voltage():
    # Read the raw ADC value (0 to 1)
    raw_value = adc.value
    
    # Convert raw value to voltage (0-10V range)
    measured_voltage = raw_value * V_OUT_MAX
    
    # Scale the measured voltage to the actual input voltage
    actual_voltage = measured_voltage * (V_IN_MAX / V_OUT_MAX)
    
    return actual_voltage

def main():
    try:
        while True:
            voltage = read_voltage()
            print(f"Measured voltage: {voltage:.2f} V")
            time.sleep(1)  # Wait for 1 second before next reading
    except KeyboardInterrupt:
        print("Measurement stopped by user")

if __name__ == "__main__":
    main()
