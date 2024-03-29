import streamlit as st
from utils import summarize_from_url, get_article_text, summarize_from_pdf, generate_answer

st.set_page_config(page_title="Qdoc", layout='wide')
st.title("📄 Qdoc (Article Assistant)")

st.sidebar.write('[My Portfolio](https://lancen.streamlit.app/)')
st.sidebar.caption("Made by [Lance Nguyen](https://www.linkedin.com/in/lancedin/)")

st.sidebar.info(
    """
    Info: Qdoc utilizes a large language model to summarize articles and PDFs from a given URL. It can also answer questions regarding the article using the history of the conversation, the article's content, and common knowledge.
    Start by entering an article URL to summarize.
    """
)

with st.sidebar.expander('**My Other Apps**'):
    st.caption('[LLM Optimization with RAG](https://lcrags.streamlit.app/)')
    st.caption('[SpotOn (Review Analysis)](https://spoton.streamlit.app/)')
    st.caption('[CooPA (Search Chatbot)](https://coopas.streamlit.app/)')

conversation_history = []

# Summary Section
user_input_url = st.text_input("Enter article URL to summarize:", key="url")
if user_input_url:
    if user_input_url.lower().endswith(".pdf"):
        st.session_state.summary = summarize_from_pdf(user_input_url)
    else:
        st.session_state.summary = summarize_from_url(user_input_url)

if st.button("Summarize"):
    if user_input_url:
        if user_input_url.lower().endswith(".pdf"):
            st.session_state.summary = summarize_from_pdf(user_input_url)
        else:
            st.session_state.summary = summarize_from_url(user_input_url)

if "summary" in st.session_state:
    st.write("Summary:")
    st.write(st.session_state.summary)

# Chatbot Section
st.header("🤖 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about the article."}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    conversation_history = [{"role": msg["role"], "message": msg["content"]} for msg in st.session_state.messages]
    article_text = get_article_text(user_input_url)

    if article_text is not None:

        # Generate an answer using the chat history, article text, and the user's question
        response = generate_answer(prompt, article_text[:16000], conversation_history)
        conversation_history.append({"role": "system", "message": response})

        # Display the system's answer
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
    else:
        st.warning("Please enter article URL first.")

if st.button("Refresh Conversation"):
    conversation_history = []
    st.session_state.messages = [{"role": "assistant", "content": "Ask me anything about the article."}]
    st.success("Conversation has been refreshed.")
