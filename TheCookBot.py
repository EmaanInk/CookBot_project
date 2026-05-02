import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq()

st.set_page_config(page_title="CookBot", page_icon="🍳", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1a0a0f; }
    .stApp, .stApp p, .stApp span, .stApp div,
    .stApp label, .stMarkdown, .stMarkdown p { color: #c8f5d0 !important; }
    .stApp h1, .stApp h2, .stApp h3 { color: #e8005a !important; }
    .stApp .stCaption, .stApp small { color: #ff6bab !important; }
    .stChatMessage { background-color: #2b1020 !important; border-radius: 12px; }
    .stChatMessage p, .stChatMessage div, .stChatMessage span { color: #c8f5d0 !important; }
    .stChatInputContainer textarea {
        background-color: #3d1830 !important;
        color: #ffcce8 !important;
        border: 1px solid #e8005a !important;
    }
    section[data-testid="stSidebar"] { background-color: #2b1020 !important; }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div { color: #c8f5d0 !important; }
    section[data-testid="stSidebar"] input {
        background-color: #3d1830 !important;
        color: #ffcce8 !important;
        border: 1px solid #e8005a !important;
    }
    hr { border-color: #3d1830 !important; }
    .stButton > button {
        background-color: #e8005a !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton > button:hover { background-color: #ff2277 !important; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

def stream_cookbot(history):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You're a helpful cooking assistant. Only answer cooking related questions."},
            *history
        ],
        stream=True
    )

def stream_ingredients(ingredients, history):
    ingredient_prompt = f"""You are a smart cooking assistant.
The user has these ingredients: {ingredients}.
Do two things:
1. Suggest 3 meals they can make RIGHT NOW with what they have.
2. For each meal, list 1-2 ingredients they're missing — and give a common substitute they might already have at home.
Format your response with meal names as headers."""
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ingredient_prompt},
            *history,
            {"role": "user", "content": f"What can I make with: {ingredients}"}
        ],
        stream=True
    )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍳 CookBot")
    st.markdown("Your AI cooking assistant.")
    st.divider()

    st.markdown("### 🥚 Ingredient Checker")
    st.caption("Type ingredients you have, get meal ideas + substitutes.")
    ingredients = st.text_input("Your ingredients",
                                placeholder="eggs, pasta, butter...",
                                key="ing_input")

    if st.button("What can I make?"):
        if ingredients:
            user_msg = f"What can I make with: {ingredients}?"
            st.session_state.history.append({"role": "user", "content": user_msg})
            stream = stream_ingredients(ingredients, st.session_state.history)
            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
            st.session_state.history.append({"role": "assistant", "content": full_response})
            st.rerun()

    st.divider()

    # ── Download button — works on phone and desktop ───────────────────────────
    st.markdown("### 💾 Save Recipes")
    if st.session_state.history:
        output = "=== CookBot Recipe Session ===\n"
        output += f"Saved: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n"
        output += "=" * 30 + "\n\n"
        for msg in st.session_state.history:
            if msg["role"] == "user":
                output += f"YOU: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                output += f"COOKBOT: {msg['content']}\n\n"
                output += "-" * 30 + "\n\n"
        st.download_button(
            label="⬇️ Download recipes",
            data=output,
            file_name=f"cookbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    else:
        st.caption("Chat first, then save!")

    st.divider()

    if st.button("🗑️ Clear chat"):
        st.session_state.history = []
        st.rerun()

# ── Main chat area ─────────────────────────────────────────────────────────────
st.markdown("## 🍳 CookBot")
st.caption("Ask me anything about cooking, recipes, or techniques.")
st.divider()

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask CookBot anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.write_stream(
            chunk.choices[0].delta.content or ""
            for chunk in stream_cookbot(st.session_state.history)
        )

