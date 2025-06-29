import pydub
import serial
import sys
from time import sleep


# --- Configuration ---
arduino_port = 'COM5' 
baud_rate = 115200
target_sample_rate = 8000
chunk_size = 64


def play_audio(file_path):
    """
    Decode the Music Format --> Processes it --> Streams it to the Arduino.
    """

    print()
    print(f"Loading and Processing '{file_path}'...")
    
    audio = pydub.AudioSegment.from_file(file_path)

    print()
    print("--- Original Audio Properties ---")
    print(f"    Channels:       {audio.channels}")
    print(f"    Frame Rate:     {audio.frame_rate} Hz")
    print(f"    Sample Width:   {audio.sample_width} bytes ({audio.sample_width * 8} - bit)")

    audio = audio.set_channels(1) # Convert to Mono
    audio = audio.set_frame_rate(target_sample_rate) # Downsample
    audio = audio.set_sample_width(1) # Convert to 8-bit (1 byte)

    print()
    print(f"Audio Processed: Mono, {target_sample_rate}Hz, 8-bit")
    
    raw_data = audio.raw_data # Get the Raw Byte Data

    print(f"Connecting to Arduino on {arduino_port} at {baud_rate} baud...")

    try:
        with serial.Serial(arduino_port, baud_rate, timeout = 1) as ser:
            sleep(2)

            print()
            print("Connection Successful. Streaming Audio...")
            print("Press [Ctrl + C] to Stop Playback at any time.")

            for i in range(0, len(raw_data), chunk_size):
                chunk = raw_data[i : i + chunk_size]
                ser.write(chunk)

            print("Finished Streaming. Playback complete.")

    except KeyboardInterrupt:
        print("Playback Interuppted by User.")

        with serial.Serial(arduino_port, baud_rate, timeout = 1) as ser:
            ser.write(b'\x00') # Write a Single Byte of 0 to set PWM Duty Cycle to 0% (Silence).
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python play.py <path_to_your_music_file>")
        sys.exit(1)
    
    music_file = sys.argv[1]
    play_audio(music_file)