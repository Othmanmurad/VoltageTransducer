import time
from gpiozero import MCP3008
from datetime import datetime

# Create an analog input channel on pin 0
adc = MCP3008(channel=0)

# Voltage transducer specifications
V_IN_MAX = 500  # Maximum input voltage of VACT500-42L
V_OUT_MAX = 10  # Maximum output voltage of VACT500-42L

def read_voltage():
    # Read the raw ADC value (0 to 1)
    raw_value = adc.value
    
    # Convert raw value to voltage (0-10V range)
    transducer_voltage = raw_value * V_OUT_MAX
    
    # Scale the measured voltage to the actual input voltage
    actual_voltage = transducer_voltage * (V_IN_MAX / V_OUT_MAX)
    
    return transducer_voltage, actual_voltage

def main():
    try:
        # Print header
        print(f"{'Timestamp':<23} {'Transducer Output (V)':<22} {'Actual Input (V)':<18}")
        print("-" * 65)
        
        while True:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Read voltages
            transducer_voltage, actual_voltage = read_voltage()
            
            # Print values in columns
            print(f"{timestamp:<23} {transducer_voltage:< 22.2f} {actual_voltage:< 18.2f}")
            
            time.sleep(1)  # Wait for 1 second before next reading
    except KeyboardInterrupt:
        print("\nMeasurement stopped by user")

if __name__ == "__main__":
    main()
