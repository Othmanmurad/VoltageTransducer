import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
import matplotlib
matplotlib.use('Agg')
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
VOLTAGE_CALIBRATION_FACTOR = 71.7
CURRENT_CALIBRATION_FACTOR = 0.2535 / 2  # Halved to address ADC saturation
CURRENT_THRESHOLD = 0.1  # Adjust based on your observations

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
    
    # Apply threshold to current
    i_rms = i_rms if i_rms > CURRENT_THRESHOLD else 0
    
    apparent_power = v_rms * i_rms
    active_power = np.mean(voltages * currents)
    power_factor = active_power / apparent_power if apparent_power != 0 else 0
    phase_angle = np.arccos(power_factor)
    reactive_power = apparent_power * np.sin(phase_angle)
    return v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle

# Set up the plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Voltage (V) / Current (A)')
ax1.grid(True)

ax2.set_xlabel('Time (minutes)')
ax2.set_ylabel('Current (A)')
ax2.grid(True)

print("Raw V ADC, Raw I ADC, V_RMS, I_RMS, Apparent Power, Active Power, Reactive Power, Power Factor, Phase Angle")

current_history = []
time_history = []
start_time = time.time()

while True:
    voltages, currents, raw_voltage, raw_current = read_signals()
    v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle = calculate_power_parameters(voltages, currents)
    
    # Clear the axes and plot new data
    ax1.clear()
    ax2.clear()
    
    time_axis = np.linspace(0, SAMPLES/SAMPLE_RATE, SAMPLES)
    ax1.plot(time_axis, voltages, label='Voltage')
    ax1.plot(time_axis, currents * 50, label='Current (x50)')  # Scale current for visibility
    ax1.set_xlim(0, SAMPLES/SAMPLE_RATE)
    ax1.set_ylim(-200, 200)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V) / Current (A)')
    ax1.legend()
    ax1.grid(True)
    
    # Update current history
    current_history.append(i_rms)
    time_history.append((time.time() - start_time) / 60)  # Convert to minutes
    
    # Keep only the last 240 points (last 4 hours if sampling every minute)
    if len(current_history) > 240:
        current_history = current_history[-240:]
        time_history = time_history[-240:]
    
    ax2.plot(time_history, current_history)
    ax2.set_xlabel('Time (minutes)')
    ax2.set_ylabel('Current (A)')
    ax2.grid(True)
    
    fig.suptitle(f'V_RMS: {v_rms:.2f}V, I_RMS: {i_rms:.2f}A, PF: {power_factor:.2f}\n'
                 f'S: {apparent_power:.2f}VA, P: {active_power:.2f}W, Q: {reactive_power:.2f}VAR')
    
    # Save the plot as an image
    plt.savefig('power_plot.png')
    
    # Print values in comma-separated format
    print(f"{raw_voltage:.0f}, {raw_current:.0f}, {v_rms:.3f}, {i_rms:.3f}, {apparent_power:.3f}, {active_power:.3f}, {reactive_power:.3f}, {power_factor:.3f}, {np.degrees(phase_angle):.3f}")
    
    time.sleep(60)  # Wait for 1 minute before next reading
