import streamlit as st
from agent import SmartAgent

st.set_page_config(page_title="Smart Home Assistant", page_icon="🏠", layout="centered")
smart_home=SmartAgent()
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"] {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Roboto', sans-serif;
    }
    .chat-box {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        height: 320px;
        overflow-y: auto;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.7);
        margin-bottom: 15px;
        border: 1px solid #333;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .message {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 15px;
        line-height: 1.4;
        word-wrap: break-word;
    }
    .user {
        background-color: #4caf50;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 0;
    }
    .assistant {
        background-color: #333333;
        color: white;
        align-self: flex-start;
        border-bottom-left-radius: 0;
    }
    .input-row {
        display: flex;
        gap: 10px;
    }
    .btn {
        background-color: #6200ee;
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    .btn:hover {
        background-color: #3700b3;
    }
    .btn-record {
        background-color: #bb86fc;
    }
    .btn-record:hover {
        background-color: #9a67ea;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏠 Smart Home")
st.markdown("Hello! I'm your Smart Home Assistant. How can I help you today?")

if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌ها با استایل
chat_html = '<div class="chat-box">'
for msg in st.session_state.messages:
    if msg.startswith("You:"):
        chat_html += f'<div class="message user">{msg[4:].strip()}</div>'
    else:
        chat_html += f'<div class="message assistant">{msg}</div>'
chat_html += "</div>"

st.markdown(chat_html, unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([6, 1, 1])
    user_input = cols[0].text_input("Type your message here...")
    record_btn = cols[1].form_submit_button("🎙️", help="Record voice")
    send_btn = cols[2].form_submit_button("Send")

    if record_btn:
        st.info("Voice recording feature is not enabled yet, coming soon!")

    if send_btn and user_input.strip():
        prompt = user_input.strip()
        st.session_state.messages.append(f"You: {prompt}")
        st.session_state.messages.append("Smart Home: ...typing")

    # در حلقه بعدی پیام ...typing رو حذف و پاسخ رو اضافه کن
    if st.session_state.messages and st.session_state.messages[-1] == "Smart Home: ...typing":
        prompt = st.session_state.messages[-2][4:].strip()  # پیام کاربر
        response = smart_home.agent_loop(prompt)
        st.session_state.messages[-1] = f"Smart Home: {response}"
