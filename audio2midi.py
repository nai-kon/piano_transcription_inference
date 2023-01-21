import os
import argparse
import torch
import time


from piano_transcription_inference import PianoTranscription, sample_rate, load_audio


def inference(args, pbar):
    """Inference template.

    Args:
      model_type: str
      audio_path: str
      cuda: bool
    """

    # Arugments & parameters
    audio_path = args.audio_path
    output_midi_path = args.output_midi_path
    device = 'cuda' if args.cuda and torch.cuda.is_available() else 'cpu'

    # Load audio
    (audio, _) = load_audio(audio_path, sr=sample_rate, mono=True)

    # Transcriptor
    transcriptor = PianoTranscription(device=device, checkpoint_path=None)
    """device: 'cuda' | 'cpu'
    checkpoint_path: None for default path, or str for downloaded checkpoint path.
    """

    # Transcribe and write out to MIDI file
    transcribe_time = time.time()
    transcribed_dict = transcriptor.transcribe(audio, output_midi_path, pbar)
    print('Transcribe time: {:.3f} s'.format(time.time() - transcribe_time))


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk, IntVar
    from tkinter import filedialog
    import threading

    label = None
    pbar = None
    args = None
    pbtn = None

    def worker():
        global args
        global pbar
        global pbtn
        inference(args, pbar)
        pbtn["state"] = tk.NORMAL
        import subprocess
        subprocess.Popen(['explorer', os.path.abspath("./output/")], shell=True)
        global label
        label['text'] = label['text'].replace("processing", "finished")

    def filesel():
        file = filedialog.askopenfilename(filetypes=[("mp3", "*.mp3")])
        if file is None or file == "":
            return
        print(file)
        global label
        label['text'] = f"processing...{os.path.basename(file)}"

        parser = argparse.ArgumentParser(description='')
        global args
        args = parser.parse_args()
        args.audio_path = file
        args.cuda = False
        savename = os.path.basename(args.audio_path).replace(".mp3", ".mid")
        args.output_midi_path = f"output/{savename}"
        global pbar
        pbar.set(0)
        global pbtn
        pbtn["state"] = tk.DISABLED
        global th
        th = threading.Thread(target=worker)
        th.start()

    baseGround = tk.Tk()
    baseGround.title("Audio to midi converter")
    baseGround.geometry('600x100')
    pbtn = tk.Button(baseGround, text="Select mp3 file", command=filesel)
    pbtn.pack()
    label = tk.Label(text="")
    label.pack()
    pbar = IntVar()
    ttk.Progressbar(baseGround, maximum=100, mode="determinate", length=550, variable=pbar).pack()
    baseGround.mainloop()