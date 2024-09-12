import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import asyncio
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription
from aiortc.contrib.signaling import BYE
import os
from dotenv import load_dotenv
import av

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

class DummyAudioTrack(MediaStreamTrack):
    kind = "audio"

    async def recv(self):
        frame = av.AudioFrame(format="s16", layout="mono", samples=960)
        frame.pts = self.time_base * 960
        frame.time_base = self.time_base
        return frame

class DummyVideoTrack(MediaStreamTrack):
    kind = "video"

    async def recv(self):
        frame = av.VideoFrame(width=640, height=480)
        frame.pts = self.time_base * 3000
        frame.time_base = self.time_base
        return frame

async def create_offer_sdp():
    pc = RTCPeerConnection()

    @pc.on("signalingstatechange")
    async def on_signalingstatechange():
        print(f"Signaling state changed: {pc.signalingState}")

    # Add dummy audio and video tracks
    audio_track = DummyAudioTrack()
    video_track = DummyVideoTrack()
    pc.addTrack(audio_track)
    pc.addTrack(video_track)

    # Add a data channel
    pc.createDataChannel("dataChannel")
    
    # Create an SDP offer
    offer = await pc.createOffer()
    print("Created SDP offer")
    await pc.setLocalDescription(offer)
    print("Set local description with SDP offer")

    # Modify the SDP to set the audio track to recvonly
    sdp = pc.localDescription.sdp
    sdp = sdp.replace("a=sendrecv", "a=recvonly", 1)

    # Return the SDP as a string
    return sdp

def get_device_id(creds):
    url = f"https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices"
    response = requests.get(url, headers={"Authorization": f"Bearer {creds.token}"})
    devices = response.json().get("devices", [])
    for device in devices:
        if "sdm.devices.types.CAMERA" in device.get("type", ""):
            return device["name"]  # Return the device ID for the camera

def generate_webrtc_offer(creds, device_id):
    url = f"https://smartdevicemanagement.googleapis.com/v1/{device_id}:executeCommand"

    # Generate the SDP offer
    offer_sdp = asyncio.run(create_offer_sdp())

    body = {
        "command": "sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream",
        "params": {
            "offerSdp": offer_sdp
        }
    }
    response = requests.post(url, headers={"Authorization": f"Bearer {creds.token}"}, json=body)
    return response.json()

async def start_webrtc_stream(answer_sdp):
    pc = RTCPeerConnection()

    @pc.on("signalingstatechange")
    async def on_signalingstatechange():
        print(f"Signaling state changed: {pc.signalingState}")

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state changed: {pc.iceConnectionState}")
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
        if track.kind == "video":
            local_track = DummyVideoTrack()  # Assuming DummyVideoTrack is correctly implemented
            pc.addTrack(local_track)
        elif track.kind == "audio":
            # If you do not want to handle audio, you can simply not add any audio tracks
            print("Ignoring audio track")

    # Clean the answer SDP (if necessary)
    cleaned_sdp = clean_sdp(answer_sdp)

    # Set the remote description using the cleaned answer SDP
    answer = RTCSessionDescription(sdp=cleaned_sdp, type="answer")

    try:
        if pc.signalingState == "have-local-offer":
            await pc.setRemoteDescription(answer)
            print("Set remote description with SDP answer")
        else:
            print(f"Cannot set remote description in signaling state: {pc.signalingState}")
    except ValueError as e:
        print(f"Error setting remote description: {e}")
        raise

    # Keep the connection alive until manually closed or a timeout occurs
    try:
        await asyncio.sleep(10)  # You can increase this to keep the stream alive longer
    except asyncio.CancelledError:
        pass  # Handle the case where the sleep is cancelled

    return pc.localDescription

def clean_sdp(sdp):
    """ Clean or adjust the SDP to be compatible with aiortc """
    lines = sdp.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.startswith("a=candidate:"):
            parts = line.split()
            if len(parts) > 2 and not parts[2].isdigit():
                # Insert parts[1] as the component ID if parts[2] is not an integer
                parts.insert(2, parts[1])
                line = " ".join(parts)
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def main():
    creds = get_credentials()
    device_id = get_device_id(creds)
    if device_id:
        stream_info = generate_webrtc_offer(creds, device_id)

        # Retrieve the answer SDP from the API response
        answer_sdp = stream_info.get('results', {}).get('answerSdp', {})
        if answer_sdp:
            asyncio.run(start_webrtc_stream(answer_sdp))
        else:
            print("Failed to receive WebRTC answer.")
    else:
        print("No camera device found.")

if __name__ == "__main__":
    main()