import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from chat import chat_engine
import json
import os

st.set_page_config(
    page_title="Lallan Lucknow AI",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# json upload
def write_to_json(data, filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            existing_data = json.load(file)
        # Check if the email already exists in the file
        if "email" in data:
            existing_emails = [
                entry["email"] for entry in existing_data if "email" in entry
            ]
            if data["email"] in existing_emails:
                return
        existing_data.append(data)
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(filename, "w") as file:
            json.dump([data], file, indent=4)


# session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = HuggingFaceEmbeddings()
if "doc" not in st.session_state:
    st.session_state.doc = PineconeVectorStore(
        index_name="lai-rag",
        embedding=st.session_state.embeddings,
        pinecone_api_key=st.secrets["PINECONE_API_KEY"],
    )
if "inpu" not in st.session_state:
    st.session_state.inpu = False

if "email" not in st.session_state:
    st.session_state.email = ""
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = chat_engine


# form
with st.form("my_form"):
    st.header("Enter you email")
    email = st.text_input("Email")
    submitted = st.form_submit_button("Submit")
    if submitted and email != "":
        write_to_json({"email": email}, "emails.json")
        st.session_state.email = email
        st.session_state.inpu = True


#####
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input(
    "Farmaiye Janaab", disabled=False if st.session_state.inpu == True else True
):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        a = st.session_state.rag_chain.chat(prompt).response
        st.markdown(a)
    email_filename = os.path.join(
        "queries", f"{st.session_state.email.split('@')[0]}.json"
    )
    queries_folder = "queries"
    if not os.path.exists(queries_folder):
        os.makedirs(queries_folder)
    write_to_json(
        {"prompt": prompt, "answer": a},
        email_filename,
    )
    st.session_state.messages.append({"role": "assistant", "content": a})
