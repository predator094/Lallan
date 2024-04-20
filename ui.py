import streamlit as st
from chat import chat_engine
from utils import write_to_json
import os

st.set_page_config(
    page_title="Lallan Lucknow AI",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load chat engine
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = chat_engine

# Load previous messages and email
if "messages" not in st.session_state:
    st.session_state.messages = []
if "email" not in st.session_state:
    st.session_state.email = ""
if "inpu" not in st.session_state:
    st.session_state.inpu = False

# Form for email input
with st.form("my_form"):
    st.header("Enter you email")
    email = st.text_input("Email")
    submitted = st.form_submit_button("Submit")
    if submitted and email != "":
        write_to_json({"email": email}, "emails.json")
        st.session_state.email = email
        st.session_state.inpu = True

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input and assistant response
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
