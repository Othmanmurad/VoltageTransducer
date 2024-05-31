#pip install gpiozero pandas openpyxl


import time
import pandas as pd
from gpiozero import MCP3008

# Create an instance of MCP3008 class with the channel number
adc = MCP3008(channel=0)  # Assuming the voltage is connected to channel 0
voltage_ref = 3.3  # Reference voltage for the ADC
sampling_interval = 1  # Sampling interval in seconds

# Create an empty DataFrame to store the voltage readings and timestamps
data = pd.DataFrame(columns=["Timestamp", "Voltage (V)"])

try:
    while True:
        # Read the voltage value from the MCP3008 ADC
        voltage = adc.value * voltage_ref  # Multiply by the reference voltage (3.3V)
        
        # Get the current timestamp
        timestamp = pd.Timestamp.now()
        
        # Append the new data to the DataFrame
        data = data.append({"Timestamp": timestamp, "Voltage (V)": voltage}, ignore_index=True)
        
        # Print the voltage value and timestamp
        print(f"Timestamp: {timestamp}, Voltage: {voltage:.2f} V")
        
        # Save the DataFrame to an Excel sheet
        data.to_excel("voltage_readings.xlsx", index=False)
        
        # Wait for the specified interval before taking the next reading
        time.sleep(sampling_interval)

except KeyboardInterrupt:
    # If the user interrupts (Ctrl+C), exit the loop
    print("\nMeasurement stopped by user.")
