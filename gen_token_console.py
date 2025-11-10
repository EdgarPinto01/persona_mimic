from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

try:
    # Desktop OAuth supports loopback on ANY free port. `port=0` lets it auto-pick.
    creds = flow.run_local_server(host="127.0.0.1", port=8765, access_type="offline", prompt="consent")

except OSError:
    # Fallback if something blocks the local server
    creds = flow.run_console(prompt="consent")

open("token.json", "w").write(creds.to_json())
print("✅ token.json created")
