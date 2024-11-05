from aiortc.contrib.media import MediaRelay
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from pydantic import BaseModel
from models.ImageStreamTrack import ImageStreamTrack

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


app = FastAPI()
clients = []

@app.websocket("/ws/signaling")
async def signaling_endpoint(websocket: WebSocket):
    print("Client connected")
    await websocket.accept()
    clients.append(websocket)

    print(f"Number of clients: {len(clients)}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            # Broadcast the data to other clients
            for client in clients:
                if client != websocket:
                    await client.send_text(data)
                    print(f"Sent data to client")
    except Exception as e:
        print(f"Client disconnected: {e}")
    finally:
        clients.remove(websocket)
