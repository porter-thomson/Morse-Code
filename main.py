# Import necessary FastAPI modules and external dependencies
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, File, UploadFile
# Import google speech-to-text api and os
from google.cloud import speech
import os
# Import subprocess, used to convert webm to flac
import subprocess
# Import numpy, and the code that translate text into morse
import dotdash as dd
import numpy as np

# Create the FastAPI app instance
app = FastAPI()

# Set up Jinja2 to look for HTML templates in the 'templates' directory
templates = Jinja2Templates(directory="templates")

# Route for the root URL ("/") that returns an HTML page
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/translate")
# Accepts a str of text from the frontend, returns the translated morse code of the text.
async def translate(text: str):
    morse = translate(text.lower())
    return {"morse": morse}

@app.get("/morse_translate")
# Accepts a str of morse code from the frontend, returns the translated english text
async def translate(text: str):
    morse = morseTranslate(text)
    return {"morseTranslate": morse}

@app.get("/listen")
# Accepts a (str) of morse code from the frontend, Translates it into sine waves,
# and returns a wav file of the translated code.
async def listen(text: str):
    return StreamingResponse(play_code(text), media_type="audio/wav")

@app.get("/set_speed")
# Sets the amplitude of the sine wave determined by the user input.
# Args:
#       speed (float): The new speed set by the user.
async def speed(speed: float):
    set_time(speed)
    return True

@app.get("/set_freq")
# Sets the frequency of the sine wave determined by the user input.
# Args:
#       freq (float): the user input of the new frequency.
async def freq(freq: float):
    set_freq(freq)
    return True

@app.post("/audio")
# Accepts an audio file from the frontend, converts it to FLAC,
# and sends it to Google Speech-to-Text for transcription.
# Args:
#       file (Webm): Audio file from user for audio transcription.
# Ret:
#       dictionary of the captions for the FLAC file and the morse code translation.
async def audio(file: UploadFile = File(...)):
    contents = await file.read()
    print("file received: ", file.filename)
    file_path = "audio.wav"
    flac_path = "audio.flac"
    with open(file_path, "wb") as f:
        f.write(contents)

    convert_wav_to_flac(file_path, flac_path)
    return audio_transcription(flac_path)

# Enable Cross-Origin Resource Sharing (CORS) to allow frontend to make API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development; restrict in production!)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the basic dotdash signals used to represent Morse code sounds
DOT = dd.dot()
DASH = dd.dash()
PAUSE = dd.pause()
SPACE = dd.space()

# Morse code mapping for characters and digits
ALPHABET = {
    'a': '.-',
    'b': '-...',
    'c': '-.-.',
    'd': '-..',
    'e': '.',
    'f': '..-.',
    'g': '--.',
    'h': '....',
    'i': '..',
    'j': '.---',
    'k': '-.-',
    'l': '.-..',
    'm': '--',
    'n': '-.',
    'o': '---',
    'p': '.--.',
    'q': '--.-',
    'r': '.-.',
    's': '...',
    't': '-',
    'u': '..-',
    'v': '...-',
    'w': '.--',
    'x': '-..-',
    'y': '-.--',
    'z': '--..',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----',
    '.': '.-.-.-',
    '?': '..--..',
    ',': '--..--',
    '"': '.-..-.',
    ' ': '/',  # Special symbol to represent space
}
REVERSED_ALPHABET = dict(zip(ALPHABET.values(), ALPHABET.keys()))

# Main function for command-line execution (not used in web app)
def main():
    user_input = input("What do you want to translate: ")
    code = translate(user_input.lower())
    set_time(.1)  # Set the dot/dash duration
    print(code)
    play_code(code)  # Play the audio version of the Morse code

# Translate input text to Morse code using the ALPHABET mapping
# Args:
#       translate (str): user input text
# Ret:
#       code (str): The translated morse code of the input text
def translate(translate):
    code = ""
    space = True
    for char in translate:
        if char in ALPHABET:
            if not space:
                code = code + ' '  # Represents pause between characters
            code = code + ALPHABET[char]
            if char == ' ':
                space = True
            else:
                space = False
    return code

# Translates morse code to Text using the REVERSE ALPHABET mapping
# Args:
#       translate (str): The morse code that needs to be translated
# Ret:
#       code (str): The translated text.
def morseTranslate(translate):
    letters = translate.split(" ")
    code = ""
    for letter in letters:
        if "/" in letter:
            code += " "
            letter = letter[1:]
        if letter in REVERSED_ALPHABET:
            code += REVERSED_ALPHABET[letter]
    return code

# Update the timing of DOT, DASH, PAUSE, and SPACE based on a new time interval
# Args:
#       new_time (float): The new time interval that the user sets.
def set_time(new_time):
    dd.set_time(new_time)
    global DOT
    DOT = dd.dot()
    global DASH
    DASH = dd.dash()
    global PAUSE
    PAUSE = dd.pause()
    global SPACE
    SPACE = dd.space()

# Updates the frequency of the sine wave and updates the values of DOT and DASH
# Args:
#       new_freq (float): The new frequency set by the user.
def set_freq(new_freq):
    dd.set_freq(new_freq)
    global DOT
    DOT = dd.dot()
    global DASH
    DASH = dd.dash()

# Convert the Morse code string into audio output using dotdash
# Args:
#       code (str): Morse code that needs to be converted to an audio file
# Ret:
#       Audio transcription of the morse code in bytes
def play_code(code):
    output = []
    print(type(code))
    for char in code:
        if char == '.':
            output += DOT
        elif char == '-':
            output += DASH
        elif char == '/':
            output += SPACE  # Space between words
        else:
            output += PAUSE  # Pause between letters
    
    output = np.array(output, dtype=np.int16)
    return dd.wav_file(output)

# Creates a transcription of a FLAC file then translates the captions
# into morse code.
# Args:
#       file_path (str): path to the FLAC file.
# Ret:
#       Dictionary of the captions of the FLAC file along with translated morse code.
def audio_transcription(file_path):
    # Setup client
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        audio_content = audio_file.read()

    # Build the request
    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript + " "
    os.remove("audio.flac")
    os.remove("audio.wav")
    return {"morse": translate(transcription.lower()), "caption" : transcription}

# Converts a wav file to a flac file.
# Args:
#   wav_path (str): path to input WAV file.
#   flac_path (str): path where the output FLAC file will be saved.
def convert_wav_to_flac(wav_path: str, flac_path: str):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_path,
        "-ar", "16000",  # 16 kHz sample rate
        "-ac", "1",       # mono channel
        flac_path
    ], check=True)

# Run the CLI version of the app if the script is executed directly
if __name__ == "__main__":
    main()
