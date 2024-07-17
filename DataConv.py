import csv
from datetime import datetime

# Input and output file names
input_file = '90mlog.csv'
output_file = '90mlog_formatted.csv'

# Read the input file and write to the output file
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write the header
    writer.writerow(['Timestamp', 'ADC Value', 'Resistor Voltage (V)', 'Current (mA)', 'Measured Voltage (V)', 'Scaled Voltage (0-10V)'])

    # Skip the header in the input file if it exists
    next(reader, None)

    for row in reader:
        # Check if the row has the expected number of columns
        if len(row) == 6:
            timestamp, adc_value, resistor_voltage, current, measured_voltage, scaled_voltage = row
            
            # Convert timestamp to a standard format if needed
            try:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If timestamp is already in the correct format, this will pass
                pass

            # Write the formatted row
            writer.writerow([
                timestamp,
                f"{float(adc_value):.2f}",
                f"{float(resistor_voltage):.4f}",
                f"{float(current):.4f}",
                f"{float(measured_voltage):.2f}",
                f"{float(scaled_voltage):.4f}"
            ])
        else:
            print(f"Skipping malformed row: {row}")

print(f"Formatted data has been written to {output_file}")
