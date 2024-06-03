import time
from gpiozero import MCP3008
import pandas as pd

class MCP3008Reader:
    def __init__(self, channel, vref=5.0):
        self.channel = channel
        self.adc = MCP3008(channel=channel)
        self.vref = vref

    def get_voltage(self):
        raw_value = self.adc.value  # Read the raw ADC value (0 to 1)
        voltage = raw_value * self.vref  # Convert to actual voltage using Vref
        return voltage

def main():
    # Initialize the MCP3008 reader for the desired channel (e.g., channel 0)
    voltage_reader = MCP3008Reader(channel=0, vref=5.0)  # Set Vref to 5.0V

    # Create an empty DataFrame to store the voltage readings and timestamps
    data = pd.DataFrame(columns=["Timestamp", "Voltage (V)"])

    try:
        while True:
            voltage = voltage_reader.get_voltage()
            timestamp = pd.Timestamp.now()
            
            # Append the new data to the DataFrame
            data = data.append({"Timestamp": timestamp, "Voltage (V)": voltage}, ignore_index=True)
            
            # Print the voltage value and timestamp
            print(f"Timestamp: {timestamp}, Voltage: {voltage:.2f} V")
            
            # Save the DataFrame to an Excel sheet
            data.to_excel("voltage_readings.xlsx", index=False)
            
            # Wait for the specified interval before taking the next reading
            time.sleep(1)

    except KeyboardInterrupt:
        # If the user interrupts (Ctrl+C), exit the loop
        print("\nMeasurement stopped by user.")

if __name__ == "__main__":
    main()
