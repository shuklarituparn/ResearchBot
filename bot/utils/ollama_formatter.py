import asyncio

from ollama import AsyncClient

client = AsyncClient(host='http://localhost:11434/')

async def file_formatter(input :str)->str:
    message={
        "role":"user",
        "content":f"Format this text, to be able to displayed on the telegram app better, use markdown and character escape- {input}"
    }
    response=await AsyncClient().chat(model="llama3", messages=[message])
    content=response["message"]["content"]
    escape_char=await escape_character(content)
    return escape_char

async def escape_character(text:str)->str:
    reserved_characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in reserved_characters:
        text = text.replace(char, f'\\{char}')
    return text






