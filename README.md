🍳 CookBot
An AI-powered cooking assistant built with Groq's LLaMA model and Streamlit. Ask it anything about cooking, get real-time streaming responses, and find out what meals you can make with whatever's in your fridge.

Features

AI chat — conversational cooking assistant that only answers cooking-related questions
Ingredient checker — type what you have, get 3 meal suggestions plus substitutes for anything you're missing
Real-time streaming — responses appear word by word as the AI generates them, like ChatGPT
Save session — export your full conversation as a .txt recipe file
Custom dark UI — deep plum and hot pink theme built with custom CSS


Demo

Ask: "How do I make pasta carbonara without cream?"
Ingredient check: "eggs, pasta, butter" → get 3 meals + substitutes instantly


Tech Stack
ToolPurposeGroq APILLaMA 3.3 70B model for AI responsesStreamlitWeb UI and deploymentPython 3.13Core languagepython-dotenvSecure API key management

Getting Started
1. Clone the repo
bashgit clone https://github.com/EmaanInk/CookBot_project.git
cd cookbot
2. Install dependencies
bashpip install -r requirements.txt
3. Set up your API key
Create a .env file in the project root:
GROQ_API_KEY=your_groq_api_key_here
Get a free API key at console.groq.com.
4. Run the app
bashstreamlit run TheCookBot.py
The app opens automatically at http://localhost:8501.

Project Structure
cookbot/
├── TheCookBot.py      # Main Streamlit app
├── .env               # Your API key (never commit this)
├── .gitignore         # Keeps .env out of GitHub
├── requirements.txt   # Dependencies
└── README.md

Requirements
groq
streamlit
python-dotenv

How It Works
CookBot sends your full conversation history to the Groq API on every message. This is what gives it memory — it's not magic, it's just the entire chat being sent each time. The ingredient checker uses a separate system prompt that instructs the model to focus specifically on meal suggestions and substitutions.
Streaming works by setting stream=True in the API call, which returns tokens one by one instead of waiting for the full response. Streamlit's st.write_stream() handles displaying them as they arrive.

Author
Built by Emaan Khan — 4th semester CS student exploring AI engineering.

License
MIT License — free to use, modify, and share.
