import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import asyncio
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.signaling import BYE
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Set your project ID, client ID, and client secret
PROJECT_ID = os.getenv("PROJECT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

print("Client ID:", CLIENT_ID)
print("Client Secret:", CLIENT_SECRET)
print("Project ID:", PROJECT_ID)

# Scopes for the OAuth2
SCOPES = ["https://www.googleapis.com/auth/sdm.service"]

def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds


async def create_offer_sdp():
    pc = RTCPeerConnection()

    pc.createDataChannel("dataChannel")
    
    # Create an SDP offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Return the SDP as a string
    return offer.sdp

def get_device_id(creds):
    url = f"https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices"
    response = requests.get(url, headers={"Authorization": f"Bearer {creds.token}"})
    devices = response.json().get("devices", [])
    for device in devices:
        if "sdm.devices.types.CAMERA" in device.get("type", ""):
            return device["name"]  # Return the device ID for the camera

def get_device_details(creds, device_id):
    url = f"https://smartdevicemanagement.googleapis.com/v1/{device_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {creds.token}"})
    
    # Print the response for debugging
    print("Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))
    
    return response.json()

def generate_webrtc_offer(creds, device_id):
    url = f"https://smartdevicemanagement.googleapis.com/v1/{device_id}:executeCommand"

    # Generate the SDP offer
    offer_sdp = asyncio.run(create_offer_sdp())
    print("Offer SDP:\n", offer_sdp)

    body = {
        "command": "sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream",
        "params": {
            "offerSdp": offer_sdp
        }
    }
    response = requests.post(url, headers={"Authorization": f"Bearer {creds.token}"}, json=body)
        # Print the response for debugging
    print("Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))
    return response.json()

async def start_webrtc_stream(offer):
    pc = RTCPeerConnection()

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            if message == BYE:
                await pc.close()

    @pc.on("track")
    def on_track(track):
        print(f"Track {track.kind} received")
        local_track = VideoStreamTrack()
        pc.addTrack(local_track)

    # Set the remote description and create an answer
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return pc.localDescription

def main():
    creds = get_credentials()
    device_id = get_device_id(creds)
    if device_id:
        device_details = get_device_details(creds, device_id)
        stream_info = generate_webrtc_offer(creds, device_id)
        offer = stream_info.get('results', {}).get('offer', {})
        if offer:
            print(f"WebRTC Offer: {offer}")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(start_webrtc_stream(offer))
        else:
            print("Failed to generate WebRTC offer.")
    else:
        print("No camera device found.")

if __name__ == "__main__":
    main()
