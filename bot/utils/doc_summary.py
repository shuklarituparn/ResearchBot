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
    print(update.effective_user.id)
    print(update.effective_user.first_name)
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
        print(documents[1])  # can send the document here to the ollama and ask it to summarize it and then send it in russian?4
        response_from_llm= await ollama_formatter.ollama_summarizer(documents[1])
        # summary = chain.invoke(
        #     {
        #         "input_documents": documents,
        #         "map_size": "одно предложение",
        #         "combine_size": "три предложения",
        #     }
        # )
        #
        # summary_text = summary.get("output_text", " ")
        #
        # summary = (
        #         "Cудя по тексту, краткое описание выглядит следующим образом: " + summary_text
        # )
        # new_summary=await ollama_formatter.escape_character(response_from_llm)
        # print(new_summary)
        return response_from_llm
    return "err: мы обрабатываем только pdf-файлы, попробуйте отправить pdf-файлы"




