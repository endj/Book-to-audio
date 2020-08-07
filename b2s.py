import pyttsx3
import sys
import re
import threading
import textract
from enum import Enum

engine = pyttsx3.init()


class ReadState(Enum):
    PAUSED = 1
    READING = 2
    READ_NEXT = 3


def speak(text):
    engine.say(text)
    engine.runAndWait()


def read_pdf_as_text(path):
    return textract.process(path)


def read_file_as_text(path):
    with open(path, 'r') as file:
        return file.read()


def sentence_generator(text):
    for sentence in re.split("[,.?!]", text):
        yield sentence
# Read pdfs and textfiles as string/sentences


state = ReadState.PAUSED


def read_loop(condition):
    while True:
        with condition:
            condition.wait()
        while state == ReadState.READING:
            sentence = next(generator)
            speak(sentence)
        if state == ReadState.READ_NEXT:
            sentence = next(generator)
            speak(sentence)


# Given some text read it out load
path_to_file = sys.argv[1]

content = ""
if path_to_file.endswith('.pdf'):
    content = str(read_pdf_as_text(path_to_file), encoding='UTF-8')
else:
    content = read_file_as_text(path_to_file)

generator = sentence_generator(content)

condition = threading.Condition()

read_thread = threading.Thread(target=read_loop, args=[condition])
read_thread.setDaemon(True)
read_thread.start()

print("""
next: To read next sentence
start: Continious playback
pause: Stop playback after current sentence.
exit: Quit
""")

while True:
    input_data = input()
    with condition:
        if input_data == 'start':
            state = ReadState.READING
            condition.notifyAll()
        elif input_data == 'pause':
            state = ReadState.PAUSED
            condition.notifyAll()
        elif input_data == 'next':
            state = ReadState.READ_NEXT
            condition.notifyAll()
        elif input_data == 'exit':
            sys.exit(0)
