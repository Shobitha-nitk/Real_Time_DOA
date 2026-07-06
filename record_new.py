import sounddevice as sd
import numpy as np

fs = 44100  # Sample rate
duration = 2.0  # Record for 2 full seconds

print("Playing your 1000Hz tone? Recording for 2 seconds...")
recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
sd.wait()
print("Recording complete.")

# 1. Start looking near the 1.0 second mark
base_idx = int(1.0 * fs) 

# 2. Search a small 1000-sample window to find the absolute loudest peak of the wave
search_window = recording[base_idx : base_idx + 1000, 0]
peak_offset = np.argmax(np.abs(search_window)) 

# 3. Create a 64-sample slice where the peak sits EXACTLY in the middle (index 32).
# This perfectly aligns the sound wave with the Verilog pipeline's math window.
start_idx = base_idx + peak_offset - 32
end_idx = start_idx + 64

# Extract the phase-locked samples
left_channel = recording[start_idx:end_idx, 0]
right_channel = recording[start_idx:end_idx, 1]

def write_hex(filename, data):
    with open(filename, 'w') as f:
        for sample in data:
            hex_val = format(int(sample) & 0xFFFF, '04X')
            f.write(f"{hex_val}\n")

write_hex('left.txt', left_channel)
write_hex('right.txt', right_channel)
print("Files saved: left.txt, right.txt")