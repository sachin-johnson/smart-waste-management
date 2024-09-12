import os
import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your project ID, client ID, and client secret
PROJECT_ID = os.getenv("PROJECT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Scopes for the OAuth2
SCOPES = ["https://www.googleapis.com/auth/sdm.service"]

def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds

def get_device_id(creds):
    url = f"https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices"
    response = requests.get(url, headers={"Authorization": f"Bearer {creds.token}"})
    devices = response.json().get("devices", [])
    for device in devices:
        if "sdm.devices.types.CAMERA" in device.get("type", ""):
            return device["name"]  # Return the device ID for the camera
    return None

def get_latest_event_id(creds, device_id):
    url = f"https://smartdevicemanagement.googleapis.com/v1/{device_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {creds.token}"})
    traits = response.json().get("traits", {})
    
    # Check for motion events first
    motion_events = traits.get("sdm.devices.traits.CameraMotion", {}).get("events", {})
    if motion_events:
        latest_event = max(motion_events.keys(), key=lambda k: motion_events[k]['timestamp'])
        return motion_events[latest_event]['eventId']

    # If no motion events, you might want to check for person detection events
    person_events = traits.get("sdm.devices.traits.CameraPerson", {}).get("events", {})
    if person_events:
        latest_event = max(person_events.keys(), key=lambda k: person_events[k]['timestamp'])
        return person_events[latest_event]['eventId']
    
    print("No events found.")
    return None

def generate_clip_preview(creds, device_id, event_id):
    url = f"https://smartdevicemanagement.googleapis.com/v1/{device_id}:executeCommand"
    body = {
        "command": "sdm.devices.commands.CameraClipPreview.GenerateClipPreview",
        "params": {
            "eventId": event_id
        }
    }

    response = requests.post(url, headers={"Authorization": f"Bearer {creds.token}"}, json=body)
    if response.status_code == 200:
        return response.json().get("results", {}).get("previewClipUrl")
    else:
        print(f"Failed to generate clip preview: {response.status_code}, {response.text}")
        return None

def download_clip(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Video clip saved as {filename}")
    else:
        print(f"Failed to download video clip: {response.status_code}, {response.text}")

def main():
    creds = get_credentials()
    device_id = get_device_id(creds)
    if device_id:
        print("Retrieving the latest event ID...")
        event_id = get_latest_event_id(creds, device_id)

        if event_id:
            print(f"Generating clip preview for event ID: {event_id}")
            clip_url = generate_clip_preview(creds, device_id, event_id)

            if clip_url:
                print("Downloading video clip...")
                download_clip(clip_url, "latest_event_clip.mp4")
            else:
                print("Failed to retrieve clip URL.")
        else:
            print("No recent events detected.")
    else:
        print("No camera device found.")

if __name__ == "__main__":
    main()
