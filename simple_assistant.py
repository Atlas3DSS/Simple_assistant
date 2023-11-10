import openai
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
from colorama import init, Fore, Style
import subprocess
import sounddevice as sd
import numpy as np
import threading
import wavio
from pathlib import Path
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize Colorama
init(autoreset=True)
client = OpenAI()


# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

# Define the system message
system_msg = 'You are a helpful assistant who understands Python code and can retain information over multiple interactions.'

# Initialize the assistant outside the loop to avoid unnecessary creation each time
assistant = client.beta.assistants.create(
    name="Bob the Beer can",
    description=system_msg,
    model="gpt-4-1106-preview"
)

# Create a thread for the session
thread = client.beta.threads.create()

print(Fore.GREEN + "Assistant and Thread initialized" + Style.RESET_ALL)

# Loop to continuously interact with the assistant
try:
    while True:
        # User inputs the message they want to send
        #user_msg = input(Fore.YELLOW + "Enter your message to the assistant: " + Style.RESET_ALL)
        # Set the audio file path
        audio_file_path = Path(__file__).parent / "audio.wav"

        # Event to signal when the recording should stop
        stop_event = threading.Event()

        # Function to record audio until Enter is pressed
        def record_audio(stop_event):
            fs = 44100  # Sample rate
            # Initialize an empty list to store audio chunks
            recording = []
            
            with sd.InputStream(samplerate=fs, channels=2, callback=lambda indata, frames, time, status: recording.append(indata.copy())):
                print("Recording... Press Enter to start.")
                input("press enter to stop")  # Wait for Enter press
                stop_event.set()

            # Concatenate all the audio chunks
            audio_data = np.concatenate(recording, axis=0)
            wavio.write(str(audio_file_path), audio_data, fs, sampwidth=2)

            return audio_file_path

        # Function to wait for Enter press in a separate thread
        def wait_for_enter(stop_event):
            input()
            stop_event.set()

        # Start a thread that waits for Enter to be pressed
        threading.Thread(target=wait_for_enter, args=(stop_event,)).start()

        # Start recording
        path_to_audio = record_audio(stop_event)

        # Open the audio file in binary mode
        with open(path_to_audio, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        user_msg = transcript.text
        # Print the transcript
        print("Transcript:", transcript)

        # Append the message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_msg
        )

        print(Fore.BLUE + "Message appended, creating run..." + Style.RESET_ALL)

        # Create a run and assign it to the thread and assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=system_msg
        )

        print(Fore.YELLOW + "Run created, waiting for completion..." + Style.RESET_ALL)

        # Polling to wait for the run to be completed
        while True:
            current_run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            run_status = current_run.status
            if run_status not in ['in_progress', 'queued']:
                break
            time.sleep(2)  # Sleep for a short interval before checking again

        print(Fore.GREEN + "Run completed!" + Style.RESET_ALL)

        # List all messages in the thread to find the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Print the entire message list for sanity check
        #print(Fore.CYAN + "All messages in the thread:" + Style.RESET_ALL)
        #for msg in messages.data:
            #print(Fore.CYAN + str(msg) + Style.RESET_ALL)  # Print the whole message object

        # Assuming the first message in the list is the latest one, find the first message from the assistant
        assistant_msg = next((m for m in messages.data if m.role == 'assistant'), None)
        if assistant_msg:
            # Access the 'value' attribute of the 'text' attribute of the first content item, which is a MessageContentText object
            assistant_response = assistant_msg.content[0].text.value
            print(Fore.BLUE + "Assistant's response: " + assistant_response + Style.RESET_ALL)
            
            # Synthesize the assistant's response into speech
            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=assistant_msg.content[0].text.value
            )

            response.stream_to_file(speech_file_path)
            
            # Command to play the mp3 file using mpg123
            play_command = f"mpg123 {speech_file_path}"

            # Run the command
            subprocess.run(play_command, shell=True, check=True)
             

        else:
            print(Fore.RED + "No assistant messages found." + Style.RESET_ALL)

        # Check if user wants to continue
        if input(Fore.YELLOW + "Do you want to send another message? (yes/no): " + Style.RESET_ALL).lower() != 'yes':
            break

except KeyboardInterrupt:
    # Exit the loop if user interrupts with Ctrl+C
    print(Fore.RED + "\nUser interrupted the conversation." + Style.RESET_ALL)
except Exception as e:
    # Log any other exceptions
    print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
