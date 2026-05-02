import tkinter as tk 
import time
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime



from dotenv import load_dotenv

load_dotenv()
client = Groq()  # automatically reads GROQ_API_KEY from .env
history = []                # stores the full conversation as a list of messages

# ── Color palette ─────────────────────────────────────────────────────────────
# Defined once here so you can change the whole app's look in one place
BG_MAIN     = "#1a0a0f"    # main window background — near-black wine tint
BG_CHAT     = "#2b1020"    # chat area background — deep plum
BG_INPUT    = "#3d1830"    # input box background — slightly lighter plum
ACCENT_HOT  = "#e8005a"    # primary accent — hot pink for buttons and title
ACCENT_SOFT = "#ff6bab"    # softer pink used for the input cursor
TEXT_USER   = "#ffcce8"    # color of the user's messages
TEXT_BOT    = "#c8f5d0"    # color of CookBot's messages — mint green
TEXT_LABEL  = "#ff8fcb"    # color for labels
FG_WHITE    = "#ffffff"    # plain white for button text

# ── Font palette ───────────────────────────────────────────────────────────────
FONT_TITLE  = ("Georgia", 17, "bold")   # app title font
FONT_CHAT   = ("Consolas", 10)          # monospace font for chat messages
FONT_INPUT  = ("Consolas", 11)          # font for the text input box
FONT_BTN    = ("Georgia", 11, "bold")   # font for buttons

