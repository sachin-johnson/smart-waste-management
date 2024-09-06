import wrtc from 'wrtc';
import fetch from 'node-fetch';
import dotenv from 'dotenv';

// Define your project-specific variables
const PROJECT_ID = process.env.PROJECT_ID; // Replace with your Project ID
const DEVICE_ID = process.env.DEVICE_ID;
const ACCESS_TOKEN = process.env.ACCESS_TOKEN;

const { RTCPeerConnection } = wrtc;

// Initialize a new RTCPeerConnection
const pc = new RTCPeerConnection();

// Handle incoming media streams
pc.ontrack = (event) => {
    console.log('Received remote stream');
    const mediaStream = event.streams[0];
    // Here, you can process mediaStream, pass it to FFmpeg, or save it
};

// Function to fetch the SDP offer from Nest
async function getNestSdpOffer() {
    let offer = await pc.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true
    });

    await pc.setLocalDescription(offer);

    console.log('Generated SDP Offer:', offer.sdp);
    console.log('End of SDP Offer');

    // Check if the SDP contains the m=application line
    const hasApplication = offer.sdp.includes("m=application");

    // If m=application is missing, append it to the SDP
    if (!hasApplication) {
        const iceUfrag = offer.sdp.match(/a=ice-ufrag:([^\r\n]*)/)[1];
        const icePwd = offer.sdp.match(/a=ice-pwd:([^\r\n]*)/)[1];
        const fingerprint = offer.sdp.match(/a=fingerprint:([^\r\n]*)/)[1];

        // Append the m=application section to the SDP
        offer.sdp += `m=application 9 DTLS/SCTP 5000\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:${iceUfrag}\r\na=ice-pwd:${icePwd}\r\na=fingerprint:${fingerprint}\r\na=setup:actpass\r\na=mid:2\r\na=sctp-port:5000\r\na=max-message-size:262144\r\n`;
    }

    console.log('Modified SDP Offer:', offer.sdp);

    return offer.sdp;
}

// Function to send the SDP offer and get the SDP answer
async function fetchNestSdpAnswer(offerSdp) {
    const response = await fetch(`https://smartdevicemanagement.googleapis.com/v1/enterprises/${PROJECT_ID}/devices/${DEVICE_ID}:executeCommand`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${ACCESS_TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "command": "sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream",
            "params": {
                "offerSdp": offerSdp
            }
        })
    });

    const data = await response.json();

    if (!response.ok) {
        console.error('Response status:', response.status);
        console.error('Response headers:', response.headers.raw());
        console.error('Full server response:', data);
        throw new Error(`Error fetching SDP answer: ${data.error.message}`);
    }

    console.log('Received SDP Answer:', data.results.answerSdp);

    return data.results.answerSdp;
}

// Function to set up the WebRTC connection
async function setUpWebRtcConnection() {
    const offerSdp = await getNestSdpOffer();
    try {
        const answerSdp = await fetchNestSdpAnswer(offerSdp);
    } catch (error) {
        console.error('Failed to set up WebRTC connection:', error);
    }

    // Set the remote description with the SDP answer
    if (answerSdp) {
        await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });
        console.log('Remote description set successfully.');
    } else {
        console.error('No SDP answer received.');
    }

    console.log('Remote description set successfully.');
}

// Call the function to set up the WebRTC connection
setUpWebRtcConnection().catch(console.error);