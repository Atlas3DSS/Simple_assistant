Python OpenAI Voice Assistant
Introduction

This script is a Python-based voice assistant powered by OpenAI's GPT-4 model. It utilizes voice input to interact with the OpenAI API, processes the responses, and even converts text responses back into speech. It's designed to demonstrate a simple yet powerful implementation of voice-based interaction with OpenAI's language models.
Prerequisites

    Python 3.x
    Microphone access for voice recording
    Internet connection for OpenAI API access

Installation

    Clone the Repository
    git clone [repository-url]](https://github.com/Atlas3DSS/Simple_assistant.git
    cd Simple_assistant
Set up a Virtual Environment (Optional but Recommended)

    Create a virtual environment:
    python -m venv venv
Activate the virtual environment:

    On Windows:
    .\venv\Scripts\activate

On macOS and Linux:

    source venv/bin/activate

Install Dependencies

    pip install -r requirements.txt

Environment Variables

    Create a .env file in the root directory of the project.
    Add your OpenAI API key to the .env file:
    OPENAI_API_KEY=your_api_key_here

Usage

    Run the script:
    python simple_assistant.py

Features

    Voice input recording
    Interaction with OpenAI's GPT-4 model
    Text-to-speech response

Note

    Ensure that your OpenAI API key is kept confidential and not exposed in public repositories.
    This script is a demonstration and should be used responsibly considering OpenAI's usage policies.

License
script is free to use from mee inherets any tos from openai - you gotta pay for your own tokens. only works with latest gpt 3.5-turbo and gpt 4 models. 



