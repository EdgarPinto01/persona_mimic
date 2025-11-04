# calendar_client.py (minimal, includes parse_start)
import os, json, datetime as dt
from dateutil import parser as dtparser
import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_info(json.load(open("token.json")), SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        open("token.json","w").write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def parse_start(time_string: str | None, time_zone: str = "Asia/Kolkata") -> dt.datetime:
    tz = pytz.timezone(time_zone)
    now = dt.datetime.now(tz)
    if not time_string:
        d = (now + dt.timedelta(days=1)).date()
        return tz.localize(dt.datetime(d.year, d.month, d.day, 11, 0))
    s = time_string.strip().lower()
    if "tomorrow" in s:
        try:
            t = dtparser.parse(s.replace("tomorrow","").strip(), fuzzy=True).time()
        except Exception:
            t = dt.time(11, 0)
        d = (now + dt.timedelta(days=1)).date()
        return tz.localize(dt.datetime.combine(d, t))
    if "today" in s:
        try:
            t = dtparser.parse(s.replace("today","").strip(), fuzzy=True).time()
        except Exception:
            n = (now + dt.timedelta(minutes=30)).replace(second=0, microsecond=0)
            t = dt.time(n.hour, n.minute)
        return tz.localize(dt.datetime.combine(now.date(), t))
    dtime = dtparser.parse(time_string)
    if dtime.tzinfo is None:
        dtime = tz.localize(dtime)
    else:
        dtime = dtime.astimezone(tz)
    return dtime
