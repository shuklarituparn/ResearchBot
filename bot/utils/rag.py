from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_community.embeddings import OllamaEmbeddings, GigaChatEmbeddings
from langchain_community.llms.gigachat import GigaChat
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from bot.utils import askai

from bot.utils.audio_summarizer import GIGACHAD_CREDENTIALS


async def query_rag(query_text, chromadb):
    PROMPT_TEMPLATE = """
    Ответьте на вопрос, основываясь только на следующем контексте:

    {context}

    ---

    Ответьте на вопрос, основываясь на приведенном выше контексте: {question}
    """
    embedding_function = GigaChatEmbeddings(
        credentials=GIGACHAD_CREDENTIALS,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
    )
    print("Entered the rag function")
    db = Chroma(persist_directory=chromadb, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query_text, k=4)
    if results is None:
        response=askai.ask_ai(query_text)
        return "", response
    else:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        model = GigaChat(
            credentials=GIGACHAD_CREDENTIALS,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        )
        response_text = model.invoke(prompt)
        print(f"response text is: {response_text}")
        sources = [doc.metadata.get("source", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        return formatted_response, response_text
