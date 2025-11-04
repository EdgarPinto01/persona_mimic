from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(
    host="127.0.0.1",
    port=8080,
    access_type="offline",
    prompt="consent",
    open_browser=True
)
open("token.json", "w").write(creds.to_json())
print("✅ token.json created")
