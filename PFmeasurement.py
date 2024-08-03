import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
from gpiozero import MCP3008
from datetime import datetime

# Set up MCP3008 for voltage and current sensors
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

# Set up the voltage and current channels
voltage_channel = AnalogIn(mcp, MCP.P1)
current_channel = AnalogIn(mcp, MCP.P0)

# Set up MCP3008 for current transducer
transducer = MCP3008(channel=2)  # Assuming channel 2 is used for the transducer

# Constants
SAMPLES = 1000
SAMPLE_RATE = 1000  # Hz
VCC = 3.3
ICC = 5.0
ADC_MAX = 65535
MAINS_FREQUENCY = 60  # Hz
VOLTAGE_CALIBRATION_FACTOR = 71.7  # Adjusted based on actual measurements
CURRENT_CALIBRATION_FACTOR = 5.0
TRANSFORMER_VREF = 5.0
CURRENT_TRANSFORMER_FACTOR = 6.8
IDLE_THRESHOLD = 0.1  # Current value to consider as idle mode (A)

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
    
    voltages = np.array(voltage_samples) / ADC_MAX * VCC * VOLTAGE_CALIBRATION_FACTOR
    currents = np.array(current_samples) / ADC_MAX * ICC * CURRENT_CALIBRATION_FACTOR
    
    return voltages, currents

def calculate_power_parameters(voltages, currents):
    v_rms = np.sqrt(np.mean(voltages**2))
    i_rms = np.sqrt(np.mean(currents**2))
    apparent_power = v_rms * i_rms
    active_power = np.mean(voltages * currents)
    power_factor = active_power / apparent_power if apparent_power != 0 else 0
    phase_angle = np.arccos(power_factor)
    reactive_power = apparent_power * np.sin(phase_angle)
    return v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle

def get_transducer_current():
    voltage = transducer.value * TRANSFORMER_VREF
    current = voltage * CURRENT_TRANSFORMER_FACTOR
    return current

print("Timestamp, V_RMS, I_RMS, Apparent Power, Active Power, Reactive Power, Power Factor, Phase Angle")

while True:
    # Read signals from sensors
    voltages, currents = read_signals()
    v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle = calculate_power_parameters(voltages, currents)
    
    # Get current from transducer
    transducer_current = get_transducer_current()

    # Check if load is in idle mode
    if transducer_current < IDLE_THRESHOLD:
        i_rms = 0.0  # Set I_rms to 0 if in idle mode
        apparent_power = 0.0
        active_power = 0.0
        reactive_power = 0.0
        power_factor = 0.0
        phase_angle = 0.0

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print the values
    print(f"{timestamp}, {v_rms:.3f}, {i_rms:.3f}, {apparent_power:.3f}, {active_power:.3f}, {reactive_power:.3f}, {power_factor:.3f}, {np.degrees(phase_angle):.3f}")
    
    time.sleep(1)
