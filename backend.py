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