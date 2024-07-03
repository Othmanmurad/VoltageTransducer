import time
from gpiozero import MCP3008
import numpy as np
from datetime import datetime

# Create an analog input channel on pin 0
adc = MCP3008(channel=0)

# Voltage transducer specifications
V_IN_MAX = 500  # Maximum input voltage of VACT500-42L
V_OUT_MAX = 10  # Maximum output voltage of VACT500-42L

# RMS calculation parameters
FREQUENCY = 60  # AC frequency (Hz)
SAMPLES_PER_CYCLE = 100  # Number of samples to take per AC cycle

def read_voltage():
    # Read the raw ADC value (0 to 1)
    raw_value = adc.value
    
    # Convert raw value to transducer output voltage (0-10V range)
    transducer_voltage = raw_value * V_OUT_MAX
    
    # Scale the measured voltage to the actual input voltage
    actual_voltage = transducer_voltage * (V_IN_MAX / V_OUT_MAX)
    
    return transducer_voltage, actual_voltage

def calculate_rms(voltages):
    return np.sqrt(np.mean(np.array(voltages)**2))

def main():
    timestamps = []
    transducer_voltages = []
    actual_voltages = []
    rms_voltages = []

    try:
        while True:
            start_time = time.time()
            cycle_voltages = []
            cycle_transducer_voltages = []
            
            for _ in range(SAMPLES_PER_CYCLE):
                transducer_v, actual_v = read_voltage()
                cycle_voltages.append(actual_v)
                cycle_transducer_voltages.append(transducer_v)
                time.sleep(1 / (FREQUENCY * SAMPLES_PER_CYCLE))
            
            rms_voltage = calculate_rms(cycle_voltages)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            timestamps.append(timestamp)
            transducer_voltages.append(cycle_transducer_voltages[-1])
            actual_voltages.append(cycle_voltages[-1])
            rms_voltages.append(rms_voltage)
            
            print(f"Timestamp: {timestamp}")
            print(f"Transducer Output: {cycle_transducer_voltages[-1]:.2f} V")
            print(f"Actual AC Voltage: {cycle_voltages[-1]:.2f} V")
            print(f"RMS Voltage: {rms_voltage:.2f} V")
            print("--------------------")
            
            time_elapsed = time.time() - start_time
            time.sleep(max(0, 1/FREQUENCY - time_elapsed))
            
    except KeyboardInterrupt:
        print("Measurement stopped by user")
        # Here you can save or process the collected data
        # For example, you could save to a CSV file:
        # import csv
        # with open('voltage_data.csv', 'w', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['Timestamp', 'Transducer Voltage', 'Actual Voltage', 'RMS Voltage'])
        #     writer.writerows(zip(timestamps, transducer_voltages, actual_voltages, rms_voltages))

if __name__ == "__main__":
    main()
