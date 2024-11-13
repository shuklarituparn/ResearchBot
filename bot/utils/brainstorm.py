from bot.utils.arXiv import ArxivAPIWrapper
from bot.utils import translate


async def generate_find_the_paper(user_query):
    arxiv = ArxivAPIWrapper(load_all_available_meta = True)
    docs = arxiv.run(user_query)
    translated_text = await translate.translate_text(docs)
    return translated_text
