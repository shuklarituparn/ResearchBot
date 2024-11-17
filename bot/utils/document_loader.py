from langchain_community.document_loaders import PyPDFDirectoryLoader


async def load_data(filePath):
    document_loader = PyPDFDirectoryLoader(filePath)  # Initialize PDF loader with specified directory
    return document_loader.load()