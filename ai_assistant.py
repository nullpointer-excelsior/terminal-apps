
from libs.openai import ask_to_chatgpt


prompt="""
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""
cli = ask_to_chatgpt(prompt=prompt)
cli()