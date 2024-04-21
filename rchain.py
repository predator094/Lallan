from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from utils import format_docs
from langchain_pinecone import PineconeVectorStore
from propmt import lallan_prompt


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"
)
docsearch = PineconeVectorStore(
    index_name="quickstart",
    embedding=embeddings,
    pinecone_api_key="fea6d7eb-1b48-4a28-afe5-df253dbe3e1d",
)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.0-pro", convert_system_message_to_human=False
)
retriever = docsearch.as_retriever()


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | lallan_prompt
    | llm
    | StrOutputParser()
)
