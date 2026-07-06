import sounddevice as sd
import numpy as np
import subprocess
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys

# --- CONFIGURATION ---
MAX_DELAY = 7.0
FS = 44100
# Record in snappy 0.25-second chunks for a responsive UI
RECORD_DURATION = 0.25 

def write_hex(filename, data):
    with open(filename, 'w') as f:
        for sample in data:
            # Cast the numpy type to a standard Python int first
            hex_val = format(int(sample) & 0xFFFF, '04x')
            f.write(hex_val + '\n')

def compile_verilog_once():
    print("Compiling SystemVerilog pipeline...")
    try:
        subprocess.run(
            ["iverilog", "-gsystem-verilog", "-o", "sim.vvp", "tb_cross_correlator.sv", "cross_correlator.sv"], 
            check=True
        )
        print("Compilation successful! Starting live feed...")
    except subprocess.CalledProcessError:
        print("Error: Verilog compilation failed. Check your .sv files.")
        sys.exit(1)

def get_audio_and_run_sim():
    # 1. Grab a quick audio chunk
    recording = sd.rec(int(RECORD_DURATION * FS), samplerate=FS, channels=2, dtype='int16')
    sd.wait()
    
    left_audio = recording[:, 0]
    
    # 2. Find the loudest peak safely away from the absolute edges
    # (We ignore the first and last 64 samples so we always have room to slice out a 64-sample window)
    valid_window = left_audio[64:-64]
    if len(valid_window) == 0:
        return 16 # Failsafe
        
    peak_offset = np.argmax(np.abs(valid_window)) + 64
    
    # 3. Create the 64-sample phase-locked slice
    start_idx = peak_offset - 32
    end_idx = start_idx + 64
    
    write_hex("left.txt", recording[start_idx:end_idx, 0])
    write_hex("right.txt", recording[start_idx:end_idx, 1])
    
    # 4. Run ONLY the pre-compiled simulation
    result = subprocess.run(["vvp", "sim.vvp"], capture_output=True, text=True)
    
    # 5. Extract output
    match = re.search(r'LAG_OUTPUT:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))
    
    return 16 # Default to center if regex fails

# --- MATPLOTLIB SETUP ---
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

def update_gauge(frame):
    # Get the raw output from our pipeline
    raw_output = get_audio_and_run_sim()
    
    # Apply the mathematical offset
    centered_lag = raw_output - 16
    
    # Clamp and map to physics
    clamped_delay = np.clip(centered_lag, -MAX_DELAY, MAX_DELAY)
    ratio = -clamped_delay / MAX_DELAY
    angle_rad = np.arccos(ratio)
    angle_deg = np.rad2deg(angle_rad)
    
    # Clear the previous frame and redraw
    ax.clear()
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    
    # Draw the red arrow
    ax.annotate("", xy=(angle_rad, 1), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="red", lw=4))
    
    ax.set_yticklabels([])
    ax.set_title(f"LIVE Audio Source Direction\nCentered Raw Lag: {centered_lag}\nAngle: {int(angle_deg)}°", va='bottom')

if __name__ == "__main__":
    # Compile the hardware
    compile_verilog_once()
    
    # Start the continuous UI loop
    # interval=10 means it will attempt to draw the next frame 10ms after the previous one finishes
    ani = animation.FuncAnimation(fig, update_gauge, interval=10, cache_frame_data=False)
    
    # Show the plot (this will run continuously until you close the window)
    plt.show()