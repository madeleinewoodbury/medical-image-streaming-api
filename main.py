import json
import time

from aiortc.contrib.media import MediaRelay
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from pydantic import BaseModel

from models.ImageStreamTrack import ImageStreamTrack
app = FastAPI()
relay = MediaRelay()
peer_connections = {}

# Define the request model
class Offer(BaseModel):
    sdp: str
    type: str


@app.post("/offer")
async def offer(offer: Offer):
    # Create new peer connection
    pc = RTCPeerConnection()
    peer_connections[pc] = pc

    # Set up the data channel for metadata
    data_channel = pc.createDataChannel("metadataChannel")

    # Add image stream track to the peer connection
    image_track = ImageStreamTrack()
    pc.addTrack(image_track)
    print("Track added to peer connection")

    # Function to send metadata
    async def send_metadata():
        metadata = {"image_id": image_track.current_index, "timestamp": time.time()}
        await data_channel.send(json.dumps(metadata))

    # Set the remote description based on the offer
    rct_offer = RTCSessionDescription(sdp=offer.sdp, type=offer.type)
    await pc.setRemoteDescription(rct_offer)
    print("Remote description set")

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    print("Answer created")

    # Return the answer
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

