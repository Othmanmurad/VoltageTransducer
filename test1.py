import time
from gpiozero import MCP3008

class MCP3008Reader:
    def __init__(self, channel, vref=4.4):
        self.channel = channel
        self.adc = MCP3008(channel=channel)
        self.vref = vref

    def get_voltage(self):
        raw_value = self.adc.value  # Read the raw ADC value (0 to 1)
        voltage = raw_value * self.vref  # Convert to actual voltage using Vref
        return voltage

def main():
    # Initialize the MCP3008 reader for the desired channel (e.g., channel 0)
    voltage_reader = MCP3008Reader(channel=0, vref=4.4)  # Adjust Vref if necessary

    try:
        while True:
            voltage = voltage_reader.get_voltage()
            print(f"Voltage: {voltage:.2f} V")
            time.sleep(1)  # Wait for 1 second before taking the next reading

    except KeyboardInterrupt:
        print("Measurement stopped by user.")

if __name__ == "__main__":
    main()
