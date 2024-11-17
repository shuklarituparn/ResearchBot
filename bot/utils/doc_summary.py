import os
import subprocess
from telegram import Update
from telegram.ext import ContextTypes


from bot.utils import ollama_formatter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from dotenv import load_dotenv

load_dotenv()
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_API_AUTH")


async def text_from_file(filename, update: Update, context: ContextTypes.DEFAULT_TYPE):
    filepath = filename
    file_extention=str.split(filename, ".")[1]
    if file_extention == "pdf":
        loader = PyPDFLoader(filepath)
        documents = loader.load_and_split()
        response_from_llm= await ollama_formatter.ollama_summarizer(documents[1])
        return response_from_llm
    elif file_extention=="doc":
        if not os.path.isfile(filepath):
            return "файл с такими именем не существует"
        else:
            file_name_without_extension = str.split(filepath, ".")[0]
            command = ['libreoffice', '--headless', '--convert-to', 'docx', filepath]
            try:
                subprocess.run(command, check=True)
                converted_file=file_name_without_extension+".docx"
                loader = Docx2txtLoader(converted_file)
                documents = loader.load_and_split()
                response_from_llm = await ollama_formatter.ollama_summarizer(documents[1])
                return response_from_llm
            except subprocess.CalledProcessError as e:
                print(f"An error occurred: {e.stderr.decode()}")
                return "Произошла ошибка при конвертации файла"


    elif file_extention=="docx":
        loader = Docx2txtLoader(filepath)
        documents = loader.load_and_split()
        response_from_llm = await ollama_formatter.ollama_summarizer(documents[1])
        return response_from_llm
    return "err: что-то пошло не так "




# SO IDEALLY NOW THE SUMMARY SHOULD WORK FOR BOTH DOC AND DOCX