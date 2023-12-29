
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from playsound import playsound
from gtts import gTTS
import pyaudio

import keyboard #exit key for microphone input
from speech_mic2wave import record_to_file #using microphone to wav from provided file

# IDLE used does not accurately locate files, will look into Linux systems
#for my compiling of the code these lines will be uncommented

#flac location: /opt/homebrew/bin/flac
flac_path = '/opt/homebrew/bin/flac'
os.environ['PATH'] += os.pathsep + os.path.dirname(flac_path)
#ffmpeg location: /opt/homebrew/bin/ffmpeg
AudioSegment.ffmpeg = '/opt/homebrew/bin/'

# setting up the recognizer
r = sr.Recognizer()

# for record_to_file
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 1024


def file_option(filename): #initial attempt to gain understanding of packages, not used in final product
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    try:
        s = r.recognize_google(audio, show_all=True)
        if "alternative" in s:
            alternatives = s['alternative']
            for alternative in alternatives:
                text = alternative['transcript']
                confidence = alternative['confidence']
                print("Text: " + text)
                print("Confidence: " + str(confidence))
                os.system("say '"+'I think you said,' + text + '!'+"'")
    except sr.WaitTimeoutError:
        print("Recognition timed out.")
    except Exception as e:
        print("Exception: " + str(e))


def mic_option(exit_key='q'):
    r.energy_threshold = 10000 #cuts out background noise
    with sr.Microphone() as source:
        print('Say something (Press "{}" to exit)'.format(exit_key))
        WAVE = "mic_wave1.wav"
        try:
            while True:
                record_to_file(WAVE)
                
                if input() == exit_key:
                    print("Transcribing...")
                    audio_transcription(WAVE)
                    break
        except sr.UnknownValueError as e:
            print("Error :", e)


def transcribe_audio(path):
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        text = r.recognize_google(audio_listened)
    return text

def audio_transcription(path):
    """Splitting the audio file into chunks
    and apply speech recognition on each of these chunks,
    increases accuracy and processing of larger files"""
    sound = AudioSegment.from_file(path)  
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    folder_name = "audio-chunks"  # creating a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    
    # processing each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        
        # translating each chunk seperately
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            speech = gTTS(text, lang='en', slow=False, tld='fr')
            speech.save("text2speech.wav")
            playsound("text2speech.wav")
            whole_text += text
            
            #creates .txt if user wishes to save .txt of .wav to computer
            with open('recorded_txt.txt', "w") as output_file: 
                output_file.write(whole_text)
            
        os.remove(chunk_filename) #removing files from created directory
    os.rmdir('audio-chunks') #removing the directory
    os.remove('text2speech.wav') #removing the temp .wav of gTTS text speech interpretation, will throw an error if the translation is empty due to incoherent input
    return whole_text

if __name__ == "__main__":
    option = input("Would you like to convert a file (enter 0) or microphone speech (enter 1)?")
    if option == '0':
        filename = input("Enter filename (with extension): ")
        
        # If user enters a sound file that is not a .wav the following will properly convert the file,
        # it is saved to the directory
        title, ext = filename.split('.')
        sound = AudioSegment.from_file(f"{title}.{ext}", format=ext)
        sound.export(f"{title}.wav", format="wav")

        audio_transcription(f"{title}.wav")
        #if (ext != '.wav'):
            #os.remove(f'{title}.wav') #if a .wav file was created from non .wav file
    elif option == '1':
        mic_option()


        #file_option(f"{title}.wav")
