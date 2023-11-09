import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)
client = OpenAI()

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
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
        user_msg = input(Fore.YELLOW + "Enter your message to the assistant: " + Style.RESET_ALL)

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
        print(Fore.CYAN + "All messages in the thread:" + Style.RESET_ALL)
        for msg in messages.data:
            print(Fore.CYAN + str(msg) + Style.RESET_ALL)  # Print the whole message object

        # Assuming the first message in the list is the latest one, find the first message from the assistant
        assistant_msg = next((m for m in messages.data if m.role == 'assistant'), None)
        if assistant_msg:
            # Access the 'value' attribute of the 'text' attribute of the first content item, which is a MessageContentText object
            assistant_response = assistant_msg.content[0].text.value
            print(Fore.BLUE + "Assistant's response: " + assistant_response + Style.RESET_ALL)
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