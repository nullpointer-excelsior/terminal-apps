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
    -   `transcribe`: Transcribe audio files to text.
-   **`audio`**: Tools for recording and manipulating audio.
    -   `record`: Record audio in MP3 format with pause and resume options.
-   **`filekit`**: Tools for files and source code exploration.
    -   `mdcat`: Show markdown files with pretty output.
    -   `mdcode-file`: Show markdown files.
    -   `mdcode-sources`: Summarize multiple source code files into a single markdown.
    -   `mdcode-directory`: Summarize all source code within a directory.
    -   `mdcode-select`: Interactive selection of files to summarize using fzf.

## Installation

```shell
# Clone the repository
git clone <repository-url>
cd terminal-apps

# Install scripts to ~/.scripts
./install.sh

# -- env requirements
export OPENAI_API_KEY="XXX"
export AI_PROMPT_RESOURCES="$HOME/Repositories/ai-prompt-resources"

# -- Usage with uv
uv run python -m ai --help
uv run python -m filekit --help
uv run python -m audio --help
```


## Parameter Explanations

### General Parameters (Applicable to `ai` commands)

-   **`--model`, `-m`**: Specifies the AI model to use (e.g., `gpt4om`, `gemini`, `o1`).
-   **`--plain`**: Plain text output.
-   **`--json`**: JSON output.
-   **`--verbose`**: Verbose output (diagnostics on stderr).
-   **`userinput`**: Text input for the AI to process (can also be piped from stdin).

### `ai screenshot` Parameters

-   **`--translate`, `-tr`**: Enables image translation.
-   **`--explain`, `-e`**: Enables image explanation.
-   **`--prompt`, `-p`**: Provides a custom text prompt for image processing.
-   **`--copy`, `-c`**: Copies the response to the clipboard.

### `ai summarize` Parameters

-   **`--words`, `-w`**: Limits the summary to a specified number of words.
-   **`--sentences`, `-s`**: Limits the summary to a specified number of sentences.
-   **`--tone`, `-t`**: Sets the tone of the summary.
-   **`--audience`, `-a`**: Specifies the target audience for the summary.
-   **`--style`, `-st`**: Sets the style of the summary.
-   **`--markdown`, `-md`**: Formats the output as Markdown.
-   **`--translate`, `-tr`**: Translates the summary if necessary.

### `ai transcribe` Parameters

-   **`--copy`, `-c`**: Copies the response to the clipboard.
-   **`--language`, `-l`**: Selects the language of the audio (e.g., "en", "es").

### `ai dev` Parameters

-   **`--markdown`, `-md`**: Formats the output as Markdown.
-   **`--file`, `-f`**: Attaches a file as context for the developer assistant.

### `audio record` Parameters

-   **`record-name`**: The base name for the recorded audio file.

### `filekit mdcode-*` Parameters

-   **`src_files`**: List of source code files to summarize (for `mdcode-sources`).
-   **`directory`**: Directory containing source code files to summarize (for `mdcode-directory`).