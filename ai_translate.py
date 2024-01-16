from libs.openai import ask_to_chatgpt
import pyperclip

prompt="""
Actua como un experto profesor en ingles y corrige lo que el usuario te de como entrada. 
[INSTRUCCIONES]:
- si el texto esta en español deberas traducir el texto.
- si el texto esta en ingles debes dar un feedback sobre su gramatica. Devolveras un resumen con los errores y sugerencias en formato markdown. 
finalmente devolveras el texto de entrada traducido o corregido en ingles encerrado en triple acento grave.
"""
cli = ask_to_chatgpt(prompt=prompt)
text = cli()
try:
    text_to_copy = text.split('```')[1]
    pyperclip.copy(text_to_copy)
    print('Texto copiado al portapapeles.')
except:
    print('\nTexto no pudo ser copiado al portapapeles.')