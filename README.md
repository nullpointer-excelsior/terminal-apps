# AI Terminal Tools

This repository contains a collection of command-line tools powered by AI, designed to enhance productivity and streamline various tasks.

## Available Terminal Applications

-   **`ai`**: A suite of AI-powered tools for text manipulation, code development, and chat interactions.
    -   `question`: Ask general questions to ChatGPT.
    -   `grammar`: Correct grammatical errors in text.
    -   `translate`: Translate text between English and Spanish.
    -   `dev`: An expert software developer assistant.
    -   `english`: An English language tutor.
    -   `summarize`: Summarize text with customizable parameters.
    -   `screenshot`: Capture screenshots and process them with AI.
    -   `commit-generator`: Generate semantic commit messages.
    -   `chat`: Interactive chat sessions with ChatGPT.
    -   `transcribe`: Transcribe audio files to text.
-   **`audio`**: Tools for recording and manipulating audio.
    -   `record`: Record audio in MP3 format with pause and resume options.
-   **`dev`**: Tools for development tasks.
    -   `summarize_sources`: Summarize source code files.
    -   `summarize_dir`: Summarize source code within a directory.
-   **`filesystem`**: Tools for files.
    -   `mdcat`: Show markdown files with pretty output.

## Installation

```shell
#!/bin/bash

#  install dependencies
pip install -r requirements.txt

# add to .bash_profile or .zshrc

# -- env requirements
export OPENAI_API_KEY="XXX"
export AI_PROMPT_RESOURCES="$HOME/Repositories/ai-prompt-resources"

# -- define alias 
alias ai='${REPOSITORY_DIR}/.venv/bin/python ${REPOSITORY_DIR}/terminal-apps/ai'
alias dev='${REPOSITORY_DIR}/.venv/bin/python ${REPOSITORY_DIR}/terminal-apps/dev'
alias audio='${REPOSITORY_DIR}/.venv/bin/python ${REPOSITORY_DIR}/terminal-apps/audio'
alias filesystem='${REPOSITORY_DIR}/.venv/bin/python ${REPOSITORY_DIR}/terminal-apps/filesystem'
```


## Parameter Explanations

### General Parameters (Applicable to `ai` commands)

-   **`--model`, `-m`**: Specifies the AI model to use (e.g., `gpt4om`).
-   **`--temperature`, `-t`**: Controls the randomness of the AI's output (0 to 2).
-   **`--copy`, `-c`**: Copies the AI's response to the clipboard.
-   **`userinput`**: Text input for the AI to process (can also be piped from stdin).

### `ai/chat.py` Parameters

-   **`--prompt`, `-p`**: Selects a prompt from predefined resources.

### `ai/screenshot.py` Parameters

-   **`--translate`, `-tr`**: Enables image translation.
-   **`--explain`, `-e`**: Enables image explanation.
-   **`--prompt`, `-p`**: Provides a custom text prompt for image processing.

### `ai/text.py` Parameters

-   **`--words`, `-w`**: Limits the summary to a specified number of words.
-   **`--sentences`, `-s`**: Limits the summary to a specified number of sentences.
-   **`--tone`, `-t`**: Sets the tone of the summary.
-   **`--audience`, `-a`**: Specifies the target audience for the summary.
-   **`--style`, `-st`**: Sets the style of the summary.
-   **`--markdown`, `-md`**: Formats the output as Markdown.
-   **`--translate`, `-tr`**: Translates the summary if necessary.
-   **`--transcription-model`, `-tm`**: Selects the transcription model.
-   **`--language`, `-l`**: Selects the language of the audio to transcribe.

### `dev/developer.py` Parameters

-   **`--session`, `-s`**: Creates or retrieves a session for the developer assistant.
-   **`userinput`**: Input text for the developer assistant to process.
-   **`--markdown`**: Formats the output as Markdown.

### `audio/recorder.py` Parameters

-   **`record-name`**: The base name for the recorded audio file.

### `dev/sumarize_source_code.py` Parameters

-   **`--output`, `-o`**: Specifies the output file for the summary in Markdown format.
-   **`src_files`**: List of source code files to summarize.
-   **`directory`**: Directory containing source code files to summarize.

### `filesystem/filesystem.py` Parameters

-   **`src_files`**: List of markdown files to show.