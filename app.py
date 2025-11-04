from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
import re
from calendar_client import parse_start
from scheduler import find_available_slots, create_meet_event

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

def schedule_meeting(email, name=None, preferred_time=None, duration_minutes=30, mode="offer_slots", time_zone="Asia/Kolkata", notes=""):
    if not EMAIL_RE.match(email or ""):
        return {"status": "error", "message": "Please share a valid email to send the invite."}

    if mode == "offer_slots":
        slots = find_available_slots(time_zone=time_zone, slot_minutes=duration_minutes, max_slots=6)
        return {
            "status": "ok",
            "mode": "offer_slots",
            "suggested_slots": slots,
            "message": "Here are a few open times. Which one works?"
        }

    # mode == auto_book
    start_dt = parse_start(preferred_time, time_zone)
    booking = create_meet_event(
        guest_email=email,
        guest_name=name,
        start_iso=start_dt.isoformat(),
        duration_minutes=duration_minutes,
        time_zone=time_zone,
        notes=notes,
    )
    return {"status": "ok", "mode": "auto_book", **booking}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

schedule_meeting_json = {
    "name": "schedule_meeting",
    "description": "Offer or book a meeting on Google Calendar and include a Google Meet link.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Guest email"},
            "name": {"type": "string", "description": "Guest name"},
            "preferred_time": {"type": "string", "description": "ISO8601 or natural text like 'Thu 3pm IST'"},
            "duration_minutes": {"type": "integer", "default": 30},
            "mode": {"type": "string", "enum": ["offer_slots", "auto_book"], "default": "offer_slots"},
            "time_zone": {"type": "string", "description": "IANA timezone", "default": "Asia/Kolkata"},
            "notes": {"type": "string", "description": "Description/agenda to include on the invite", "default": ""}
        },
        "required": ["email"]
    }
}



tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json},
        {"type": "function", "function": schedule_meeting_json}]


class Me:

    def __init__(self):
        openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai = OpenAI(api_key=openai_api_key)
        self.name = "Edgar Pinto"
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. If the user wants to talk \
   call schedule_meeting with mode='offer_slots' and show 4–6 options in Asia/Kolkata timezone. \
 If the user picks a time, call schedule_meeting with mode='auto_book' (confirm their email first) and return the Google Meet link and calendar link. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()