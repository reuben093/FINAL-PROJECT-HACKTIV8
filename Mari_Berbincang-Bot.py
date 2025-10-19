import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("💬 Mari Berbincang-Bot")

# =====================
# 🔑 Input API Key
# =====================
def get_api_key_input():
    """Minta user untuk masukkan Google API Key."""
    if "GOOGLE_API_KEY" not in st.session_state:
        st.session_state["GOOGLE_API_KEY"] = ""

    if st.session_state["GOOGLE_API_KEY"]:
        return

    st.write("Masukkan Google API Key kamu:")
    col1, col2 = st.columns((80, 20))
    with col1:
        api_key = st.text_input("", label_visibility="collapsed", type="password")
    with col2:
        if st.button("Submit"):
            st.session_state["GOOGLE_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
            st.rerun()

    if not st.session_state["GOOGLE_API_KEY"]:
        st.stop()


# =====================
# ⚙️ Load LLM
# =====================
def load_llm():
    """Dapatkan instance LLM."""
    if "llm" not in st.session_state:
        st.session_state["llm"] = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return st.session_state["llm"]


# =====================
# 💬 Chat History
# =====================
def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    return st.session_state["chat_history"]


# =====================
# 🎭 Pilih Gaya Chat
# =====================
def get_chat_mode():
    """Tentukan gaya bicara AI."""
    if "chat_mode" not in st.session_state:
        st.session_state["chat_mode"] = "Lucu"

    mode = st.radio(
        "🧠 Pilih gaya bicara chatbot:",
        ["Formal", "Santai", "Lucu"],
        horizontal=True,
        index=["Formal", "Santai", "Lucu"].index(st.session_state["chat_mode"])
    )
    st.session_state["chat_mode"] = mode

    # Tentukan system prompt sesuai mode
    if mode == "Formal":
        prompt = "Kamu adalah asisten yang sopan dan profesional, gunakan bahasa baku."
    elif mode == "Santai":
        prompt = "Kamu adalah asisten yang santai dan ramah seperti teman ngobrol."
    else:
        prompt = "Kamu adalah asisten lucu yang selalu menyelipkan candaan ringan."

    # Hanya update jika belum ada system prompt
    if not st.session_state.get("system_set", False):
        chat_history = get_chat_history()
        chat_history.insert(0, SystemMessage(content=prompt))
        st.session_state["system_set"] = True

    return mode


# =====================
# 💬 Display Chat
# =====================
def display_chat_message(message):
    if isinstance(message, HumanMessage):
        role = "User"
    elif isinstance(message, AIMessage):
        role = "AI"
    else:
        role = "Unknown"

    with st.chat_message(role):
        st.markdown(message.content)


def display_chat_history(chat_history):
    for chat in chat_history:
        if not isinstance(chat, SystemMessage):  # Jangan tampilkan system prompt
            display_chat_message(chat)


# =====================
# 🚀 Kirim Query
# =====================
def user_query_to_llm(llm, chat_history):
    prompt = st.chat_input("Ketik pesan kamu di sini...")
    if not prompt:
        st.stop()

    chat_history.append(HumanMessage(content=prompt))
    display_chat_message(chat_history[-1])

    response = llm.invoke(chat_history)
    chat_history.append(response)
    display_chat_message(chat_history[-1])


# =====================
# 🧹 Clear Chat
# =====================
def clear_chat():
    """Hapus semua percakapan."""
    if st.button("🧹 Hapus Riwayat Chat"):
        for key in ["chat_history", "system_set"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# =====================
# 🧩 Main Function
# =====================
def main():
    get_api_key_input()
    llm = load_llm()
    mode = get_chat_mode()
    chat_history = get_chat_history()

    st.markdown(f"**Mode aktif:** {mode}")
    clear_chat()  # Tombol hapus chat

    display_chat_history(chat_history)
    user_query_to_llm(llm, chat_history)


# Jalankan aplikasi
main()
