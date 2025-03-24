from openai import OpenAI

chatgpt_models = {
    'gpt3': 'gpt-3.5-turbo',
    'gpt4': 'gpt-4',
    'gpt4t': 'gpt-4-turbo',
    'gpt4o': 'gpt-4o',
    'gpt4om': 'gpt-4o-mini'
}

client = OpenAI()

def get_model(model: str):
    return chatgpt_models.get(model, 'gpt-4o-mini')


def ask_to_chatgpt(userinput, model='gpt4om', temperature=0, prompt="Eres un util asistente. Responderas de forma directa y sin explicaciones"):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": userinput}
    ]
    return _get_response_from_chatgpt(messages, model, temperature)


def transcribe_audio(audio_filename, transcription_model='gpt-4o-mini-transcribe', language='es'):
    with open(audio_filename, "rb") as audio_file:
        stream = client.audio.transcriptions.create(
            file=audio_file,
            model=transcription_model,
            language=language,
            stream=True
        )
        complete_response = ''
        for event in stream:
            if event.type == 'transcript.text.delta':
                delta = event.delta
                print(delta, end="", flush=True)
            elif event.type == 'transcript.text.done':
                complete_response = event.text
        return complete_response


def ask_simple_question_to_chatgpt(userinput, model='gpt4om', temperature=0):
    messages = [{"role": "user", "content": userinput}]
    return _get_response_from_chatgpt(messages, model, temperature)


def chat_with_chatgpt(messages, model='gpt4om', temperature=0):
    return _get_response_from_chatgpt(messages, model, temperature)


def _get_response_from_chatgpt(messages, model, temperature):
    complete_response = ''
    stream = client.chat.completions.create(
        model=get_model(model),
        messages=messages,
        temperature=temperature,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        answer = delta.content if delta.content is not None else ''
        print(answer, end="", flush=True)
        complete_response += answer
    print()
    return complete_response
