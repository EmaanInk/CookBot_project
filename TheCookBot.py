import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq()

# ── Page config ────────────────────────────────────────────────────────────────
# This must be the very first Streamlit command — sets browser tab title and icon
st.set_page_config(page_title="CookBot", page_icon="🍳", layout="centered")

# ── Custom CSS ─────────────────────────────────────────────────────────────────
# Injects your color palette directly into the browser
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #1a0a0f; }

    /* Force all text to be visible */
    .stApp, .stApp p, .stApp span, .stApp div,
    .stApp label, .stMarkdown, .stMarkdown p { 
        color: #c8f5d0 !important; 
    }

    /* Title and headers */
    .stApp h1, .stApp h2, .stApp h3 { 
        color: #e8005a !important; 
    }

    /* Caption text */
    .stApp .stCaption, .stApp small { 
        color: #ff6bab !important; 
    }

    /* Chat message bubbles */
    .stChatMessage { 
        background-color: #2b1020 !important; 
        border-radius: 12px; 
    }

    /* Chat message text */
    .stChatMessage p, .stChatMessage div, .stChatMessage span { 
        color: #c8f5d0 !important; 
    }

    /* Input box at the bottom */
    .stChatInputContainer textarea {
        background-color: #3d1830 !important;
        color: #ffcce8 !important;
        border: 1px solid #e8005a !important;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] { 
        background-color: #2b1020 !important; 
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div { 
        color: #c8f5d0 !important; 
    }

    /* Sidebar input box */
    section[data-testid="stSidebar"] input {
        background-color: #3d1830 !important;
        color: #ffcce8 !important;
        border: 1px solid #e8005a !important;
    }

    /* Divider lines */
    hr { border-color: #3d1830 !important; }

    /* Buttons */
    .stButton > button {
        background-color: #e8005a !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton > button:hover { 
        background-color: #ff2277 !important; 
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
# st.session_state persists data across reruns — this is Streamlit's memory system
# Every time the user sends a message, Streamlit reruns the whole script top to bottom
# Without session_state, history would reset to [] on every rerun
if "history" not in st.session_state:
    st.session_state.history = []   # stores full conversation history

# ── AI functions ───────────────────────────────────────────────────────────────
def stream_cookbot(history):
    # stream=True is the key difference — returns a generator, not a complete response
    # the AI sends tokens one by one as it generates them
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You're a helpful cooking assistant. Only answer cooking related questions."},
            *history
        ],
        stream=True     # ← this is what makes it stream like ChatGPT
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
        stream=True     # streaming here too
    )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍳 CookBot")
    st.markdown("Your AI cooking assistant.")
    st.divider()

    # ── Ingredient checker in sidebar ──────────────────────────────────────────
    st.markdown("### 🥚 Ingredient Checker")
    st.caption("Type ingredients you have, get meal ideas + substitutes.")

    # text_input holds its value in session_state automatically via the key parameter
    ingredients = st.text_input("Your ingredients", 
                                placeholder="eggs, pasta, butter...",
                                key="ing_input")

    if st.button("What can I make?"):
        if ingredients:
            # Add user message to history and display it
            user_msg = f"What can I make with: {ingredients}?"
            st.session_state.history.append({"role": "user", "content": user_msg})

            # Get streaming response
            stream = stream_ingredients(ingredients, st.session_state.history)

            # Collect the full streamed response
            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta

            # Save to history
            st.session_state.history.append({"role": "assistant", "content": full_response})
            st.rerun()  # refreshes the page so the new messages appear in chat

    st.divider()

    # ── Save conversation ──────────────────────────────────────────────────────
    st.markdown("### 💾 Save Recipes")
    if st.button("Save this session"):
        if st.session_state.history:
            filename = f"cookbot_recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== CookBot Recipe Session ===\n")
                f.write(f"Saved: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")
                f.write("=" * 30 + "\n\n")
                for msg in st.session_state.history:
                    if msg["role"] == "user":
                        f.write(f"YOU: {msg['content']}\n\n")
                    elif msg["role"] == "assistant":
                        f.write(f"COOKBOT: {msg['content']}\n\n")
                        f.write("-" * 30 + "\n\n")
            st.success(f"Saved as {filename}")  # shows a green success message
        else:
            st.warning("Nothing to save yet!")

    st.divider()

    # ── Clear conversation ─────────────────────────────────────────────────────
    if st.button("🗑️ Clear chat"):
        st.session_state.history = []   # wipes history
        st.rerun()                      # refreshes page

# ── Main chat area ─────────────────────────────────────────────────────────────
st.markdown("## 🍳 CookBot")
st.caption("Ask me anything about cooking, recipes, or techniques.")
st.divider()

# Render all past messages from history
# Streamlit rerenders everything on each run, so we loop through history each time
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):  # "user" gets a person icon, "assistant" gets a bot icon
        st.markdown(msg["content"])

# ── Chat input at the bottom ───────────────────────────────────────────────────
# st.chat_input stays pinned to the bottom of the page automatically
if prompt := st.chat_input("Ask CookBot anything..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add to history
    st.session_state.history.append({"role": "user", "content": prompt})

    # Stream the bot response
    with st.chat_message("assistant"):
        # st.write_stream handles the streaming generator automatically
        # it displays each token as it arrives — this is the ChatGPT effect
        response = st.write_stream(
            chunk.choices[0].delta.content or ""
            for chunk in stream_cookbot(st.session_state.history)
        )

    # Save the complete response to history once streaming is done
    st.session_state.history.append({"role": "assistant", "content": response})