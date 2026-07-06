import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np

# Updated calibration: Maximum delay is now 7
MAX_DELAY = 7.0  

def run_simulation():
    # Compile and run assuming Icarus Verilog
    subprocess.run(["iverilog", "-gsystem-verilog", "-o", "sim.vvp", "tb_cross_correlator.sv", "cross_correlator.sv"], check=True)
    result = subprocess.run(["vvp", "sim.vvp"], capture_output=True, text=True)
    
    # Extract output using regex
    match = re.search(r'LAG_OUTPUT:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))
    
    print("Warning: Failed to parse Verilog output. Defaulting to center.")
    return 16 # Default to 16 (0 delay)

def draw_gauge(raw_delay):
    # Clamp delay strictly to your new physical limits to prevent math errors
    clamped_delay = np.clip(raw_delay, -MAX_DELAY, MAX_DELAY)
    
    # Symmetrical physics-based mapping using Arc-Cosine
    # -7 becomes ratio  1.0 -> arccos(1.0) = 0 degrees (Right)
    #  0 becomes ratio  0.0 -> arccos(0.0) = 90 degrees (Center)
    #  7 becomes ratio -1.0 -> arccos(-1.0) = 180 degrees (Left)
    ratio = -clamped_delay / MAX_DELAY
    angle_rad = np.arccos(ratio)
    
    # Convert back to degrees for the UI text
    angle_deg = np.rad2deg(angle_rad)
    
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    
    # Draw the red arrow
    ax.annotate("", xy=(angle_rad, 1), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="red", lw=4))
    
    ax.set_yticklabels([])
    
    # Display the math
    ax.set_title(f"Audio Source Direction\nCentered Raw Lag: {raw_delay}\nAngle: {int(angle_deg)}°", va='bottom')
    plt.show()

if __name__ == "__main__":
    verilog_output = run_simulation()
    
    # Apply the 16-sample window shift immediately
    centered_lag = verilog_output - 16
    
    print(f"Raw Verilog Pipeline Output: {verilog_output}")
    print(f"Centered Physical Lag: {centered_lag}")
    
    draw_gauge(centered_lag)