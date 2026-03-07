import streamlit as st
from pymongo import MongoClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME="vector_store_database"
COLLECTION_NAME="embeddings_stream"
ATLAS_VECTOR_SEARCH="vector_index"

def get_vector_store():
    client = MongoClient(MONGO_URI)
    collection = client[DB_NAME][COLLECTION_NAME]
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=ATLAS_VECTOR_SEARCH
    )
    return vector_store

