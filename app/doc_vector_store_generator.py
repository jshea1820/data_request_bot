from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import pickle

class DocumentVectorStoreGenerator:

    def __init__(self):
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vector_store = InMemoryVectorStore(embeddings)
    
    def load_documents(self, document_path):

        loader = UnstructuredMarkdownLoader(document_path)
        self.docs = loader.load()

    def create_vector_store(self):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            add_start_index=True,
        )

        splits = text_splitter.split_documents(self.docs)
        self.vector_store.add_documents(documents=splits)

