import click
import sys, select, os
import pyperclip
from openai import OpenAI
from enum import Enum


class ChatGPTModel(Enum):
    GPT_3_5_TURBO = 'gpt-3.5-turbo'
    GPT_4 = 'gpt-4'
    GPT_4o = 'gpt-4o'
    GPT_4oM = 'gpt-4o-mini'
    GPT_4_TURBO = 'gpt-4-turbo'

MODEL_MAPPER = {
    'gpt3': ChatGPTModel.GPT_3_5_TURBO,
    'gpt4': ChatGPTModel.GPT_4,
    'gpt4t': ChatGPTModel.GPT_4_TURBO,
    'gpt4o': ChatGPTModel.GPT_4o,
    'gpt4om': ChatGPTModel.GPT_4oM
}

def get_model(model: str):
    return MODEL_MAPPER[model]


client = OpenAI()


def ask_to_chatgpt_stream(messages, model=ChatGPTModel.GPT_4oM, temperature=0):
    stream = client.chat.completions.create(
        model=model.value,
        messages=messages,
        temperature=temperature,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        answer = delta.content if delta.content is not None else ''
        yield answer


def get_completion_stream(prompt, model=ChatGPTModel.GPT_4oM, temperature=0):
    messages = [{"role": "user", "content": prompt}]
    return ask_to_chatgpt_stream(messages=messages, model=model, temperature=temperature)


def model_option(model=ChatGPTModel.GPT_4oM):
    model_choices= list(MODEL_MAPPER.keys())
    def decorator(wrapped_function):
        return click.option(
            '--model', '-m',
            type=click.Choice(model_choices, case_sensitive=False),
            default=model,
            help='Indica el modelo AI a usar'
        )(wrapped_function)

    return decorator


def temperature_option(temperature=0):
    def decorator(wrapped_function):
        return click.option(
            '--temperature', '-t',
            type=float, 
            help='Temperatura del modelo. Entre 0 y 2. Los valores más altos como 0.8 harán que la salida sea más aleatoria, mientras que los valores más bajos como 0.2 la harán más enfocada y determinista.', 
            default=temperature
        )(wrapped_function)
    return decorator


def read_file_or_get_content(value):
    if os.path.exists(value):
        with open(value, 'r') as file:
            return file.read()
    return value


def read_stdin():
    if select.select([sys.stdin,],[],[],0.0)[0]:
        return sys.stdin.read().strip()
    return None


def print_stream(value):
    sys.stdout.write(value)
    sys.stdout.flush()


def ask_to_chatgpt(model='gpt4om', prompt="Eres un util asistente. Responderas de forma directa y sin explicaciones", help="Pregunta rápida y configurable a ChatGPT"):
    @click.command(help=help)
    @click.argument('argument', default=None, required=False)
    @model_option(model)
    @temperature_option()
    def cli(argument, model, temperature):
        content = argument if argument is not None else read_stdin()
        content = read_file_or_get_content(content)
        complete_response = ''
        messages = [
            {"role": "assistant", "content": prompt},
            {"role": "user", "content": content}
        ]
        for stream in ask_to_chatgpt_stream(messages=messages, model=get_model(model), temperature=temperature):
            print_stream(stream)
            complete_response += stream
        print()
        pyperclip.copy(complete_response)
        return complete_response
    return cli