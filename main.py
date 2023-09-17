import json
import wave
import vosk
from datetime import datetime
import pytz

def transcribe_with_timecodes(model_path, audio_path):
    vosk.SetLogLevel(0)

    # Load the Vosk model
    model = vosk.Model(model_path)

    # Open the audio file
    wf = wave.open(audio_path, "rb")

    frames = wf.getnframes()
    
    # Check the sample rate
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
        print("Audio file must be WAV format mono PCM.")
        return
    
    framerate = wf.getframerate()

    # Initialize the recognizer
    rec = vosk.KaldiRecognizer(model, framerate)
    rec.SetWords(True)

    transcriptions = []

    frame = 0

    while True:
        #frames = frames + frame

        # Read audio data
        data = wf.readframes(4000)

        frame = frame + 4000

        number = frame / frames
        formatted_number = "{:.2%}".format(number)

        print(f"[{formatted_number}] Read {frame} from {frames}")

        if len(data) == 0:
            break
        
        # Process audio data
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            transcriptions.append(result)

    # Process remaining audio data
    results = json.loads(rec.FinalResult())

    transcriptions.append(results)

    return transcriptions

if __name__ == "__main__":
    #model_dir = "vosk-model-small-ru-0.22" # e.g., "vosk-model-en-us-aspire-0.2"
    model_dir = "vosk-model-ru-0.42"
    audio_file = "fdp_41.wav"
    
    transcriptions = transcribe_with_timecodes(model_dir, audio_file)
    with open("transcriptions.txt", "w") as f:
        for item in transcriptions:
            if "result" in item:
                start_time = item["result"][0]["start"]
                end_time = item["result"][-1]["end"]

                # Convert start_time and end_time to datetime objects
                start_time = datetime.fromtimestamp(start_time, tz=pytz.UTC)
                end_time = datetime.fromtimestamp(end_time, tz=pytz.UTC)

                start_time = start_time.strftime("%H:%M:%S")
                end_time = end_time.strftime("%H:%M:%S")

                f.write(f"[{start_time} - {end_time}] {item['text']}\n")

                continue

            f.write(f"[] {item['text']}\n")
