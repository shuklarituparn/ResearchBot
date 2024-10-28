import os
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import ollama_formatter
from langchain_community.chat_models import GigaChat
from langchain.prompts import load_prompt
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_API_AUTH")


async def text_from_file(filename, update: Update, context: ContextTypes.DEFAULT_TYPE):
    giga = GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
    )
    map_prompt = load_prompt("./bot/utils/map.yaml")
    combine_prompt = load_prompt("./bot/utils/combine.yaml")
    chain = load_summarize_chain(
        giga,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
    )

    filepath = filename
    file_extention=str.split(filename, ".")[1]
    if file_extention == "pdf":
        loader = PyPDFLoader(filepath)
        documents = loader.load_and_split()
        summary = chain.invoke(
            {
                "input_documents": documents,
                "map_size": "одно предложение",
                "combine_size": "три предложения",
            }
        )

        summary_text = summary.get("output_text", " ")

        summary = (
                "Cудя по тексту, краткое описание выглядит следующим образом:" + summary_text
        )
        return summary
    return "err: мы обрабатываем только pdf-файлы, попробуйте отправить pdf-файлы"




