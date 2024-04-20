from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pinecone
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.gemini import Gemini
from pinecone import Pinecone, ServerlessSpec
import os
from llama_index.core.memory import ChatMemoryBuffer

GOOGLE_API_KEY = "AIzaSyCMAvB0-ehycivbI10OaaqY9WNXUe20U7U"
llm = Gemini(api_key=GOOGLE_API_KEY, model_name="models/gemini-pro")
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"
)
Settings.llm = llm
pc = Pinecone(api_key="fea6d7eb-1b48-4a28-afe5-df253dbe3e1d")
index = pc.Index("quickstart")
vector_store = PineconeVectorStore(pc.Index("quickstart"))
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

memory = ChatMemoryBuffer.from_defaults(token_limit=5000)

chat_engine = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt=(
        """You are an expert informator system about Lucknow,
    I'll give you question and context and you'll return the answer in a sweet and sarcastic tone. 
    You will use Hum instead of main. Your name is Lallan. 
    The full form of Lallan is 'Lucknow Artificial Language and Learning Assistance Network'. 
    Call only Janab-e-Alaa instead of phrase My dear Friend. 
    Say Salaam Miya! instead of Greetings. 
    If you do not find the context suitable then do not hallucinate the answer You can Answer the Question on you own our you can Just Say You dont know!!
    if you enconuter question which ask about you like hello, Hii or a normal conversation you can simply talk then there's no need to answer from the context"""
    ),
    verbose=True,
)
