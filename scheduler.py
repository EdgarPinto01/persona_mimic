# scheduler.py
import datetime as dt
import pytz, uuid
from calendar_client import get_calendar_service

def find_available_slots(
    time_zone="Asia/Kolkata",
    days_ahead=7,
    daily_start="10:00",
    daily_end="18:00",
    slot_minutes=30,
    max_slots=6,
):
    svc = get_calendar_service()
    tz = pytz.timezone(time_zone)
    now = dt.datetime.now(tz)
    time_min = now.isoformat()
    time_max = (now + dt.timedelta(days=days_ahead)).isoformat()

    fb = svc.freebusy().query(
        body={"timeMin": time_min, "timeMax": time_max, "timeZone": time_zone, "items": [{"id": "primary"}]}
    ).execute()

    busy = []
    for b in fb["calendars"]["primary"].get("busy", []):
        # Google returns RFC3339; dt.fromisoformat handles offset
        busy.append((dt.datetime.fromisoformat(b["start"]), dt.datetime.fromisoformat(b["end"])))

    def day_window(d):
        h1, m1 = map(int, daily_start.split(":"))
        h2, m2 = map(int, daily_end.split(":"))
        return tz.localize(dt.datetime(d.year, d.month, d.day, h1, m1)), tz.localize(dt.datetime(d.year, d.month, d.day, h2, m2))

    def overlaps(a_start, a_end):
        for b_start, b_end in busy:
            if a_start < b_end and b_start < a_end:
                return True
        return False

    slots = []
    d = now
    end_date = (now + dt.timedelta(days=days_ahead)).date()
    while len(slots) < max_slots and d.date() <= end_date:
        if d.weekday() < 5:  # Mon–Fri
            start_day, end_day = day_window(d)
            t = max(d, start_day)
            # snap to next slot boundary
            minute_block = (t.minute // slot_minutes + (1 if t.minute % slot_minutes else 0)) * slot_minutes
            t = t.replace(minute=minute_block if minute_block < 60 else 0, hour=t.hour if minute_block < 60 else t.hour + 1, second=0, microsecond=0)
            while t + dt.timedelta(minutes=slot_minutes) <= end_day and len(slots) < max_slots:
                s, e = t, t + dt.timedelta(minutes=slot_minutes)
                if not overlaps(s, e):
                    slots.append({"start": s.isoformat(), "end": e.isoformat(), "tz": time_zone})
                t = e
        d = (d + dt.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    return slots

def create_meet_event(guest_email, guest_name, start_iso, duration_minutes=30, time_zone="Asia/Kolkata", notes=""):
    svc = get_calendar_service()
    start_dt = dt.datetime.fromisoformat(start_iso)
    if start_dt.tzinfo is None:
        start_dt = pytz.timezone(time_zone).localize(start_dt)
    end_dt = start_dt + dt.timedelta(minutes=duration_minutes)

    event = {
        "summary": "Intro call with Edgar Pinto",
        "description": notes or "Introductory conversation",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": time_zone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": time_zone},
        "attendees": [{"email": guest_email, "displayName": guest_name or guest_email}],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4())[:30],
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {"useDefault": True},
    }

    created = svc.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,
        sendUpdates="all",
    ).execute()

    meet_link = created.get("hangoutLink") or (created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri"))
    return {
        "status": "ok",
        "event_id": created["id"],
        "html_link": created.get("htmlLink"),
        "meet_link": meet_link,
        "start": created["start"]["dateTime"],
        "end": created["end"]["dateTime"],
    }
