from libs.recorder import Recorder, merge_mp3
import click
from datetime import datetime
import os
import tempfile


def generate_part():
    temp_dir = tempfile.gettempdir()
    filename = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + "-part.mp3"
    return os.path.join(temp_dir, filename)


def valid_input(message, valid_options):
    while True:
        option = input(message)
        if option in valid_options:
            return option
        else:
            click.echo(click.style(f"Invalid option: {option}", fg="yellow"))


@click.command(help="Graba audio en formato MP3 con opciones de pausar y reanudar la grabación.")
@click.argument("record-name")
def record(record_name):
    filename = record_name + ".mp3"
    recording_parts = []
    pause_key = 'p'
    resume_key = 'r'
    stop_key = 's'

    def start_new_recording():
        filename_part = generate_part()
        recorder = Recorder(filename_part)
        recorder.start()
        return recorder, filename_part

    def stop_recording(recorder, filepart):
        recording_parts.append(filepart)
        recorder.stop()

    try:
        recorder, filename_part = start_new_recording()
        
        while True:
            signal = valid_input(click.style('Press "p" to Pause or "s" to Stop recording: ', fg="cyan"), [pause_key, stop_key])
            if signal == pause_key:
                stop_recording(recorder, filename_part)
                signal = valid_input(click.style('Recording paused. Press "r" to Resume or "s" to Stop: ',fg="yellow"), [resume_key, stop_key])
                if signal == resume_key:
                    recorder, filename_part = start_new_recording()
                    click.echo(click.style("Recording resumed.", fg="green"))
                elif signal == stop_key:
                    stop_recording(recorder, filename_part)
                    click.echo(click.style("Recording stopped.", fg="red"))
                    break
            elif signal == stop_key:
                stop_recording(recorder, filename_part)
                click.echo(click.style("Recording stopped.", fg="red"))
                break

    except KeyboardInterrupt:
        stop_recording(recorder, filename_part)
        click.echo(click.style("Recording stopped by CTRL+C.", fg="red"))
    
    # Merge mp3 parts
    merge_mp3(recording_parts, filename)
    click.echo(click.style(f"Recording file: {filename}", fg="green"))
