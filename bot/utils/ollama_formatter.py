import asyncio

# Ok what to do here, need to fix the formatting and the link
from ollama import AsyncClient

client = AsyncClient(host='http://localhost:11434/')

async def ollama_summarizer(input :str)->str:
    message={
        "role":"user",
        "content":f"Summarize this text and explain in russian language- {input}"
    }
    response=await AsyncClient().chat(model="llama3", messages=[message])
    content=response["message"]["content"]
    escape_char=await escape_character(content)
    return escape_char

async def escape_character(text:str)->str:
    reserved_characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in reserved_characters:
        text = text.replace(char, f"\\{char}")

    return text