# ── Ingredient checker AI call ─────────────────────────────────────────────────
def ask_ingredients(ingredients, history):
    # builds a specific system prompt focused on ingredient-based suggestions
    ingredient_prompt = f"""You are a smart cooking assistant. 
    the user has these ingredients: {ingredients}.
    Do two things:
1. Suggest 3 meals they can make RIGHT NOW with what they have.
2. For each meal, list 1-2 ingredients they're missing — and give a common substitute they might already have at home.
Format your response quickly with meal names as headers."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",    # the AI model being used
        messages=[
            {"role": "system", "content": ingredient_prompt},  # gives the AI its instructions
            *history,                                           # includes past conversation
            {"role": "user", "content": f"What can I make with: {ingredients}"}  # the actual question
        ]
    )
    return response.choices[0].message.content   # extracts just the text reply

# ── General cooking AI call ────────────────────────────────────────────────────
def ask_cookbot(history):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",    # same model
        messages=[
            {"role": "system", "content": "You're a helpful cooking assistant. Only answer cooking related questions."},
            *history    # sends the full conversation so it remembers context
        ]
    )
    return response.choices[0].message.content   # extracts just the text reply

# ── Handles the SEND button ────────────────────────────────────────────────────
def send_message():
    question = input_box.get()      # reads whatever the user typed
    if question == "":              # does nothing if the box is empty
        return

    chat_area.config(state="normal")                                    # unlocks chat to write
    chat_area.insert(tk.END, "You: " + question + "\n\n", "user")      # shows user message
    chat_area.insert(tk.END, "-" * 50 + "\n", "divider")               # divider line

    history.append({"role": "user", "content": question})  # adds user message to memory

    answer = ask_cookbot(history)   # sends full history to AI, gets reply

    history.append({"role": "assistant", "content": answer})  # adds AI reply to memory

    chat_area.insert(tk.END, "CookBot: ", "bot")    # prints the "CookBot:" label
    animate_typing(answer, "bot")                   # types the answer letter by letter
    chat_area.insert(tk.END, "-" * 50 + "\n\n", "divider")  # divider after reply

    chat_area.config(state="disabled")  # locks chat again so user can't edit it
    chat_area.see(tk.END)               # scrolls to the bottom automatically
    input_box.delete(0, tk.END)         # clears the input box after sending

# ── Saves the conversation to a .txt file ─────────────────────────────────────
def save_chat():
    if not history:     # does nothing if no messages have been sent yet
        return

    from datetime import datetime
    # creates a unique filename using the current date and time
    filename = f"cookbot_recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:   # opens/creates the file
        f.write("=== CookBot Recipe Session ===\n")
        f.write(f"Saved: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")
        f.write("=" * 30 + "\n\n")

        for msg in history:     # loops through every message in history
            if msg["role"] == "user":
                f.write(f"YOU: {msg['content']}\n\n")          # writes user messages
            elif msg["role"] == "assistant":
                f.write(f"COOKBOT: {msg['content']}\n\n")      # writes bot messages
                f.write("-" * 30 + "\n\n")                     # separator between exchanges

    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"✅ Saved as {filename}\n\n", "divider")  # confirms save in chat
    chat_area.config(state="disabled")

# ── Typing animation ───────────────────────────────────────────────────────────
def animate_typing(text, tag):
    chat_area.config(state="normal")        # unlocks chat to write
    for char in text:                       # loops through every character in the reply
        chat_area.insert(tk.END, char, tag) # inserts one character at a time
        chat_area.update()                  # forces the window to redraw so you see it appear
        time.sleep(0.0012)                  # tiny pause between each character — controls speed
    chat_area.insert(tk.END, "\n\n")        # adds space after the full message
    chat_area.config(state="disabled")      # locks chat again
    chat_area.see(tk.END)                   # scrolls to bottom

# ── Build the window ───────────────────────────────────────────────────────────
window = tk.Tk()                        # creates the main application window
window.title("CookBot")                 # sets the window title bar text
window.geometry("500x600")              # sets width x height in pixels
window.config(bg=BG_MAIN)              # applies background color

# Title label at the top
label = tk.Label(window, text="🍳 CookBot",
                 font=FONT_TITLE, bg=BG_MAIN, fg=ACCENT_HOT)
label.pack(pady=10)                     # adds it to the window with vertical padding

# Main chat display area
chat_area = tk.Text(window, height=28, width=62,
                    state="disabled",           # starts locked — user can't type here
                    bg=BG_CHAT, fg=TEXT_BOT,
                    font=FONT_CHAT,
                    relief="flat", borderwidth=0,
                    insertbackground=ACCENT_HOT)
chat_area.pack(pady=10)

# Text color/style rules for different message types
chat_area.tag_config("user", foreground=TEXT_USER, font=("Consolas", 10, "bold"))
chat_area.tag_config("bot", foreground=TEXT_BOT, font=FONT_CHAT)
chat_area.tag_config("divider", foreground="#553344")   # muted color for separator lines

# Input box where the user types their message
input_box = tk.Entry(window, width=38, bg=BG_INPUT,
                     fg=TEXT_USER, font=FONT_INPUT,
                     insertbackground=ACCENT_SOFT,      # cursor color inside the box
                     relief="flat")
input_box.pack(pady=5)

# Send button — triggers send_message() when clicked
send_button = tk.Button(window, text="SEND  ➤",
                        bg=ACCENT_HOT, fg=FG_WHITE,
                        font=FONT_BTN, relief="flat",
                        activebackground="#ff2277",      # color when you click it
                        cursor="hand2",                  # shows hand cursor on hover
                        command=send_message)
send_button.pack(pady=5)

# Save button — triggers save_chat() when clicked
save_button = tk.Button(window, text="💾 Save Recipes",
                        bg=BG_INPUT, fg=TEXT_LABEL,
                        font=FONT_BTN, relief="flat",
                        cursor="hand2",
                        command=save_chat)               # fixed: was pointing to send_message before
save_button.pack(pady=3)

# ── Ingredient checker section ─────────────────────────────────────────────────
ing_frame = tk.Frame(window, bg=BG_MAIN)    # container frame for the ingredient row
ing_frame.pack(pady=3)

ing_label = tk.Label(ing_frame, text="🥚 Got ingredients?",
                     font=FONT_BTN, bg=BG_MAIN, fg=TEXT_LABEL)
ing_label.pack(side=tk.LEFT, padx=5)       # places label on the left side of the frame

ing_box = tk.Entry(ing_frame, width=25, bg=BG_INPUT,
                   fg=TEXT_USER, font=FONT_INPUT,
                   insertbackground=ACCENT_SOFT,
                   relief="flat")
ing_box.pack(side=tk.LEFT, padx=5)         # places input box next to the label

# ── Handles the ingredient Check button ───────────────────────────────────────
def check_ingredients():
    ingredients = ing_box.get()     # reads the ingredient list the user typed
    if ingredients == "":           # does nothing if empty
        return

    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"You: What can I make with {ingredients}?\n\n", "user")
    chat_area.insert(tk.END, "-" * 50 + "\n", "divider")
    chat_area.config(state="disabled")

    answer = ask_ingredients(ingredients, history)  # calls the ingredient-specific AI function

    history.append({"role": "user", "content": f"What can I make with: {ingredients}"})
    history.append({"role": "assistant", "content": answer})

    chat_area.config(state="normal")
    chat_area.insert(tk.END, "CookBot: ", "bot")
    animate_typing(answer, "bot")                   # types response letter by letter
    chat_area.insert(tk.END, "-" * 50 + "\n\n", "divider")
    chat_area.config(state="disabled")
    ing_box.delete(0, tk.END)       # clears ingredient input box after checking

# Check button — triggers check_ingredients() when clicked
ing_btn = tk.Button(ing_frame, text="Check!",
                    bg=ACCENT_HOT, fg=FG_WHITE,
                    font=FONT_BTN, relief="flat",
                    cursor="hand2",
                    command=check_ingredients)
ing_btn.pack(side=tk.LEFT, padx=5)

window.mainloop()   # starts the app — everything runs inside this loop until window closes
