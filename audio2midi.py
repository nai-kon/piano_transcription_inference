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

    DISP_IDENT_OUTDIR = "output: "

    def worker(files, output_dir):
        parser = argparse.ArgumentParser(description='')
        args = parser.parse_args()
        global pbar
        global pbtn
        global label
        for i, file in enumerate(files):
            pbar.set(0)
            label['text'] = f"{i+1}/{len(files)} processing...{os.path.basename(file)}"
            args.audio_path = file
            args.cuda = False
            savename = os.path.basename(args.audio_path).replace(".mp3", ".mid")
            args.output_midi_path = f"{output_dir}/{savename}"
            inference(args, pbar)
        pbtn["state"] = tk.NORMAL
        import subprocess
        subprocess.Popen(['explorer', os.path.abspath(output_dir)], shell=True)
        label['text'] = label['text'].replace("processing", "finished")

    def dirsel():
        global label_output_dir
        output_dir = filedialog.askdirectory(mustexist=True)
        if output_dir == "":
            return
        label_output_dir["text"] = DISP_IDENT_OUTDIR + output_dir

    def filesel():
        output_dir = label_output_dir["text"].lstrip(DISP_IDENT_OUTDIR)
        if output_dir == "":
            tk.messagebox.showwarning(title="output folder error", message="Please select output folder firstly")
            return

        files = filedialog.askopenfilenames(filetypes=[("mp3", "*.mp3")])
        if len(files) == 0:
            return
        print(files)
        global pbar
        pbar.set(0)
        global pbtn
        pbtn["state"] = tk.DISABLED
        global th
        th = threading.Thread(target=worker, args=(files, output_dir))
        th.start()

    baseGround = tk.Tk()
    baseGround.title("Audio to midi converter")
    baseGround.geometry('600x140')
    pbtn = tk.Button(baseGround, text="Select output folder", command=dirsel)
    pbtn.pack()
    label_output_dir = tk.Label(text=DISP_IDENT_OUTDIR)
    label_output_dir.pack()
    pbtn2 = tk.Button(baseGround, text="Select input mp3 files", command=filesel)
    pbtn2.pack()
    label = tk.Label(text="")
    label.pack()
    pbar = IntVar()
    ttk.Progressbar(baseGround, maximum=100, mode="determinate", length=550, variable=pbar).pack()

    baseGround.mainloop()
