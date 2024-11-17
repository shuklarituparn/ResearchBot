from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate


async def query_rag(query_text, chromadb):
    PROMPT_TEMPLATE = """
    Ответьте на вопрос, основываясь только на следующем контексте:

    {context}

    ---

    Ответьте на вопрос, основываясь на приведенном выше контексте: {question}
    """
    embedding_function = OllamaEmbeddings()

    db = Chroma(persist_directory=chromadb, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    model = ChatOllama(model="llama3")
    response_text = model.predict(prompt)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return formatted_response, response_text
