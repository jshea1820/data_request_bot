from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import pickle

class DocumentVectorStoreGenerator:

    def __init__(self):
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vector_store = InMemoryVectorStore(embeddings)
    
    def load_documents(self, document_path):

        loader = JSONLoader(
            file_path=document_path,
            jq_schema=".",
            text_content=False
        )
        self.docs = loader.load()

    def create_vector_store(self):

        self.vector_store.add_documents(documents=self.docs)

