import time
from gpiozero import MCP3008
import numpy as np
from datetime import datetime

# ... (keep the previous setup code)

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
