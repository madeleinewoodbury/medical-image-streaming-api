from aiortc.contrib.media import MediaRelay
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from pydantic import BaseModel
from models.ImageStreamTrack import ImageStreamTrack
from models.ImageProcessor import WatershedProcessor, SnakesProcessor
from routes import images
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router)

# Test route
@app.get("/")
async def root():
    return {"message": "Hello World"}

relay = MediaRelay()
peer_connections = {}

# Define the request model
class Offer(BaseModel):
    sdp: str
    type: str


# Add new endpoint
@app.post("/stop-stream")
async def stop_stream():
    # Clean up all existing connections
    for pc in list(peer_connections.values()):
        await cleanup_connection(pc)
    peer_connections.clear()
    print("All streams stopped")
    return {"message": "All streams stopped"}


async def cleanup_connection(pc):
    # Stop all tracks
    for sender in pc.getSenders():
        if sender.track:
            await sender.track.stop()

    # Close the connection
    await pc.close()

    # Remove from connections dict
    if pc in peer_connections:
        del peer_connections[pc]

## Process the offer and create an answer
async def handle_offer(offer, image_track):
    # Create new peer connection
    pc = RTCPeerConnection()
    peer_connections[pc] = pc

    # Add image stream track to the peer connection
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

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState in ["closed", "failed", "disconnected"]:
            await image_track.stop()
            # await cleanup_connection(pc)

    # Return the answer
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


@app.post("/snakes")
async def offer(
        offer: Offer,
        kernel_size: int = 3,
        x: int = 100,
        y: int = 100,
        radius: int = 50,
        image_delay: int = 1
):

    print("Snakes offer received")

    # Initialize the image processor for snakes
    image_processor = SnakesProcessor(kernel_size, x, y, radius)
    # Create image stream track
    image_track = ImageStreamTrack(image_processor, image_delay)

    return await handle_offer(offer, image_track)

@app.post("/watershed")
async def offer(
        offer: Offer,
        threshold_ratio: float = 0.5,
        kernel_size: int = 3,
        image_delay: int = 1
):

    # Initialize the image processor for watershed
    image_processor = WatershedProcessor(threshold_ratio, kernel_size)

    # Add image stream track to the peer connection
    image_track = ImageStreamTrack(image_processor, image_delay)

    return await handle_offer(offer, image_track)
