import tkinter.messagebox
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pydub import AudioSegment
from pathlib import Path
from vosk import Model, KaldiRecognizer
from vosk import SetLogLevel
SetLogLevel(-1)
import wave
import sys
import json
import os
import shutil

root = tk.Tk()
root.geometry('205x220')
root.resizable(False, False)
root.title("Transcribbl")

videoFile = Path()

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(".")

def extract_files():
    target_dirs = ["videos", "audios", "txt", "VoskModel"]
    for folder in target_dirs:
        target_path = Path.cwd() / folder
        source_path = base_path / folder

        if not target_path.exists():
            try:
                shutil.copytree(source_path, target_path)
            except Exception as e:
                tkinter.messagebox.showerror("Błąd", f"Nie udało się wypakować wymaganych folderów. {e}")

extract_files()

def loadFile():
    global videoFile
    videoFile = Path(filedialog.askopenfilename(title="Wybierz plik wideo"))
    filePath.config(text=videoFile.name)
    filePath.update_idletasks()

def convert():
    if not videoFile or videoFile == Path("."):
        tkinter.messagebox.showerror("Nie wybrano pliku", "Nie wybrano pliku wideo.")
        return 0
    progress.config(value=5)
    root.update_idletasks()
    txtFolder = Path.cwd() / "txt"
    audiosFolder = Path.cwd() / "audios"
    voskModelPath = Path.cwd() / "VoskModel" / "vosk-model-small-pl-0.22"
    txtFile = txtFolder / "text.txt"
    audioFile = audiosFolder / "audio.wav"

    txtFolder.mkdir(parents=True, exist_ok=True)
    audiosFolder.mkdir(parents=True, exist_ok=True)

    progress.config(value=20)
    root.update_idletasks()
    video = AudioSegment.from_file(str(videoFile), format="mp4")
    audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    progress.config(value=30)
    root.update_idletasks()
    audio.export(audioFile, format="wav")
    model = Model(str(voskModelPath))
    recognizer = KaldiRecognizer(model, 16000)

    progress.config(value=60)
    root.update_idletasks()

    try:
        txtFile.write_text("")  # Clearing the text file.
    except Exception as e:
        tkinter.messagebox.showerror("Błąd zapisu", f"Nie udało się wyczyścić pliku: {e}")
        sys.exit(3)

    transcribed_text = ""

    with wave.open(str(audioFile), "rb") as wf:
        while True:
            audio_chunk = wf.readframes(16000 * 300)

            if len(audio_chunk) == 0:
                break
            if recognizer.AcceptWaveform(audio_chunk):
                result = recognizer.Result()
                try:
                    result_dict = json.loads(result)
                    text = result_dict.get("text", " ")
                    transcribed_text += text
                except Exception as e:
                    tkinter.messagebox.showwarning("Błąd", "Nie udało się przekonwertować jednego z fragmentów.")

    txtFile.write_text(txtFile.read_text(encoding="utf-8") + transcribed_text, encoding="utf-8")
    progress.config(value=100)
    root.update_idletasks()
    tkinter.messagebox.showinfo("Sukces!", f"Sukces, zapisano tekst do {txtFile}")

    progress.config(value=0)
    root.update_idletasks()



ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    os.environ["FFMPEG_BINARY"] = ffmpeg_path
else:
    tkinter.messagebox.showerror("Błąd FFMPEG", "Nie znaleziono FFMPEG, program zostanie wyłączony.")
    sys.exit(1)

logo = tk.Label(root, text="Transcribbl", font=("Segoe UI", 14, 'bold'))
logo.grid(row=0, column=0, columnspan=2, pady=6)

AskFile = tk.Button(root, text="Wybierz plik", command=loadFile)
AskFile.grid(row=1, column=0, columnspan=2, pady=6)

filePath = tk.Label(root, text='Tu się wyświetli  nazwa twojego pliku', font=("Segoe UI", 10), wraplength=180)
filePath.grid(row=2, column=0, padx=25, pady=6, columnspan=2)

progress = ttk.Progressbar(root, orient="horizontal", length=150, mode="determinate")
progress.grid(row=3, column=0, padx=25, pady=6, columnspan=2)

ExecuteFunction = tk.Button(root, text="Uruchom", command=convert)
ExecuteFunction.grid(row=4, column=0, padx=10, pady=6, columnspan=2)

root.mainloop()