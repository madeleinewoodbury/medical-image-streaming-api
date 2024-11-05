import asyncio
import os

import cv2
import pydicom
from aiortc import VideoStreamTrack
import numpy as np
from av import VideoFrame


class ImageStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_index = 0
        self.frame_rate = 1

        self.load_images("images")

    def load_images(self, folder):
        # Reset the images list
        self.images = []

        # Load all images form the folder
        for filename in os.listdir(folder):
            # Check if image is a DICOM image
            if filename.endswith('.dcm'):
                # Read the DICOM image using PyDICOM
                dicom_data = pydicom.dcmread(os.path.join(folder, filename))
                image = dicom_data.pixel_array.astype(np.float32)
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                self.images.append(image)

        if len(self.images) == 0:
            raise ValueError("No images found in folder")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Get the current image
        current_image = self.images[self.current_index]

        video_frame = VideoFrame.from_ndarray(current_image, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        # Move to the next image
        self.current_index = (self.current_index + 1) % len(self.images)

        # Adjust delay based on frame rate
        await asyncio.sleep(5)

        return video_frame