# 🧠 Persona Mimic — AI Chat Assistant

**Persona Mimic** is an interactive AI portfolio assistant built by Edgar Pinto.  
It answers questions about Edgar’s work, background, and experience — and can even schedule Google Meet calls automatically using the Google Calendar API.

---

## 🚀 Features

- 💬 Conversational AI interface (powered by **Gradio**)
- 🧠 Context-aware replies using your LinkedIn PDF + personal summary
- 📅 Google Calendar + Meet integration (auto-scheduling)
- 🔔 Optional push notifications via **Pushover**
- ⚙️ Easy to extend with new tools or APIs

---

## 🧩 Project Structure

## 🧩 Project Structure

```
persona_mimic/
│
├── app.py                 # main chat app with Gradio
├── calendar_client.py     # Google Calendar auth + time parsing
├── scheduler.py           # finds free slots and books meetings
├── me/
│   ├── summary.txt        # your short bio
│   └── linkedin.pdf       # LinkedIn export (not committed)
├── .env                   # environment variables (not committed)
├── requirements.txt       # dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Guide

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/persona_mimic.git
cd persona_mimic

2️⃣ Create a virtual environment

python -m venv .venv
.venv\Scripts\activate   # Windows
# or
source .venv/bin/activate   # macOS / Linux

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Add your environment variables

Create a file named .env in the project root:

OPENAI_API_KEY=sk-your-openai-key
PUSHOVER_TOKEN=your-pushover-token
PUSHOVER_USER=your-pushover-user

   

🔑 Google Calendar Setup

-Go to Google Cloud Console

-Enable Google Calendar API.

-Create an OAuth 2.0 Client ID → choose Desktop App/web app.

-Download the JSON and rename it credentials.json.

-Place it in the project root.

-Run once to generate a token:

    python gen_token_console.py

    Sign in and allow access — this creates token.json.

💬 Run the Chat App

python app.py

Then open the link shown in your terminal:
👉 http://127.0.0.1:7860

Use share=True inside app.py to generate a temporary public link:

    gr.ChatInterface(me.chat, type="messages").launch(share=True)

🧱 Tech Stack
Purpose	Tool
Chat UI	Gradio
LLM	OpenAI GPT-4o-mini
Calendar	Google Calendar API
Notifications	Pushover
Env config	python-dotenv
🧠 Example Conversation

    User: Can we schedule a quick call next week?
    Edgar: Sure! Here are some available time slots...
    (offers options)
    User: Thursday at 3 PM works.
    Edgar: Great — booked! Here’s your Google Meet link: <meet-link>

🧰 Development Notes

    Update me/summary.txt with your current background.

    Replace me/linkedin.pdf with your own LinkedIn export.

    Update self.name in app.py inside the Me class.

    Adjust the system_prompt() text to change personality or tone.

*Persona Mimic** is an interactive AI portfolio assistant built by me,  
inspired and mentored by Ed Donner (https://www.linkedin.com/in/eddonner/).
