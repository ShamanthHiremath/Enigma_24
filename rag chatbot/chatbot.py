# import library
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
load_dotenv()

st.title("RAG Based Agent For Stock Insights")
# Load and read the PDF file "linear.pdf" using PyPDFLoader.
loader = PyPDFLoader("KB.pdf")
data = loader.load()
# Split the loaded PDF data into smaller chunks using RecursiveCharacterTextSplitter.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)
# FAISS vector store from the split documents using embeddings from Google Generative AI.
vectorstore = FAISS.from_documents(documents=docs, embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
# Define a language model (LLM) using Google Generative AI model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0, max_tokens=None, timeout=None)

query = st.chat_input("Say something: ") 
prompt = query
# Define a system prompt that instructs the assistant on how to generate answers.
system_prompt = (
    "You are a question-answering assistant. Use the retrieved context to answer the user's question. "
    "If unsure, say you don't know. Keep your response concise, using up to three sentences."
    "\n\n"
    "{context}"
)
# Create a prompt template for the LLM, combining the system instructions and user input.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

if query:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": query})
    st.write(response["answer"])
