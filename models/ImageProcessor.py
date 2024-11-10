import cv2
import numpy as np
from skimage.segmentation import active_contour
from abc import abstractmethod

class ImageProcessor:
    def __init__(self, kernel_size):
        self.kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.kernel_size = kernel_size
        self.image = None

    def segment_image(self, image):
        self.image = image

        self.apply_preprocessing()
        segmented_image = self.apply_segmentation()

        return segmented_image

    def apply_preprocessing(self):
        # Apply Gaussian Blur to smooth out noise
        self.image = cv2.GaussianBlur(self.image, (self.kernel_size, self.kernel_size), 0)
        # Apply opening (erosion followed by dilation) to remove small noise
        self.image = cv2.morphologyEx(self.image, cv2.MORPH_OPEN, self.kernel)
        # Apply closing (dilation followed by erosion) to close small holes
        self.image = cv2.morphologyEx(self.image, cv2.MORPH_CLOSE, self.kernel)

    @abstractmethod
    def apply_segmentation(self):
        pass


class WatershedProcessor(ImageProcessor):
    def __init__(self, threshold_ratio, kernel_size):
        super().__init__(kernel_size)
        self.threshold_ratio = threshold_ratio

    def apply_segmentation(self):
        # Apply Otsu's Thresholding
        _, binary = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Distance transform to compute markers
        distance = cv2.distanceTransform(binary, cv2.DIST_L2, 5)

        # Use a threshold ratio to define the marker region
        _, markers = cv2.threshold(distance, self.threshold_ratio * distance.max(), 255, 0)
        markers = np.uint8(markers)

        # Convert grayscale image to BGR for watershed processing
        bgr_image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)

        # Use Canny edge detection to improve marker initialization
        x, y = self.image.shape
        x = int(x / 2)
        y = int(y / 2)
        edges = cv2.Canny(self.image, x, y)

        # Apply connected components to create the markers
        _, markers = cv2.connectedComponents(edges)

        # Apply watershed algorithm
        cv2.watershed(bgr_image, markers)

        # Mark the boundaries of regions with red
        bgr_image[markers == -1] = [255, 0, 0]

        return bgr_image

class SnakesProcessor(ImageProcessor):
    def __init__(self, kernel_size, x, y, radius):
        super().__init__(kernel_size)
        self.x = x
        self.y = y
        self.radius = radius

    def apply_segmentation(self):
        # Manual initialization: User-defined initial points for the ellipse
        s = np.linspace(0, 2 * np.pi, 400)
        r = self.y + self.radius * np.sin(s)  # Adjusting for the y-coordinate
        c = self.x + self.radius * np.cos(s)  # Adjusting for the x-coordinate
        init = np.array([r, c]).T  # Initial snake points

        # Apply the active contour model
        alpha: float = 0.015
        beta: float = 10
        gamma: float = 0.001
        snake = active_contour(self.image, init, alpha=alpha, beta=beta, gamma=gamma)

        # Draw the snake on the image
        snake_image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        for point in snake:
            cv2.circle(snake_image, (int(point[1]), int(point[0])), 1, (0, 0, 255), -1)

        return snake_image






