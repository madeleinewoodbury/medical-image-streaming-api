import asyncio
import os
import cv2
import pydicom
from aiortc import VideoStreamTrack
import numpy as np
from av import VideoFrame
from routes.images import UPLOAD_FOLDER

class ImageStreamTrack(VideoStreamTrack):
    def __init__(self, imageProcessor, image_delay):
        super().__init__()
        self.images = []
        self.current_index = 0
        self.image_delay = image_delay
        self.processed_images = []
        self.image_processor = imageProcessor
        self._stopped = False

        self.load_images(UPLOAD_FOLDER)

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
                self.images.append(image)

        if len(self.images) == 0:
            raise ValueError("No images found in folder")

    async def recv(self):
        if self._stopped:
            return

        pts, time_base = await self.next_timestamp()
        if len(self.processed_images) < len(self.images):
            # Get the current image
            current_image = self.images[self.current_index]
            # Segment the image
            segmented_image = self.image_processor.segment_image(current_image)
            self.processed_images.append(segmented_image)
        else:
            segmented_image = self.processed_images[self.current_index]

        video_frame = VideoFrame.from_ndarray(segmented_image, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        # Move to the next image
        self.current_index = (self.current_index + 1) % len(self.images)

        # Adjust delay based on image delay
        await asyncio.sleep(self.image_delay)

        return video_frame

    async def stop(self):
        self._stopped = True
