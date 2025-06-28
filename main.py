# Import necessary FastAPI modules and external dependencies
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request

# Import Morse code utilities and NumPy
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
async def translate(text: str):
    morse = translate(text.lower())
    return {"morse": morse}

@app.get("/morse_translate")
async def translate(text: str):
    morse = morseTranslate(text)
    return {"morseTranslate": morse}

@app.get("/listen")
async def listen(text: str):
    return StreamingResponse(play_code(text), media_type="audio/wav")

@app.get("/set_speed")
async def speed(speed: float):
    set_time(speed)
    return True

@app.get("/set_freq")
async def freq(freq: float):
    set_freq(freq)
    return True

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

def set_freq(new_freq):
    dd.set_freq(new_freq)
    global DOT
    DOT = dd.dot()
    global DASH
    DASH = dd.dash()

# Convert the Morse code string into audio output using dotdash
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

# Run the CLI version of the app if the script is executed directly
if __name__ == "__main__":
    main()
