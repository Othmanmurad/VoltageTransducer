import time
import pandas as pd
from gpiozero import MCP3008

class MCP3008Reader:
    def __init__(self, channel, vref=5.0):
        self.channel = channel
        self.adc = MCP3008(channel=channel)
        self.vref = vref

    def get_voltage(self):
        raw_value = self.adc.value  # Read the raw ADC value (0 to 1)
        voltage = raw_value * self.vref  # Convert to actual voltage using Vref
        return voltage

    def scale_voltage(self, voltage):
        # Scale the voltage from 1-5V range to 0-10V range
        # (voltage - 1V) maps 1-5V to 0-4V, multiply by 2.5 to get 0-10V
        if voltage < 1:
            return 0.0
        scaled_voltage = (voltage - 1) * (10 / 4)
        return scaled_voltage

def main():
    # Initialize the MCP3008 reader for the desired channel (e.g., channel 0)
    voltage_reader = MCP3008Reader(channel=0, vref=5.0)

    # Create an empty DataFrame to store the voltage readings and timestamps
    data = pd.DataFrame(columns=["Timestamp", "Scaled Voltage (V)"])

    try:
        while True:
            voltage = voltage_reader.get_voltage()
            scaled_voltage = voltage_reader.scale_voltage(voltage)
            timestamp = pd.Timestamp.now()
            
            # Append the new data to the DataFrame
            data = data.append({"Timestamp": timestamp, "Scaled Voltage (V)": scaled_voltage}, ignore_index=True)
            
            # Print the voltage value and timestamp
            print(f"Timestamp: {timestamp}, Scaled Voltage: {scaled_voltage:.2f} V")
            
            # Save the DataFrame to an Excel sheet
            data.to_excel("scaled_voltage_readings.xlsx", index=False)
            
            # Wait for the specified interval before taking the next reading
            time.sleep(1)

    except KeyboardInterrupt:
        # If the user interrupts (Ctrl+C), exit the loop
        print("\nMeasurement stopped by user.")

if __name__ == "__main__":
    main()
