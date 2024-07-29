import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend, which doesn't require a display
import matplotlib.pyplot as plt

# Set up MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

# Set up the voltage and current channels
voltage_channel = AnalogIn(mcp, MCP.P0)
current_channel = AnalogIn(mcp, MCP.P1)

# Constants
SAMPLES = 1000
SAMPLE_RATE = 1000  # Hz
VCC = 3.3
ADC_MAX = 65535
MAINS_FREQUENCY = 60  # Hz
VOLTAGE_CALIBRATION_FACTOR = 71.7  # Adjusted based on actual measurements
CURRENT_CALIBRATION_FACTOR = 0.2535

def read_signals():
    voltage_samples = []
    current_samples = []
    start_time = time.monotonic()
    for _ in range(SAMPLES):
        voltage_samples.append(voltage_channel.value)
        current_samples.append(current_channel.value)
        while time.monotonic() - start_time < 1/SAMPLE_RATE:
            pass
        start_time += 1/SAMPLE_RATE
    
    raw_voltage = np.mean(voltage_samples)
    raw_current = np.mean(current_samples)
    
    voltages = np.array(voltage_samples) / ADC_MAX * VCC * VOLTAGE_CALIBRATION_FACTOR
    currents = np.array(current_samples) / ADC_MAX * VCC * CURRENT_CALIBRATION_FACTOR
    
    return voltages, currents, raw_voltage, raw_current

def calculate_power_parameters(voltages, currents):
    v_rms = np.sqrt(np.mean(voltages**2))
    i_rms = np.sqrt(np.mean(currents**2))
    apparent_power = v_rms * i_rms
    active_power = np.mean(voltages * currents)
    power_factor = active_power / apparent_power if apparent_power != 0 else 0
    phase_angle = np.arccos(power_factor)
    reactive_power = apparent_power * np.sin(phase_angle)
    return v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle

# Set up the plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, SAMPLES/SAMPLE_RATE)
ax.set_ylim(-200, 200)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V) / Current (A)')
ax.grid(True)

print("Raw V ADC, Raw I ADC, V_RMS, I_RMS, Apparent Power, Active Power, Reactive Power, Power Factor, Phase Angle")

while True:
    voltages, currents, raw_voltage, raw_current = read_signals()
    v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle = calculate_power_parameters(voltages, currents)
    
    # Clear the axis and plot new data
    ax.clear()
    time_axis = np.linspace(0, SAMPLES/SAMPLE_RATE, SAMPLES)
    ax.plot(time_axis, voltages, label='Voltage')
    ax.plot(time_axis, currents * 50, label='Current (x50)')  # Scale current for visibility
    ax.set_xlim(0, SAMPLES/SAMPLE_RATE)
    ax.set_ylim(-200, 200)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (V) / Current (A)')
    ax.legend()
    ax.grid(True)
    ax.set_title(f'V_RMS: {v_rms:.2f}V, I_RMS: {i_rms:.2f}A, PF: {power_factor:.2f}\n'
                 f'S: {apparent_power:.2f}VA, P: {active_power:.2f}W, Q: {reactive_power:.2f}VAR')
    
    # Save the plot as an image
    plt.savefig('power_plot.png')
    
    # Print values in comma-separated format
    print(f"{raw_voltage:.0f}, {raw_current:.0f}, {v_rms:.3f}, {i_rms:.3f}, {apparent_power:.3f}, {active_power:.3f}, {reactive_power:.3f}, {power_factor:.3f}, {np.degrees(phase_angle):.3f}")
    
    time.sleep(1)

# To calibrate voltage:
# 1. Measure actual voltage with a multimeter
# 2. Note the reported V_RMS from this script
# 3. Calculate new calibration factor:
#    NEW_FACTOR = (ACTUAL_VOLTAGE / REPORTED_V_RMS) * CURRENT_VOLTAGE_CALIBRATION_FACTOR
# 4. Update VOLTAGE_CALIBRATION_FACTOR with the new value
