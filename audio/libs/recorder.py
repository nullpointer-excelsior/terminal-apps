import sounddevice as sd
import soundfile as sf
from dataclasses import dataclass, field
from queue import Queue
import sys
from threading import Thread
import numpy as np


@dataclass
class Recorder:
    filename: str
    is_recording: bool = field(default=False, init=False)
    thread: Thread = field(default=None, init=False)
    q: Queue = field(default_factory=Queue, init=False)

    def _callback(self, indata, frames, time, status):
        """Handles incoming audio data."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def start(self):
        """Starts recording in a separate thread."""
        if self.is_recording == False:
            self.is_recording = True
            self.thread = Thread(target=self._record, daemon=True)
            self.thread.start()

    def _record(self):
        """Handles the recording process."""
        samplerate = 44100
        channels = 1
        try:
            with sf.SoundFile(self.filename, mode="x", samplerate=samplerate, channels=channels) as file:
                with sd.InputStream(samplerate=samplerate, channels=channels, callback=self._callback):
                    while self.is_recording:
                        file.write(self.q.get())
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

    def stop(self):
        """Stops the recording."""
        self.is_recording = False
        if self.thread:
            self.thread.join()
        return self.filename



def merge_mp3(files, output_file):
    """
    Merges multiple MP3 files into a single MP3 file.

    :param files: List of MP3 file paths to merge.
    :param output_file: Output MP3 file path.
    """
    combined_audio = []
    sample_rate = None

    for file in files:
        data, samplerate = sf.read(file)

        # Ensure all files have the same sample rate
        if sample_rate is None:
            sample_rate = samplerate
        elif sample_rate != samplerate:
            raise ValueError(f"Sample rate mismatch in file: {file}")

        combined_audio.append(data)

    # Concatenate all audio data
    merged_data = np.concatenate(combined_audio)

    # Save the merged audio file
    sf.write(output_file, merged_data, sample_rate)

