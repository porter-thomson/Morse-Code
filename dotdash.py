import wave
import numpy as np
import math
import pyaudio
from io import BytesIO


RATE = 16000 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
TIME = .1
AMPLITUDE = 1000
FREQUENCY = 1000

# Returns an array that holds the values of a sine wav based on the formula for a sine wave.
def sin_x(amp, freq, time):
    val = []
    for i in range(0, time):
        val.append(amp * math.sin(2 * math.pi * freq * i / RATE))
    return val

# Changes the global value of time based on user specification.
def set_time(new_time):
    global TIME
    TIME = new_time

# Changes the global value of frequency based on user specification.
def set_freq(new_freq):
    global FREQUENCY
    FREQUENCY = new_freq

# Generates a wav file from a byte array parameter then plays the audio.
def generate(bytearray):
    
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(bytearray))
    wf.close()

    p = pyaudio.PyAudio()
    output = 'output.wav'
    wf = wave.open("output.wav", 'rb')

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Creates a wav file from an array and returns the file.
def wav_file(array):
    buffer = BytesIO()
    
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(array))
    
    buffer.seek(0)
    return buffer

# produces a sound wave of a dot in morse code
def dot():
    val1 = sin_x(AMPLITUDE, FREQUENCY, int(TIME * RATE))
    val2 = sin_x(0, 500, int(TIME * RATE))
    return val1 + val2

# produces a sound wave of a dash in morse code
def dash():
    val1 = sin_x(AMPLITUDE, FREQUENCY, int((TIME * 3) * RATE))
    val2 = sin_x(0, 500, int(TIME * RATE))
    return val1 + val2

# produces a sound wave of a space in morse code
def space():
    return sin_x(0, 500, int((TIME * 6) * RATE))

# produces a sound wave of a pause in morse code
def pause():
    return sin_x(0, 500, int((TIME * 2) * RATE))
