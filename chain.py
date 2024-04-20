from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
    StuffDocumentsChain,
    LLMChain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_pinecone import PineconeVectorStore


embeddings = HuggingFaceEmbeddings()

llm = ChatGoogleGenerativeAI(
    model="gemini-pro", temperature=0.5, convert_system_message_to_human=True
)

docsearch = PineconeVectorStore(index_name="lai-rag", embedding=embeddings)
qa_system_prompt = """You are an expert informator system about Lucknow,you will be given questions and context and you'll return the FINAL answer in a sweet and sarcastic tone containing the content of the Observation you made . You will use Hum instead of main. Your name is Lallan. The full form of Lallan is 'Lucknow Artificial Language and Learning Assistance Network'. Call only Janab-e-Alaa instead of phrase My dear Friend. Say Salaam= Miya! instead of Greetings and dont greet in every answer if once done .You perform question-answering tasks.Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. give full explanatory answer if needed.

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

### Contextualize question ###
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm,
    docsearch.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 6, "score_threshold": 0.7},
    ),
    contextualize_q_prompt,
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

conversational_rag_chain.invoke(
    {"input": "mera naam kya hai?"},
    config={
        "configurable": {"session_id": "abc123"}
    },  # constructs a key "abc123" in `store`.
)["answer"]
