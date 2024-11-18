from ollama import AsyncClient

client = AsyncClient(host='http://localhost:11434/')

async def ask_ai(input :str)->str:
    message={
        "role":"user",
        "content":f"Обьясни - {input}"
    }
    response=await AsyncClient().chat(model="llama3", messages=[message])
    content=response["message"]["content"]
    return content

